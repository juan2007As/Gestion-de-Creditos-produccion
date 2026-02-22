"""
CRÍTICA #7: TRANSACTION INTEGRITY & ERROR HANDLING
Gestión robusta de transacciones para operaciones financieras críticas
"""

from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from functools import wraps
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)


class TransactionError(Exception):
    """Error base para errores transaccionales"""
    pass


class PaymentError(TransactionError):
    """Error específico de operaciones de pago"""
    pass


class CuotaError(TransactionError):
    """Error específico de operaciones de cuota"""
    pass


def transactional_payment(func):
    """
    Decorador para envolver operaciones de pago en transacciones atómicas
    
    Guarantees:
    - Pago creado OR nada creado (atomicidad)
    - Cuota actualizada (estado, montos) OR nada actualizado
    - Préstamo actualizado (estado) OR nada actualizado
    - Rollback automático en cualquier error
    
    Ejemplo:
        @transactional_payment
        def registrar_pago(request, cuota_id):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                return func(*args, **kwargs)
        except (ValidationError, PaymentError, CuotaError) as e:
            # Errores esperados - log + return
            logger.warning(f"Error en pago: {str(e)}")
            raise
        except IntegrityError as e:
            # Error de integridad BD (constraints, FK, etc)
            logger.error(f"Integridad de BD: {str(e)}")
            raise PaymentError(f"Error de integridad en BD: {str(e)}")
        except Exception as e:
            # Error inesperado
            logger.error(f"Error inesperado en pago: {str(e)}", exc_info=True)
            raise PaymentError(f"Error interno: {str(e)}")
    
    return wrapper


def validate_payment_amount(monto, cuota_pendiente):
    """Valida que el monto de pago sea válido"""
    
    # Validar que no sea None
    if monto is None:
        raise PaymentError("Monto no puede ser nulo")
    
    # Validar que sea convertible a Decimal
    try:
        monto_decimal = Decimal(str(monto))
    except (InvalidOperation, TypeError, ValueError):
        raise PaymentError(f"Monto inválido: {monto}")
    
    # Validar que sea positivo
    if monto_decimal <= 0:
        raise PaymentError("Monto debe ser positivo")
    
    # Validar que no exceda lo pendiente
    if monto_decimal > cuota_pendiente:
        raise PaymentError(f"Monto ${monto_decimal} excede lo pendiente ${cuota_pendiente}")
    
    return monto_decimal


def registrar_pago_atomico(cuota, monto_pago, usuario, notas="", referencia=""):
    """
    Registra un pago de forma atómica con garantías ACID
    
    Args:
        cuota: Instancia de Cuota
        monto_pago: Monto a pagar (Decimal)
        usuario: Usuario que registra el pago
        notas: Notas adicionales
        referencia: Referencia del pago
    
    Returns:
        Pago creado
    
    Raises:
        PaymentError: Si hay error en el pago
        CuotaError: Si hay error en cuota
    """
    
    from mi_app.models import Pago
    
    with transaction.atomic():
        # 1. Lock de la cuota para evitar race conditions
        cuota = cuota.__class__.objects.select_for_update().get(pk=cuota.pk)
        
        # 2. Validar monto
        monto_decimal = validate_payment_amount(
            monto_pago,
            cuota.monto_pendiente
        )
        
        # 3. Validar que la cuota pueda recibir pago
        if cuota.pagado:
            raise CuotaError("Cuota ya está completamente pagada")
        
        if cuota.prestamo.estado not in ['ACTIVO', 'VENCIDA', 'EN_MORA']:
            raise CuotaError(f"Cuota no puede recibir pago (Prestamo estado: {cuota.prestamo.estado})")
        
        # 4. Crear pago (transacción comienza aquí)
        try:
            pago = Pago.objects.create(
                cuota=cuota,
                monto_pagado=monto_decimal,
                monto_principal=monto_decimal,  # Simplificado - en prod sería más complejo
                usuario_registra=usuario.username if hasattr(usuario, 'username') else str(usuario),
                notas=notas,
                referencia=referencia
            )
        except Exception as e:
            raise PaymentError(f"Error creando pago: {str(e)}")
        
        # 5. Actualizar cuota
        try:
            cuota.monto_pendiente = max(cuota.monto_pendiente - monto_decimal, Decimal('0'))
            cuota.monto_pagado_principal += monto_decimal
            
            # Si cuota completamente pagada
            if cuota.monto_pendiente <= 0:
                cuota.pagado = True
                from django.utils import timezone
                cuota.fecha_pago_real = timezone.now().date()
            
            cuota.actualizar_estado()
            cuota.save()
        except Exception as e:
            raise CuotaError(f"Error actualizando cuota: {str(e)}")
        
        # 6. Actualizar préstamo si todas las cuotas están pagadas
        try:
            prestamo = cuota.prestamo
            if prestamo.cuotas.filter(pagado=False).count() == 0:
                prestamo.estado = 'COMPLETADO'
                prestamo.save()
        except Exception as e:
            raise PaymentError(f"Error actualizando préstamo: {str(e)}")
        
        # 7. Auditoría (no debe fallar transacción si auditoría falla)
        try:
            from mi_app.models import AuditLog
            AuditLog.objects.create(
                usuario=usuario,
                accion='CREATE',
                modelo='Pago',
                objeto_id=pago.id,
                objeto_representacion=f"Pago ${monto_decimal} Cuota #{cuota.numero_cuota}",
                descripcion=f"Pago registrado: ${monto_decimal}",
            )
        except Exception as e:
            logger.warning(f"Error en auditoría de pago: {str(e)}")
        
        logger.info(f"Pago registrado exitosamente: ${monto_decimal} en Cuota #{cuota.numero_cuota}")
        
        return pago


def actualizar_estado_cuota_atomica(cuota):
    """
    Actualiza el estado de una cuota de forma atómica
    
    Protege contra race conditions con select_for_update()
    """
    
    with transaction.atomic():
        # Lock para evitar race conditions
        cuota = cuota.__class__.objects.select_for_update().get(pk=cuota.pk)
        
        # Verificar si está pagada
        if cuota.monto_pendiente <= 0 and cuota.monto_pendiente_interes <= 0:
            cuota.pagado = True
            from django.utils import timezone
            if not cuota.fecha_pago_real:
                cuota.fecha_pago_real = timezone.now().date()
        
        cuota.actualizar_estado()
        cuota.save()
        
        return cuota


def actualizar_estado_prestamo_atomica(prestamo):
    """
    Actualiza el estado de un préstamo de forma atómica
    
    Verifica si todas las cuotas están pagadas para marcar como COMPLETADO
    """
    
    with transaction.atomic():
        # Lock del préstamo
        prestamo = prestamo.__class__.objects.select_for_update().get(pk=prestamo.pk)
        
        # Contar cuotas no pagadas
        cuotas_pendientes = prestamo.cuotas.filter(pagado=False).count()
        
        if cuotas_pendientes == 0:
            prestamo.estado = 'COMPLETADO'
            prestamo.save()
            logger.info(f"Préstamo #{prestamo.id} marcado como COMPLETADO")
        
        return prestamo


def eliminar_pago_atomico(pago, usuario=None):
    """
    Elimina un pago y revierte los cambios en cuota (rollback de pago)
    
    Realiza el reverso de registrar_pago_atomico
    """
    
    with transaction.atomic():
        cuota = pago.cuota.__class__.objects.select_for_update().get(pk=pago.cuota.pk)
        
        # 1. Reversar cambios en cuota
        if pago.monto_pagado:
            cuota.monto_pendiente += pago.monto_pagado
            cuota.monto_pagado_principal -= min(pago.monto_principal or Decimal('0'), cuota.monto_pagado_principal)
            cuota.monto_pagado_interes -= min(pago.monto_interes or Decimal('0'), cuota.monto_pagado_interes)
            cuota.monto_pagado_mora -= min(pago.monto_mora or Decimal('0'), cuota.monto_pagado_mora)
            
            # Resetear pagado si es necesario
            if cuota.pagado:
                cuota.pagado = False
                cuota.fecha_pago_real = None
            
            cuota.actualizar_estado()
            cuota.save()
        
        # 2. Eliminar pago (auditoría manejada por signals.py post_delete)
        pago.delete()
        
        logger.info(f"Pago revertido exitosamente de Cuota #{cuota.numero_cuota}")
        
        return cuota


# ===============================================================================
# DECORATOR PARA VISTAS
# ===============================================================================

def atomic_payment_view(func):
    """
    Decorador para views que manejan pagos
    Wrappea todo en una transacción y maneja errores
    
    Uso:
        @atomic_payment_view
        @login_required
        def registrar_pago_view(request):
            ...
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            with transaction.atomic():
                return func(request, *args, **kwargs)
        except PaymentError as e:
            from django.contrib import messages
            messages.error(request, f"Error en pago: {str(e)}")
            logger.warning(f"PaymentError en view {func.__name__}: {str(e)}")
            
            # Retornar a view anterior
            from django.shortcuts import redirect
            return redirect(request.META.get('HTTP_REFERER', 'inicio'))
        
        except CuotaError as e:
            from django.contrib import messages
            messages.error(request, f"Error en cuota: {str(e)}")
            logger.warning(f"CuotaError en view {func.__name__}: {str(e)}")
            
            from django.shortcuts import redirect
            return redirect(request.META.get('HTTP_REFERER', 'inicio'))
        
        except Exception as e:
            from django.contrib import messages
            messages.error(request, "Error inesperado al procesar pago")
            logger.error(f"Error inesperado en view {func.__name__}: {str(e)}", exc_info=True)
            
            from django.shortcuts import redirect
            return redirect(request.META.get('HTTP_REFERER', 'inicio'))
    
    return wrapper

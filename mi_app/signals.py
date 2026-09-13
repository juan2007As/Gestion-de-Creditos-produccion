"""
CRÍTICA #6: AUDIT SIGNALS
Captura automáticamente TODOS los cambios en modelos principales
"""

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from mi_app.models import (
    Cliente, Prestamo, Cuota, Pago, ListaNegra, Configuracion, AuditLog
)


def get_client_ip(request):
    """Obtiene la IP del cliente de la request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_object_representation(obj):
    """Retorna una representación legible del objeto"""
    if isinstance(obj, Cliente):
        return f"Cliente: {obj.nombre} ({obj.cedula})"
    elif isinstance(obj, Prestamo):
        return f"Préstamo #{obj.id} - {obj.cliente.nombre} (${obj.monto_total})"
    elif isinstance(obj, Cuota):
        return f"Cuota #{obj.numero_cuota} Préstamo #{obj.prestamo.id}"
    elif isinstance(obj, Pago):
        return f"Pago ${obj.monto_pagado} Cuota #{obj.cuota.numero_cuota}"
    elif isinstance(obj, ListaNegra):
        return f"Lista Negra: {obj.cliente.nombre} ({obj.razon})"
    elif isinstance(obj, Configuracion):
        return f"Configuración #{obj.id}"
    elif isinstance(obj, User):
        return f"Usuario: {obj.username}"
    else:
        return str(obj)


def get_changed_fields(before, after, instance):
    """
    Compara before/after y retorna los campos que cambiaron
    """
    cambios = {}
    
    # Obtener campos del modelo
    for field in instance._meta.get_fields():
        if field.name.startswith('_'):
            continue
        
        try:
            valor_antes = getattr(before, field.name, None) if before else None
            valor_despues = getattr(after, field.name, None) if after else None
            
            # Convertir a string para comparación
            valor_antes_str = str(valor_antes) if valor_antes is not None else ""
            valor_despues_str = str(valor_despues) if valor_despues is not None else ""
            
            if valor_antes_str != valor_despues_str:
                cambios[field.name] = [valor_antes_str, valor_despues_str]
        except:
            pass
    
    return cambios if cambios else None


# =============================================================================
# SIGNALS - CLIENTE
# =============================================================================

_cliente_original = {}

@receiver(pre_save, sender=Cliente)
def capturar_cliente_pre_save(sender, instance, **kwargs):
    """Captura estado original antes de guardar"""
    if instance.pk:
        try:
            _cliente_original[instance.pk] = Cliente.objects.get(pk=instance.pk)
        except:
            _cliente_original[instance.pk] = None


@receiver(post_delete, sender=Cliente)
def auditar_cliente_delete(sender, instance, **kwargs):
    """Registra eliminación de cliente"""
    # Nota: En un delete no tenemos request, usar contexto global si es necesario
    AuditLog.objects.create(
        usuario=None,  # No tenemos usuario en signal de delete
        accion='DELETE',
        modelo='Cliente',
        objeto_id=instance.id,
        objeto_representacion=get_object_representation(instance),
        cambios=None,
        descripcion=f"Eliminado cliente: {instance.nombre}"
    )


# =============================================================================
# SIGNALS - PRESTAMO
# =============================================================================

_prestamo_original = {}

@receiver(pre_save, sender=Prestamo)
def capturar_prestamo_pre_save(sender, instance, **kwargs):
    """Captura estado original antes de guardar"""
    if instance.pk:
        try:
            _prestamo_original[instance.pk] = Prestamo.objects.get(pk=instance.pk)
        except:
            _prestamo_original[instance.pk] = None


@receiver(post_delete, sender=Prestamo)
def auditar_prestamo_delete(sender, instance, **kwargs):
    """Registra eliminación de préstamo"""
    AuditLog.objects.create(
        usuario=None,
        accion='DELETE',
        modelo='Prestamo',
        objeto_id=instance.id,
        objeto_representacion=get_object_representation(instance),
        cambios=None,
        descripcion=f"Eliminado préstamo #{instance.id} de {instance.cliente.nombre}"
    )


# =============================================================================
# SIGNALS - CUOTA
# =============================================================================

_cuota_original = {}

@receiver(pre_save, sender=Cuota)
def capturar_cuota_pre_save(sender, instance, **kwargs):
    """Captura estado original antes de guardar"""
    if instance.pk:
        try:
            _cuota_original[instance.pk] = Cuota.objects.get(pk=instance.pk)
        except:
            _cuota_original[instance.pk] = None


@receiver(post_delete, sender=Cuota)
def auditar_cuota_delete(sender, instance, **kwargs):
    """Registra eliminación de cuota"""
    AuditLog.objects.create(
        usuario=None,
        accion='DELETE',
        modelo='Cuota',
        objeto_id=instance.id,
        objeto_representacion=get_object_representation(instance),
        cambios=None,
        descripcion=f"Eliminada cuota #{instance.numero_cuota} del préstamo #{instance.prestamo.id}"
    )


# =============================================================================
# SIGNALS - PAGO
# =============================================================================

_pago_original = {}

@receiver(pre_save, sender=Pago)
def capturar_pago_pre_save(sender, instance, **kwargs):
    """Captura estado original antes de guardar"""
    if instance.pk:
        try:
            _pago_original[instance.pk] = Pago.objects.get(pk=instance.pk)
        except:
            _pago_original[instance.pk] = None


@receiver(post_delete, sender=Pago)
def auditar_pago_delete(sender, instance, **kwargs):
    """Registra eliminación de pago"""
    AuditLog.objects.create(
        usuario=None,
        accion='DELETE',
        modelo='Pago',
        objeto_id=instance.id,
        objeto_representacion=get_object_representation(instance),
        cambios=None,
        descripcion=f"Eliminado pago de ${instance.monto_pagado}"
    )


# =============================================================================
# SIGNALS - LISTA NEGRA
# =============================================================================

_listaen_negra_original = {}

@receiver(pre_save, sender=ListaNegra)
def capturar_listanegra_pre_save(sender, instance, **kwargs):
    """Captura estado original antes de guardar"""
    if instance.pk:
        try:
            _listaen_negra_original[instance.pk] = ListaNegra.objects.get(pk=instance.pk)
        except:
            _listaen_negra_original[instance.pk] = None


@receiver(post_delete, sender=ListaNegra)
def auditar_listanegra_delete(sender, instance, **kwargs):
    """Registra eliminación de lista negra"""
    AuditLog.objects.create(
        usuario=None,
        accion='DELETE',
        modelo='ListaNegra',
        objeto_id=instance.id,
        objeto_representacion=get_object_representation(instance),
        cambios=None,
        descripcion=f"Removido {instance.cliente.nombre} de lista negra"
    )

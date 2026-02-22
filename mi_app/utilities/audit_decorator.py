"""
CRÍTICA #6: AUDIT DECORATOR
Decorador para capturar acciones en las vistas
"""

from functools import wraps
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import json
import traceback

from mi_app.models import AuditLog, Cliente, Prestamo, Cuota, Pago, ListaNegra


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def get_object_representation(obj):
    """Retorna una representación legible del objeto"""
    if obj is None:
        return "N/A"
    
    if isinstance(obj, Cliente):
        return f"Cliente: {obj.nombre} ({obj.cedula})"
    elif isinstance(obj, Prestamo):
        return f"Préstamo #{obj.id} - {obj.cliente.nombre} (${obj.monto_total})"
    elif isinstance(obj, Cuota):
        return f"Cuota #{obj.numero_cuota} Préstamo #{obj.prestamo.id}"
    elif isinstance(obj, Pago):
        return f"Pago ${obj.monto} Cuota #{obj.cuota.numero_cuota}"
    elif isinstance(obj, ListaNegra):
        return f"Lista Negra: {obj.cliente.nombre} ({obj.razon})"
    else:
        return str(obj)


def audit_view(accion, modelo=None, objeto_getter=None, descripcion_template=None):
    """
    Decorador para auditar acciones en vistas
    
    Args:
        accion (str): CREATE, UPDATE, DELETE, RESTORE, etc.
        modelo (str): Nombre del modelo (Cliente, Prestamo, etc.)
        objeto_getter (callable): Función que retorna el objeto afectado
        descripcion_template (str): Template para la descripción
    
    Ejemplo:
        @audit_view('CREATE', 'Prestamo')
        def crear_prestamo(request):
            ...
        
        @audit_view('UPDATE', modelo='Prestamo', 
                   objeto_getter=lambda r: Prestamo.objects.get(id=r.POST.get('prestamo_id')))
        def editar_prestamo(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Ejecutar la vista
                response = view_func(request, *args, **kwargs)
                
                # Intentar obtener el objeto afectado
                objeto = None
                objeto_id = None
                
                if objeto_getter:
                    try:
                        objeto = objeto_getter(request, *args, **kwargs)
                    except:
                        objeto = None
                
                # Si la vista retorna un objeto en contexto
                if hasattr(response, 'context_data') and 'object' in response.context_data:
                    objeto = response.context_data['object']
                
                # Obtener representación del objeto
                objeto_repr = get_object_representation(objeto)
                objeto_id = getattr(objeto, 'id', None)
                
                # Construir descripción
                if descripcion_template:
                    descripcion = descripcion_template.format(
                        objeto=objeto_repr,
                        usuario=request.user.username if request.user.is_authenticated else "Anónimo"
                    )
                else:
                    usuario = request.user.username if request.user.is_authenticated else "Anónimo"
                    descripcion = f"{accion}: {objeto_repr} realizado por {usuario}"
                
                # Registrar en auditoría
                try:
                    AuditLog.objects.create(
                        usuario=request.user if request.user.is_authenticated else None,
                        accion=accion,
                        modelo=modelo or "Desconocido",
                        objeto_id=objeto_id or 0,
                        objeto_representacion=objeto_repr,
                        cambios=None,
                        ip_address=get_client_ip(request),
                        descripcion=descripcion
                    )
                except Exception as e:
                    print(f"⚠️ Error registrando auditoría: {e}")
                    traceback.print_exc()
                
                return response
            
            except Exception as e:
                # Si hay excepción, registrarla pero dejar que Django la maneje
                print(f"⚠️ Error en vista auditada {view_func.__name__}: {e}")
                traceback.print_exc()
                raise
        
        return wrapper
    
    return decorator


def audit_action(accion, modelo, objeto_repr, descripcion, usuario, ip_address):
    """
    Función auxiliar para registrar una acción manualmente
    Útil cuando no se puede usar decorador
    
    Ejemplo:
        from mi_app.audit_decorator import audit_action
        
        audit_action(
            accion='PAGO',
            modelo='Pago',
            objeto_repr=f"Pago ${pago.monto}",
            descripcion=f"Pagada cuota #{cuota.numero_cuota}",
            usuario=request.user,
            ip_address=get_client_ip(request)
        )
    """
    try:
        AuditLog.objects.create(
            usuario=usuario if usuario.is_authenticated else None,
            accion=accion,
            modelo=modelo,
            objeto_id=0,
            objeto_representacion=objeto_repr,
            cambios=None,
            ip_address=ip_address,
            descripcion=descripcion
        )
    except Exception as e:
        print(f"⚠️ Error registrando auditoría: {e}")
        traceback.print_exc()

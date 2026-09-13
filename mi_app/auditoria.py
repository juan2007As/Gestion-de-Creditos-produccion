"""
Decorador para registrar cambios en la auditoría del sistema.
Permite capturar automáticamente QUIÉN cambió QUÉ, CUÁNDO y POR QUÉ.
"""

from functools import wraps
from django.utils import timezone
from mi_app.models import HistorioCambios
import json


def registrar_cambio(accion='EDITAR', modelo=None):
    """
    Decorador para registrar cambios automáticamente en auditoría.
    
    Uso:
        @registrar_cambio(accion='EDITAR', modelo='Cliente')
        def editar_cliente(request, cliente_id):
            # ... código ...
    
    Args:
        accion: Tipo de acción (CREAR, EDITAR, ELIMINAR, etc.)
        modelo: Nombre del modelo afectado (ej: 'Cliente', 'Préstamo')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Ejecutar la vista
            response = view_func(request, *args, **kwargs)
            
            # Registrar en auditoría si el usuario está autenticado
            if request.user.is_authenticated:
                # Intentar obtener datos de contexto (pueden ser agregados a request)
                contexto_auditoria = getattr(request, '_auditoria_contexto', {})
                
                HistorioCambios.objects.create(
                    usuario=request.user,
                    accion=accion,
                    modelo=modelo or view_func.__name__,
                    objeto_id=contexto_auditoria.get('objeto_id', 0),
                    objeto_str=contexto_auditoria.get('objeto_str', ''),
                    campo_modificado=contexto_auditoria.get('campo', ''),
                    valor_anterior=contexto_auditoria.get('valor_anterior', ''),
                    valor_nuevo=contexto_auditoria.get('valor_nuevo', ''),
                    razon=contexto_auditoria.get('razon', ''),
                    ip_address=get_client_ip(request),
                    notas=contexto_auditoria.get('notas', ''),
                )
            
            return response
        
        return wrapper
    
    return decorator


def registrar_cambio_manual(usuario, accion, modelo, objeto_id, objeto_str, 
                           campo='', valor_anterior='', valor_nuevo='', 
                           razon='', ip_address=None, notas=''):
    """
    Registra un cambio manualmente en auditoría.
    Útil para operaciones no vinculadas a vistas.
    
    Args:
        usuario: Usuario que hizo el cambio
        accion: Tipo de acción
        modelo: Nombre del modelo
        objeto_id: ID del objeto modificado
        objeto_str: Representación del objeto
        campo: Campo modificado
        valor_anterior: Valor antes
        valor_nuevo: Valor después
        razon: Justificación
        ip_address: IP del usuario
        notas: Notas adicionales
    
    Returns:
        HistorioCambios: El registro creado
    """
    return HistorioCambios.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        objeto_str=objeto_str,
        campo_modificado=campo,
        valor_anterior=str(valor_anterior),
        valor_nuevo=str(valor_nuevo),
        razon=razon,
        ip_address=ip_address,
        notas=notas,
    )


def registrar_cambios_multiples(usuario, accion, modelo, objeto_id, objeto_str, 
                               cambios_dict, razon='', ip_address=None):
    """
    Registra múltiples cambios para el mismo objeto.
    
    Args:
        usuario: Usuario que hizo los cambios
        accion: Tipo de acción
        modelo: Nombre del modelo
        objeto_id: ID del objeto
        objeto_str: Representación del objeto
        cambios_dict: Dict con cambios {'campo': (valor_anterior, valor_nuevo), ...}
        razon: Justificación
        ip_address: IP del usuario
    
    Returns:
        list: Lista de registros HistorioCambios creados
    """
    registros = []
    
    for campo, (valor_antes, valor_despues) in cambios_dict.items():
        if valor_antes != valor_despues:  # Solo registrar si realmente cambió
            registro = registrar_cambio_manual(
                usuario=usuario,
                accion=accion,
                modelo=modelo,
                objeto_id=objeto_id,
                objeto_str=objeto_str,
                campo=campo,
                valor_anterior=valor_antes,
                valor_nuevo=valor_despues,
                razon=razon,
                ip_address=ip_address,
            )
            registros.append(registro)
    
    return registros


def get_client_ip(request):
    """
    Obtiene la IP del cliente desde la solicitud HTTP.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_auditoria_contexto(request, **kwargs):
    """
    Establece contexto de auditoría en la request.
    Usado junto con el decorador @registrar_cambio.
    
    Uso:
        set_auditoria_contexto(request,
            objeto_id=cliente.id,
            objeto_str=str(cliente),
            campo='nombre',
            valor_anterior=cliente.nombre_antiguo,
            valor_nuevo=cliente.nombre,
            razon='Corrección de datos'
        )
    """
    if not hasattr(request, '_auditoria_contexto'):
        request._auditoria_contexto = {}
    
    request._auditoria_contexto.update(kwargs)


class AuditoriaMiddleware:
    """
    Middleware para capturar IP del cliente en cada request.
    Agregar a MIDDLEWARE en settings.py para que funcione automáticamente.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Guardar IP en la request para usarla después
        request.client_ip = get_client_ip(request)
        
        response = self.get_response(request)
        return response


class AuditoriaRequestMiddleware:
    """
    Middleware de auditoría automática para la mayoría de operaciones de escritura.
    Registra requests autenticadas de tipo POST/PUT/PATCH/DELETE.
    """

    EXCLUDED_PATH_PREFIXES = (
        '/static/',
        '/media/',
        '/api/',
        '/login/',
        '/logout/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not request.user.is_authenticated:
            return response

        if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return response

        if any(request.path.startswith(prefix) for prefix in self.EXCLUDED_PATH_PREFIXES):
            return response

        if response.status_code >= 500:
            return response

        if request.path.startswith('/auditoria/'):
            return response

        payload = {}
        if request.method == 'POST':
            for key, value in request.POST.items():
                if key in ('csrfmiddlewaretoken', 'password', 'password1', 'password2'):
                    continue
                payload[key] = str(value)[:200]

        if request.method == 'DELETE':
            accion = 'ELIMINAR'
        elif request.method in ('PUT', 'PATCH'):
            accion = 'EDITAR'
        elif request.method == 'POST':
            accion = 'CREAR'
        else:
            accion = 'OTRO'

        try:
            HistorioCambios.objects.create(
                usuario=request.user,
                accion=accion,
                modelo='HTTP',
                objeto_id=0,
                objeto_str=f"{request.method} {request.path}"[:255],
                campo_modificado='request',
                valor_anterior='',
                valor_nuevo=json.dumps(payload, ensure_ascii=False)[:2000],
                razon='',
                ip_address=get_client_ip(request),
                notas=f"status={response.status_code}",
            )
        except Exception:
            pass

        return response

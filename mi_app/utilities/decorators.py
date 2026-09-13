"""
Decoradores para validación de roles y permisos.
Usados en views.py para proteger vistas según autorización de usuario.

Proporciona:
- @require_rol(*roles) - Requiere uno de los roles especificados
- @require_permission(codigo) - Requiere un permiso específico
- @require_any_permission(*codigos) - Requiere al menos uno de los permisos
- @admin_required - Atajo para @require_rol('ADMIN')
- @gerente_o_admin - Atajo para @require_rol('GERENTE', 'ADMIN')
- @no_operario_solamente - Permite ADMIN y GERENTE, rechaza OPERARIO

Ejemplos de uso:

    @require_rol('ADMIN')
    def vista_admin(request):
        return render(request, 'admin.html')
    
    @require_permission('cliente.create')
    def crear_cliente(request):
        return render(request, 'crear_cliente.html')
    
    @admin_required
    def editar_configuracion(request):
        return render(request, 'config.html')
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def obtener_profile(user):
    """
    Obtiene el UsuarioProfile del usuario actual.
    Crea uno automáticamente si no existe (para compatibilidad con usuarios existentes).
    
    Args:
        user: Usuario Django autenticado
        
    Returns:
        UsuarioProfile: Perfil del usuario
    """
    from mi_app.models import UsuarioProfile, Rol
    
    profile, created = UsuarioProfile.objects.get_or_create(
        usuario=user,
        defaults={'rol': Rol.objects.filter(nombre='OPERARIO').first()}
    )
    return profile


def require_rol(*roles_permitidos):
    """
    Decorador que valida que el usuario tenga UNO de los roles especificados.
    
    Rechaza acceso si:
    - Usuario no está autenticado → Redirecciona a login
    - Usuario no tiene uno de los roles → Retorna 403 Forbidden
    
    Uso:
        @require_rol('ADMIN')
        def mi_vista(request):
            pass
        
        @require_rol('ADMIN', 'GERENTE')
        def otra_vista(request):
            pass
    
    Args:
        *roles_permitidos: Nombres de rol (ej: 'ADMIN', 'GERENTE', 'OPERARIO')
    
    Returns:
        - Acceso si el usuario tiene uno de los roles
        - Redirección a login si no está autenticado
        - HttpResponseForbidden (403) si no tiene el rol
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            profile = obtener_profile(request.user)
            
            if not profile.rol or profile.rol.nombre not in roles_permitidos:
                messages.error(
                    request,
                    f'Acceso denegado. Rol requerido: {", ".join(roles_permitidos)}'
                )
                return HttpResponseForbidden(
                    f'No tienes acceso. Solo los roles permitidos son: {", ".join(roles_permitidos)}'
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_permission(codigo_permiso):
    """
    Decorador que valida que el usuario tenga un permiso específico.
    
    Rechaza acceso si:
    - Usuario no está autenticado → Redirecciona a login
    - Usuario no tiene el permiso → Retorna 403 Forbidden
    
    Uso:
        @require_permission('cliente.create')
        def crear_cliente(request):
            pass
    
    Args:
        codigo_permiso (str): Código del permiso (ej: 'cliente.create', 'pago.create')
    
    Returns:
        - Acceso si el usuario tiene el permiso
        - Redirección a login si no está autenticado
        - HttpResponseForbidden (403) si no tiene el permiso
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            profile = obtener_profile(request.user)
            
            if not profile.tiene_permiso(codigo_permiso):
                messages.error(
                    request,
                    f'No tienes permiso para esta acción: {codigo_permiso}'
                )
                return HttpResponseForbidden(
                    f'Permiso denegado: {codigo_permiso}'
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*codigos_permiso):
    """
    Decorador que valida que el usuario tenga AL MENOS UNO de los permisos especificados.
    
    Rechaza acceso si:
    - Usuario no está autenticado → Redirecciona a login
    - Usuario no tiene NINGUNO de los permisos → Retorna 403 Forbidden
    
    Uso (usuario necesita ALGUNO de estos permisos):
        @require_any_permission('cliente.create', 'cliente.edit')
        def gestionar_cliente(request):
            pass
    
    Args:
        *codigos_permiso: Códigos de permiso (ej: 'cliente.create', 'cliente.edit')
    
    Returns:
        - Acceso si el usuario tiene al menos uno de los permisos
        - Redirección a login si no está autenticado
        - HttpResponseForbidden (403) si no tiene ninguno
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            profile = obtener_profile(request.user)
            
            tiene_permiso = any(
                profile.tiene_permiso(codigo) for codigo in codigos_permiso
            )
            
            if not tiene_permiso:
                messages.error(
                    request,
                    f'No tienes permiso para esta acción'
                )
                return HttpResponseForbidden(
                    f'Permisos requeridos (al menos uno): {", ".join(codigos_permiso)}'
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorador que requiere rol ADMIN.
    Atajo para @require_rol('ADMIN')
    
    Uso:
        @admin_required
        def mi_vista_admin(request):
            pass
    
    Returns:
        - Acceso si el usuario es ADMIN
        - HttpResponseForbidden (403) si no es ADMIN
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return require_rol('ADMIN')(view_func)(request, *args, **kwargs)
    return wrapper


def gerente_o_admin(view_func):
    """
    Decorador que requiere rol GERENTE o ADMIN.
    Atajo para @require_rol('GERENTE', 'ADMIN')
    
    Uso:
        @gerente_o_admin
        def mi_vista_gerentes(request):
            pass
    
    Returns:
        - Acceso si el usuario es GERENTE o ADMIN
        - HttpResponseForbidden (403) si es OPERARIO
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return require_rol('GERENTE', 'ADMIN')(view_func)(request, *args, **kwargs)
    return wrapper


def no_operario_solamente(view_func):
    """
    Decorador que permite todo MENOS solo OPERARIO.
    Es decir: permite ADMIN y GERENTE, rechaza OPERARIO.
    Atajo para @require_rol('ADMIN', 'GERENTE')
    
    Uso:
        @no_operario_solamente
        def editar_config(request):
            pass
    
    Returns:
        - Acceso si el usuario es ADMIN o GERENTE
        - HttpResponseForbidden (403) si es OPERARIO
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return require_rol('ADMIN', 'GERENTE')(view_func)(request, *args, **kwargs)
    return wrapper


def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente considerando proxies y balanceadores.
    
    Intenta obtener la IP real del cliente incluso detrás de proxies.
    Usado para auditoría de seguridad e intentos de violación.
    
    Verifica en orden:
    1. X-Forwarded-For (cabecera común en proxies/load balancers)
    2. REMOTE_ADDR (IP directa si no hay proxy)
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP
        
    Returns:
        str: Dirección IP del cliente (ej: "192.168.1.1")
    
    Example:
        >>> ip = get_client_ip(request)
        >>> logger.warning(f"Intento de acceso desde IP {ip}")
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

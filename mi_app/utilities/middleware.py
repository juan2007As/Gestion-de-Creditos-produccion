"""
Middleware personalizado para manejo de errores globales.
Incluye manejador de rate limiting (429 Too Many Requests).
"""

from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Middleware para capturar excepciones de rate limiting y retornar 429.
    
    ✅ SEGURIDAD MEJORADA (Bloque B - REGLA #3):
    - Previene DOS attacks en endpoints críticos (backup_rapido_*)
    - Retorna respuesta JSON 429 consistent con API
    - Registra intentos de abuso en logs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Ratelimited as e:
            # 🔒 Rate limit excedido
            logger.warning(
                f"🚨 RATE LIMIT EXCEDIDO: {request.user} "
                f"en {request.path} - IP: {self.get_client_ip(request)}"
            )
            
            # Responer con 429 Too Many Requests
            if request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': '⏱️ Demasiadas solicitudes. Intenta de nuevo en 1 minuto.',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }, status=429)
            else:
                return JsonResponse({
                    'error': 'Too Many Requests'
                }, status=429)
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Obtener IP del cliente considerando proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

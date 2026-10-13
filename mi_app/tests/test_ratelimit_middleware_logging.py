from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django_ratelimit.exceptions import Ratelimited

from mi_app.utilities.middleware import RateLimitMiddleware


class RateLimitMiddlewareLoggingTests(TestCase):
    """
    Regresión de auditoría de seguridad (DEUDA-TECNICA.md #22ter):
    RateLimitMiddleware.__call__ tenía logger.warning(f"🚨 RATE LIMIT
    EXCEDIDO...") con emoji -- mismo patrón del bug ya resuelto en
    DEUDA-TECNICA.md #39 (UnicodeEncodeError en consola Windows sin UTF-8).
    Esta vista solo se ejecuta cuando RateLimitMiddleware de verdad atrapa
    un Ratelimited, algo que solo pasa en PRODUCTION/STAGING (el middleware
    no está registrado en local) -- por eso se prueba el middleware
    directamente en vez de depender de una vista real.
    """

    def setUp(self):
        self.factory = RequestFactory()

        def get_response_que_siempre_limita(request):
            raise Ratelimited()

        self.middleware = RateLimitMiddleware(get_response_que_siempre_limita)

    def test_no_revienta_con_unicodeencodeerror_al_loguear(self):
        request = self.factory.post('/backup/generar/')
        request.user = AnonymousUser()

        # Antes del fix, esto reventaba con UnicodeEncodeError en una
        # consola Windows sin UTF-8 en vez de devolver la respuesta 429.
        response = self.middleware(request)

        self.assertEqual(response.status_code, 429)

"""
Context processors para agregar información del ambiente a los templates
"""

def environment_context(request):
    """
    Agrega información del ambiente actual a todos los templates
    """
    from django.conf import settings

    return {
        'ENVIRONMENT': getattr(settings, 'ENVIRONMENT', 'unknown'),
        'DEBUG': getattr(settings, 'DEBUG', False),
        'PRODUCTION': getattr(settings, 'ENVIRONMENT', 'local') == 'production',
        'STAGING': getattr(settings, 'ENVIRONMENT', 'local') == 'staging',
        'LOCAL': getattr(settings, 'ENVIRONMENT', 'local') == 'local',
        'CREDITS_CONFIG': getattr(settings, 'CREDITS_CONFIG', {}),
    }
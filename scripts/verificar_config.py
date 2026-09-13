#!/usr/bin/env python
"""
Script para verificar la configuración actual del proyecto
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.conf import settings
import json

def verificar_configuracion():
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 50)

    # Ambiente
    print(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    print(f"🐛 Debug: {settings.DEBUG}")
    print(f"🏭 Producción: {getattr(settings, 'PRODUCTION', False)}")
    print(f"🧪 Staging: {getattr(settings, 'STAGING', False)}")
    print(f"🏠 Local: {getattr(settings, 'LOCAL', False)}")

    print("\n💾 BASE DE DATOS:")
    db_config = settings.DATABASES['default']
    print(f"  Motor: {db_config['ENGINE'].split('.')[-1]}")
    print(f"  Nombre: {db_config['NAME']}")

    if settings.ENVIRONMENT != 'local':
        print(f"  Usuario: {db_config['USER']}")
        print(f"  Host: {db_config['HOST']}:{db_config['PORT']}")

    print("\n⚙️ CONFIGURACIÓN DE CRÉDITOS:")
    for key, value in settings.CREDITS_CONFIG.items():
        print(f"  {key}: {value}")

    print("\n🔒 SEGURIDAD:")
    print(f"  Secret Key: {'✅ Configurada' if settings.SECRET_KEY != 'django-insecure-dev-key-change-in-production' else '⚠️ Usando clave por defecto'}")
    print(f"  Allowed Hosts: {', '.join(settings.ALLOWED_HOSTS)}")
    print(f"  SSL Redirect: {getattr(settings, 'SECURE_SSL_REDIRECT', False)}")

    print("\n📧 EMAIL:")
    if hasattr(settings, 'EMAIL_BACKEND'):
        if 'console' in settings.EMAIL_BACKEND:
            print("  Backend: Console (desarrollo)")
        else:
            print("  Backend: SMTP (producción)")
            print(f"  Host: {getattr(settings, 'EMAIL_HOST', 'No configurado')}")

    print("\n✅ VERIFICACIÓN COMPLETADA")

if __name__ == '__main__':
    verificar_configuracion()
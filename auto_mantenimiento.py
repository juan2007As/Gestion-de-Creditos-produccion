import os
import django
from datetime import datetime

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.core.management import call_command
from mi_app.models import Cliente

def ejecutar_mantenimiento_automatico():
    print(f"\n{'='*70}")
    print(f"INICIANDO MANTENIMIENTO AUTOMÁTICO - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 1. Ejecutar Auto-tagging de Lista Negra
        print("\n--- 1. PROCESANDO LISTA NEGRA ---")
        call_command('auto_tagging_lista_negra', dias=30, dry_run=False, verbose=True)
        
        # 2. Ejecutar Auto-tagging de Etiquetas (Bueno/Medio/Malo)
        print("\n--- 2. ACTUALIZANDO ETIQUETAS DE CLIENTES ---")
        call_command('auto_tagging_etiquetas', dry_run=False, verbose=True)
        
        # 3. Sincronizar estados de cuotas (por si acaso)
        print("\n--- 3. SINCRONIZANDO ESTADOS DE CUOTAS ---")
        call_command('sincronizar_estados_cuotas')
        
        print(f"\n{'='*70}")
        print(f"✅ MANTENIMIENTO COMPLETADO EXITOSAMENTE")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO durante el mantenimiento: {str(e)}")

if __name__ == '__main__':
    ejecutar_mantenimiento_automatico()

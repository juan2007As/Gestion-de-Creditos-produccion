import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import (
    Cliente, Prestamo, Cuota, Pago, 
    PrestamoRapido, CuotaRapida, PagoPrestamoRapido,
    HistorioCambios, AuditLog, AuditoriaBackup,
    ListaNegra, ClienteScoring
)
from django.contrib.auth.models import User

def limpiar_base_de_datos():
    print("⚠️  ADVERTENCIA: Iniciando limpieza total de datos de negocio...")
    print("Esto NO borrará los usuarios ni los roles configurados.")
    
    try:
        # 1. Datos de Préstamos y Pagos
        print("🗑️  Borrando Pagos...")
        Pago.objects.all().delete()
        PagoPrestamoRapido.objects.all().delete()
        
        print("🗑️  Borrando Cuotas...")
        Cuota.objects.all().delete()
        CuotaRapida.objects.all().delete()
        
        print("🗑️  Borrando Préstamos...")
        Prestamo.objects.all().delete()
        PrestamoRapido.objects.all().delete()
        
        # 2. Datos de Clientes y Scoring
        print("🗑️  Borrando Historial de Scoring y Listas Negras...")
        ClienteScoring.objects.all().delete()
        ListaNegra.objects.all().delete()
        
        print("🗑️  Borrando Clientes...")
        Cliente.objects.all().delete()
        
        # 3. Logs y Auditoría
        print("🗑️  Borrando Logs de Auditoría y Cambios...")
        HistorioCambios.objects.all().delete()
        AuditLog.objects.all().delete()
        AuditoriaBackup.objects.all().delete()
        
        print("\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE.")
        print("La base de datos de negocio está vacía y lista para usar.")
        
    except Exception as e:
        print(f"\n❌ ERROR durante la limpieza: {str(e)}")

if __name__ == '__main__':
    confirmacion = input("¿Estás SEGURO de que quieres borrar TODOS los datos de clientes, préstamos y pagos? (si/no): ")
    if confirmacion.lower() == 'si':
        limpiar_base_de_datos()
    else:
        print("❌ Operación cancelada.")

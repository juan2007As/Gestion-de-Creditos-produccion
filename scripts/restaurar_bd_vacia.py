"""
SCRIPT DE RESTAURACIÓN: Resetea BD a estado vacío
==================================================

Uso:
    python restaurar_bd_vacia.py

Esto borrará TODOS los clientes y sus datos, manteniendo solo el superuser.
Confirmará antes de hacerlo.
"""

import os
import shutil
from datetime import datetime

# Archivos de BD
BD_ACTUAL = "db.sqlite3"
BD_VACIA = "BD_VACIA_BACKUP_20260203_164502.sqlite3"

def main():
    print("=" * 70)
    print("🗑️  RESTAURAR BASE DE DATOS A ESTADO VACÍO")
    print("=" * 70)
    
    # Verificar que el backup existe
    if not os.path.exists(BD_VACIA):
        print(f"\n❌ ERROR: Backup '{BD_VACIA}' no encontrado")
        print(f"   Ubicación esperada: {os.path.abspath(BD_VACIA)}")
        return
    
    print(f"\n📁 Archivos:")
    print(f"   BD Actual: {BD_ACTUAL} ({os.path.getsize(BD_ACTUAL)} bytes)")
    print(f"   BD Vacía:  {BD_VACIA} ({os.path.getsize(BD_VACIA)} bytes)")
    
    print("\n⚠️  ADVERTENCIA:")
    print("   - Se BORRARÁN TODOS los clientes importados")
    print("   - Se BORRARÁN TODOS los préstamos y cuotas")
    print("   - El superuser 'admin' se PRESERVARÁ")
    print("   - No hay forma de recuperar los datos después")
    
    # Confirmar
    confirmacion = input("\n¿Estás seguro de continuar? (sí/no): ").strip().lower()
    
    if confirmacion not in ['sí', 'si', 'yes', 'y']:
        print("\n❌ Operación cancelada")
        return
    
    # Crear respaldo de la BD actual antes de restaurar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo_anterior = f"db.sqlite3.backup_{timestamp}"
    
    print(f"\n💾 Creando respaldo de BD actual: {respaldo_anterior}")
    shutil.copy2(BD_ACTUAL, respaldo_anterior)
    
    # Restaurar BD vacía
    print(f"⏳ Restaurando BD vacía...")
    shutil.copy2(BD_VACIA, BD_ACTUAL)
    
    print("\n✅ BASE DE DATOS RESTAURADA")
    print(f"\n📊 Estado:")
    print(f"   - Clientes: 0")
    print(f"   - Préstamos: 0")
    print(f"   - Cuotas: 0")
    print(f"   - Superuser: admin (preservado)")
    print(f"\n💾 Respaldo anterior guardado como: {respaldo_anterior}")
    print("\n🚀 Puedes importar nuevamente el Excel de clientes")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

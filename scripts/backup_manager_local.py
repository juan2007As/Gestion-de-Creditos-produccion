"""
Gestor de Backups LOCAL (Sin Google Drive)
Guarda backups en carpeta local: /backups/
Comprime automáticamente, mantiene últimos 30
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.conf import settings


class LocalBackupManager:
    """Maneja backups locales sin dependencias externas"""
    
    BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')
    MAX_BACKUPS = 30
    DB_FILE = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    
    def __init__(self):
        """Inicializa el gestor de backups"""
        self.create_backup_dir()
    
    def create_backup_dir(self):
        """Crea la carpeta de backups si no existe"""
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        print(f"✅ Carpeta de backups lista: {self.BACKUP_DIR}")
    
    def get_backup_filename(self):
        """Genera nombre único para el backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_{timestamp}.zip"
    
    def create_backup(self):
        """Crea un backup comprimido de la BD"""
        try:
            print("\n" + "="*60)
            print("🔄 INICIANDO BACKUP LOCAL")
            print("="*60)
            
            if not os.path.exists(self.DB_FILE):
                print(f"❌ Error: Base de datos no encontrada: {self.DB_FILE}")
                return False
            
            backup_name = self.get_backup_filename()
            backup_path = os.path.join(self.BACKUP_DIR, backup_name)
            
            print(f"📦 Base de datos: {self.DB_FILE}")
            print(f"💾 Guardando en: {backup_path}")
            
            # Crear ZIP
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                arcname = os.path.basename(self.DB_FILE)
                zipf.write(self.DB_FILE, arcname=arcname)
            
            # Obtener tamaño
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            print(f"✅ Backup creado: {backup_name} ({size_mb:.2f} MB)")
            
            # Limpiar backups antiguos
            self.cleanup_old_backups()
            
            print("✅ Backup completado exitosamente")
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"❌ Error al crear backup: {str(e)}")
            print("="*60 + "\n")
            return False
    
    def cleanup_old_backups(self):
        """Elimina backups antiguos, mantiene solo los últimos MAX_BACKUPS"""
        try:
            backups = sorted(
                [f for f in os.listdir(self.BACKUP_DIR) if f.startswith('backup_')],
                reverse=True
            )
            
            if len(backups) > self.MAX_BACKUPS:
                print(f"🧹 Limpiando backups antiguos (máximo {self.MAX_BACKUPS})...")
                for backup in backups[self.MAX_BACKUPS:]:
                    backup_path = os.path.join(self.BACKUP_DIR, backup)
                    os.remove(backup_path)
                    print(f"   ✓ Eliminado: {backup}")
            
            print(f"📊 Backups guardados: {len(backups[:self.MAX_BACKUPS])}/{self.MAX_BACKUPS}")
            
        except Exception as e:
            print(f"⚠️  Error al limpiar backups: {str(e)}")
    
    def list_backups(self):
        """Lista todos los backups disponibles"""
        try:
            backups = sorted(
                [f for f in os.listdir(self.BACKUP_DIR) if f.startswith('backup_')],
                reverse=True
            )
            
            if not backups:
                print("ℹ️  No hay backups disponibles")
                return
            
            print("\n" + "="*60)
            print("📋 BACKUPS DISPONIBLES")
            print("="*60)
            
            for i, backup in enumerate(backups, 1):
                backup_path = os.path.join(self.BACKUP_DIR, backup)
                size_mb = os.path.getsize(backup_path) / (1024 * 1024)
                mod_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
                
                print(f"{i}. {backup}")
                print(f"   Tamaño: {size_mb:.2f} MB")
                print(f"   Fecha: {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
                print()
            
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ Error al listar backups: {str(e)}")
    
    def restore_backup(self, backup_filename):
        """Restaura una BD desde un backup"""
        try:
            backup_path = os.path.join(self.BACKUP_DIR, backup_filename)
            
            if not os.path.exists(backup_path):
                print(f"❌ Error: Backup no encontrado: {backup_filename}")
                return False
            
            print("\n" + "="*60)
            print("🔄 RESTAURANDO BACKUP")
            print("="*60)
            print(f"Archivo: {backup_filename}")
            
            # Hacer backup de la BD actual
            current_backup = f"{self.DB_FILE}.backup"
            if os.path.exists(self.DB_FILE):
                shutil.copy(self.DB_FILE, current_backup)
                print(f"💾 BD actual respaldada en: {current_backup}")
            
            # Restaurar
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(settings.BASE_DIR)
            
            print("✅ Backup restaurado exitosamente")
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"❌ Error al restaurar: {str(e)}")
            print("="*60 + "\n")
            return False
    
    def get_backup_info(self):
        """Retorna información sobre el espacio de backups"""
        try:
            if not os.path.exists(self.BACKUP_DIR):
                return None
            
            total_size = 0
            backup_count = 0
            
            for f in os.listdir(self.BACKUP_DIR):
                if f.startswith('backup_'):
                    file_path = os.path.join(self.BACKUP_DIR, f)
                    total_size += os.path.getsize(file_path)
                    backup_count += 1
            
            return {
                'backup_dir': self.BACKUP_DIR,
                'total_size_mb': total_size / (1024 * 1024),
                'backup_count': backup_count,
                'max_backups': self.MAX_BACKUPS,
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return None


# ============================================================================
# INTERFAZ DE LÍNEA DE COMANDOS
# ============================================================================

if __name__ == '__main__':
    import sys
    
    manager = LocalBackupManager()
    
    if len(sys.argv) < 2:
        # Sin argumentos: hacer backup
        manager.create_backup()
    else:
        command = sys.argv[1].lower()
        
        if command == 'create':
            manager.create_backup()
        
        elif command == 'list':
            manager.list_backups()
        
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("Uso: python backup_manager.py restore <nombre_archivo>")
                print("\nEjemplo: python backup_manager.py restore backup_20260131_203045.zip")
                manager.list_backups()
            else:
                manager.restore_backup(sys.argv[2])
        
        elif command == 'info':
            info = manager.get_backup_info()
            if info:
                print("\n" + "="*60)
                print("📊 INFORMACIÓN DE BACKUPS")
                print("="*60)
                print(f"Carpeta: {info['backup_dir']}")
                print(f"Tamaño total: {info['total_size_mb']:.2f} MB")
                print(f"Backups guardados: {info['backup_count']}/{info['max_backups']}")
                print("="*60 + "\n")
        
        else:
            print(f"Comando desconocido: {command}")
            print("\nComandos disponibles:")
            print("  python backup_manager.py create   - Crear backup")
            print("  python backup_manager.py list     - Listar backups")
            print("  python backup_manager.py info     - Ver info de backups")
            print("  python backup_manager.py restore <archivo> - Restaurar backup")

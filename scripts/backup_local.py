"""
Backup Local - Copias de Seguridad Gratis
Comprime la BD SQLite y guarda en carpeta local
Sin pagar nada, sin dependencias externas
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import zipfile
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.conf import settings


class BackupLocal:
    """Gestor de backups locales - 100% GRATIS"""
    
    BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')
    MAX_BACKUPS = 30  # Mantener últimos 30 backups
    
    def __init__(self):
        self.create_backup_dir()
        self.log_file = os.path.join(settings.BASE_DIR, 'logs', 'backup_local.log')
    
    def log(self, message):
        """Registra mensaje en log y consola"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Guardar en archivo de log
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except:
            pass
    
    def create_backup_dir(self):
        """Crea carpeta de backups si no existe"""
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        self.log(f"✅ Carpeta de backups: {self.BACKUP_DIR}")
    
    def backup_database(self):
        """Hace copia de la base de datos"""
        try:
            db_path = str(settings.DATABASES['default']['NAME'])
            
            if not os.path.exists(db_path):
                self.log(f"❌ BD no encontrada: {db_path}")
                return False
            
            # Nombre del backup con fecha y hora
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}.zip"
            backup_path = os.path.join(self.BACKUP_DIR, backup_name)
            
            # Obtener tamaño original
            original_size = os.path.getsize(db_path) / (1024 * 1024)
            self.log(f"📊 Tamaño BD original: {original_size:.2f} MB")
            
            # Comprimir
            self.log(f"📦 Comprimiendo BD...")
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(db_path, arcname='db.sqlite3')
            
            # Tamaño comprimido
            compressed_size = os.path.getsize(backup_path) / (1024 * 1024)
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            self.log(f"✅ Backup creado: {backup_name}")
            self.log(f"📦 Tamaño comprimido: {compressed_size:.2f} MB (reducción: {ratio:.1f}%)")
            
            # Limpiar backups antiguos
            self.cleanup_old_backups()
            
            self.log(f"🎉 Backup completado exitosamente!")
            return True
            
        except Exception as e:
            self.log(f"❌ Error en backup: {str(e)}")
            return False
    
    def cleanup_old_backups(self):
        """Elimina backups más viejos que MAX_BACKUPS"""
        try:
            # Listar todos los backups
            files = sorted(
                [f for f in os.listdir(self.BACKUP_DIR) if f.startswith('backup_')],
                reverse=True
            )
            
            self.log(f"📋 Total de backups: {len(files)}")
            
            if len(files) > self.MAX_BACKUPS:
                to_delete = files[self.MAX_BACKUPS:]
                self.log(f"🗑️  Eliminando {len(to_delete)} backups antiguos...")
                
                for f in to_delete:
                    path = os.path.join(self.BACKUP_DIR, f)
                    try:
                        os.remove(path)
                        self.log(f"   - Eliminado: {f}")
                    except:
                        pass
                
                self.log(f"✅ Manteniendo últimos {self.MAX_BACKUPS} backups")
        
        except Exception as e:
            self.log(f"⚠️  Error limpiando: {str(e)}")
    
    def list_backups(self):
        """Lista todos los backups disponibles"""
        try:
            files = sorted(
                [f for f in os.listdir(self.BACKUP_DIR) if f.startswith('backup_')],
                reverse=True
            )
            
            if not files:
                self.log("📭 No hay backups disponibles")
                return
            
            self.log(f"\n📋 Backups disponibles ({len(files)}):")
            for i, f in enumerate(files[:10], 1):  # Mostrar últimos 10
                path = os.path.join(self.BACKUP_DIR, f)
                size = os.path.getsize(path) / (1024 * 1024)
                mod_time = datetime.fromtimestamp(os.path.getmtime(path))
                self.log(f"   {i}. {f} ({size:.2f} MB) - {mod_time}")
            
            if len(files) > 10:
                self.log(f"   ... y {len(files) - 10} más")
        
        except Exception as e:
            self.log(f"⚠️  Error listando: {str(e)}")


if __name__ == '__main__':
    import sys
    
    backup = BackupLocal()
    
    # Ver opciones
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        backup.list_backups()
    else:
        # Hacer backup por defecto
        backup.backup_database()

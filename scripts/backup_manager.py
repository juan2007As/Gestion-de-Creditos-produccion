"""
Gestor de Backups a Google Drive
Realiza copia automática de la base de datos SQLite a Google Drive
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.conf import settings


class GoogleDriveBackup:
    """Maneja backups a Google Drive"""
    
    FOLDER_ID = "1ddrGXyqDRQ_EDlc5Xoa4arls9-5SRrTQ"  
    MAX_BACKUPS = 30  # Mantener últimos 30 backups
    CREDENTIALS_FILE = os.path.join(settings.BASE_DIR, 'config', 'google_drive_credentials.json')
    
    def __init__(self):
        """Inicializa el gestor de backups"""
        self.service = None
        self.folder_id = None
        self.authenticate()
    
    def authenticate(self):
        """Autentica con Google Drive usando credenciales de service account"""
        try:
            if not os.path.exists(self.CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Archivo de credenciales no encontrado: {self.CREDENTIALS_FILE}\n"
                    "Ejecuta: python setup_backup.py"
                )
            
            credentials = Credentials.from_service_account_file(
                self.CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            print("✅ Autenticación exitosa con Google Drive")
            
        except Exception as e:
            print(f"❌ Error en autenticación: {str(e)}")
            raise
    
    def get_or_create_backup_folder(self):
        """Obtiene la carpeta compartida de backups"""
        try:
            # Usar directamente el ID de la carpeta compartida
            self.folder_id = self.FOLDER_ID
            print(f"✅ Usando carpeta compartida: {self.FOLDER_ID}")
            return self.folder_id
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
    
    def upload_backup(self, file_path, file_name):
        """Sube un archivo de backup a Google Drive"""
        try:
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, createdTime, size'
            ).execute()
            
            print(f"✅ Backup subido: {file_name}")
            print(f"   ID: {file.get('id')}")
            print(f"   Tamaño: {file.get('size', 0)} bytes")
            print(f"   Fecha: {file.get('createdTime')}")
            
            return file.get('id')
        
        except Exception as e:
            print(f"❌ Error al subir backup: {str(e)}")
            raise
    
    def list_backups(self, limit=None):
        """Lista los backups almacenados en Google Drive"""
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                pageSize=100,
                fields='files(id, name, createdTime, size)',
                orderBy='createdTime desc'
            ).execute()
            
            files = results.get('files', [])
            
            if limit:
                files = files[:limit]
            
            print(f"\n📋 Backups en Google Drive ({len(files)} encontrados):")
            print("-" * 80)
            
            for i, file in enumerate(files, 1):
                size_mb = int(file.get('size', 0)) / (1024 * 1024)
                print(f"{i}. {file['name']}")
                print(f"   Tamaño: {size_mb:.2f} MB | Fecha: {file['createdTime']}")
            
            return files
        
        except Exception as e:
            print(f"❌ Error al listar backups: {str(e)}")
            return []
    
    def delete_old_backups(self):
        """Elimina backups antiguos, manteniendo solo los últimos MAX_BACKUPS"""
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                pageSize=100,
                fields='files(id, name, createdTime)',
                orderBy='createdTime desc'
            ).execute()
            
            files = results.get('files', [])
            
            if len(files) > self.MAX_BACKUPS:
                to_delete = files[self.MAX_BACKUPS:]
                print(f"\n🗑️  Eliminando {len(to_delete)} backups antiguos...")
                
                for file in to_delete:
                    self.service.files().delete(fileId=file['id']).execute()
                    print(f"   ✅ Eliminado: {file['name']}")
        
        except Exception as e:
            print(f"❌ Error al eliminar backups antiguos: {str(e)}")
    
    def create_backup(self):
        """Crea un backup de la base de datos"""
        try:
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Base de datos no encontrada: {db_path}")
            
            # Crear nombre con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_db_{timestamp}.sqlite3"
            
            # Crear archivo temporal
            temp_backup = os.path.join(settings.BASE_DIR, f'temp_{backup_filename}')
            
            print(f"\n📦 Creando backup: {backup_filename}")
            
            # Copiar base de datos
            shutil.copy2(db_path, temp_backup)
            print(f"✅ Base de datos copiada")
            
            # Asegurar que la carpeta existe
            if not self.folder_id:
                self.get_or_create_backup_folder()
            
            # Subir a Google Drive
            self.upload_backup(temp_backup, backup_filename)
            
            # Limpiar archivo temporal
            os.remove(temp_backup)
            
            # Eliminar backups antiguos
            self.delete_old_backups()
            
            return True
        
        except Exception as e:
            print(f"❌ Error al crear backup: {str(e)}")
            return False


def main():
    """Función principal"""
    print("=" * 80)
    print("🔄 GESTOR DE BACKUPS - Google Drive")
    print("=" * 80)
    
    try:
        backup = GoogleDriveBackup()
        backup.get_or_create_backup_folder()
        
        import sys
        
        if len(sys.argv) > 1:
            if sys.argv[1] == 'list':
                backup.list_backups()
            elif sys.argv[1] == 'clean':
                backup.delete_old_backups()
            else:
                backup.create_backup()
        else:
            backup.create_backup()
    
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

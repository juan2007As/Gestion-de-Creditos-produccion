"""
Sistema de Backups Local
Crea y gestiona backups de la BD en la carpeta /backups
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class BackupManager:
    """Gestor de backups locales"""
    
    def __init__(self):
        # Ajuste para PythonAnywhere: buscar la BD en la raíz del proyecto
        # Si el archivo está en mi_app/utilities/backup_manager.py, subimos 2 niveles para llegar a la raíz
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.backups_dir = os.path.join(self.base_dir, 'backups')
        self.db_path = os.path.join(self.base_dir, 'db.sqlite3')
        
        # DEBUG para consola
        print(f"DEBUG BackupManager: BASE_DIR={self.base_dir}")
        print(f"DEBUG BackupManager: DB_PATH={self.db_path}")
        
        # Crear directorio si no existe
        if not os.path.exists(self.backups_dir):
            os.makedirs(self.backups_dir, exist_ok=True)
    
    def create_backup(self):
        """Crea un nuevo backup de la BD"""
        try:
            print(f"DEBUG: Intentando backup. DB_PATH: {self.db_path}")
            if not os.path.exists(self.db_path):
                # Intentar ruta alternativa si falla
                alt_db_path = os.path.join(os.getcwd(), 'db.sqlite3')
                if os.path.exists(alt_db_path):
                    self.db_path = alt_db_path
                else:
                    return {'success': False, 'error': f'Base de datos no encontrada en {self.db_path}'}
            
            # Generar nombre con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.sqlite3"
            backup_path = os.path.join(self.backups_dir, backup_name)
            
            # Copiar BD
            shutil.copy2(self.db_path, backup_path)
            
            # Crear metadata
            metadata = {
                'nombre': backup_name,
                'fecha': datetime.now().isoformat(),
                'tamaño': os.path.getsize(backup_path),
                'descripcion': 'Backup automático'
            }
            
            # Guardar metadata
            metadata_path = backup_path + '.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                'success': True,
                'mensaje': f'Backup creado: {backup_name}',
                'backup_path': backup_path,
                'nombre': backup_name
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_backups(self):
        """Lista todos los backups disponibles (sqlite3 y zip)"""
        backups = []
        
        try:
            for filename in sorted(os.listdir(self.backups_dir), reverse=True):
                if filename.endswith('.sqlite3') or filename.endswith('.zip'):
                    backup_path = os.path.join(self.backups_dir, filename)
                    metadata_path = backup_path + '.json'
                    
                    # Intentar leer metadata
                    metadata = {'fecha': datetime.fromtimestamp(os.path.getmtime(backup_path)).isoformat()}
                    if os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                        except:
                            pass
                    
                    backups.append({
                        'nombre': filename,
                        'ruta': backup_path,
                        'tamaño': os.path.getsize(backup_path),
                        'fecha': metadata.get('fecha', ''),
                        'descripcion': metadata.get('descripcion', 'Sin descripción'),
                        'id': filename.replace('backup_', '').replace('.sqlite3', '').replace('.zip', '')
                    })
        
        except Exception as e:
            print(f"Error listando backups: {e}")
        
        return backups
    
    def restore_backup(self, backup_id):
        """Restaura un backup específico (sqlite3 o zip)"""
        try:
            # Buscar el archivo (puede ser .sqlite3 o .zip)
            backup_filename_sqlite = f"backup_{backup_id}.sqlite3"
            backup_filename_zip = f"backup_{backup_id}.zip"
            
            backup_path = os.path.join(self.backups_dir, backup_filename_sqlite)
            is_zip = False
            
            if not os.path.exists(backup_path):
                backup_path = os.path.join(self.backups_dir, backup_filename_zip)
                is_zip = True
                
            if not os.path.exists(backup_path):
                return {'success': False, 'error': 'Backup no encontrado'}
            
            # Crear respaldo de la BD actual antes de restaurar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"db.sqlite3.backup_{timestamp}"
            current_backup_path = os.path.join(self.base_dir, current_backup)
            
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, current_backup_path)
            
            # Restaurar backup
            if is_zip:
                import zipfile
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    # Buscar db.sqlite3 dentro del zip
                    zip_ref.extract('db.sqlite3', self.base_dir)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            return {
                'success': True,
                'mensaje': f'Backup restaurado: {os.path.basename(backup_path)}',
                'respaldo_anterior': current_backup
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_backup(self, backup_id):
        """Elimina un backup específico (sqlite3 o zip)"""
        try:
            backup_filename_sqlite = f"backup_{backup_id}.sqlite3"
            backup_filename_zip = f"backup_{backup_id}.zip"
            
            deleted = False
            for filename in [backup_filename_sqlite, backup_filename_zip]:
                backup_path = os.path.join(self.backups_dir, filename)
                metadata_path = backup_path + '.json'
                
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    deleted = True
                
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
            
            if deleted:
                return {'success': True, 'mensaje': 'Backup eliminado'}
            else:
                return {'success': False, 'error': 'Backup no encontrado'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Crear instancia global
backup_manager = BackupManager()

"""
Sincronización SIMPLE de backups a VPS
Solo subir y restaurar, nada más.
"""

import os
import json
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BackupVPSSync:
    """Sincronización simple - solo subir y restaurar"""
    
    def __init__(self):
        self.config_path = Path("vps_config.json")
        self.local_path = Path("backups")
        self.config = None
        
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self.config = json.load(f)
            except:
                pass
    
    def subir_backup(self, nombre):
        """Sube backup a VPS"""
        if not self.config:
            return {"ok": False}
        
        try:
            archivo = self.local_path / nombre
            if not archivo.exists():
                return {"ok": False}
            
            host = self.config.get("vps_host")
            user = self.config.get("vps_user")
            port = self.config.get("vps_port", "22")
            vps_path = self.config.get("vps_backup_path")
            
            cmd = f'scp -P {port} "{archivo}" {user}@{host}:{vps_path}/{nombre}'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            
            return {"ok": result.returncode == 0}
        except:
            return {"ok": False}
    
    def restaurar_desde_vps(self, nombre):
        """Descarga backup desde VPS"""
        if not self.config:
            return {"ok": False, "archivo": None}
        
        try:
            host = self.config.get("vps_host")
            user = self.config.get("vps_user")
            port = self.config.get("vps_port", "22")
            vps_path = self.config.get("vps_backup_path")
            
            archivo_local = self.local_path / nombre
            self.local_path.mkdir(exist_ok=True)
            
            cmd = f'scp -P {port} {user}@{host}:{vps_path}/{nombre} "{archivo_local}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            
            if result.returncode == 0:
                return {"ok": True, "archivo": nombre}
            return {"ok": False, "archivo": None}
        except:
            return {"ok": False, "archivo": None}

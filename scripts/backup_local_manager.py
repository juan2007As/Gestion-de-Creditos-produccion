"""
Sistema de Gestión de Backups Locales para Proyecto John
Maneja creación, compresión, eliminación y restauración de backups de BD
"""

import os
import shutil
import gzip
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

# Configuración - RAÍZ DEL PROYECTO
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'backups')
DB_PATH = os.path.join(PROJECT_ROOT, 'db.sqlite3')
BACKUP_RETENTION_DAYS = 30
MAX_BACKUP_SIZE_MB = 100

# Crear directorio de backups si no existe
Path(BACKUP_DIR).mkdir(exist_ok=True)

# Configurar logging
logging.basicConfig(
    filename=os.path.join(BACKUP_DIR, 'backup.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class BackupLocalManager:
    """Gestor de backups locales para la base de datos SQLite3"""
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.db_path = DB_PATH
        self.retention_days = BACKUP_RETENTION_DAYS
    
    def crear_backup(self, descripcion="Backup automático"):
        """
        Crea un backup de la base de datos SQLite3
        
        Args:
            descripcion (str): Descripción del backup
            
        Returns:
            dict: {
                'success': bool,
                'archivo': str (nombre del archivo),
                'ruta_completa': str,
                'tamaño_mb': float,
                'error': str (si aplica)
            }
        """
        try:
            if not os.path.exists(self.db_path):
                return {
                    'success': False,
                    'error': f'Base de datos no encontrada: {self.db_path}'
                }
            
            # Crear nombre de archivo con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_nombre = f'backup_{timestamp}.db'
            backup_path = os.path.join(self.backup_dir, backup_nombre)
            
            # Copiar archivo de BD
            shutil.copy2(self.db_path, backup_path)
            
            # Obtener tamaño
            tamaño_bytes = os.path.getsize(backup_path)
            tamaño_mb = tamaño_bytes / (1024 * 1024)
            
            # Registrar en log
            logger.info(f'✅ Backup creado: {backup_nombre} ({tamaño_mb:.2f} MB) - {descripcion}')
            
            return {
                'success': True,
                'archivo': backup_nombre,
                'ruta_completa': backup_path,
                'tamaño_mb': tamaño_mb,
                'timestamp': timestamp
            }
            
        except Exception as e:
            error_msg = f'❌ Error al crear backup: {str(e)}'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def comprimir_backup(self, nombre_archivo):
        """
        Comprime un backup con gzip (reduce ~70%)
        
        Args:
            nombre_archivo (str): Nombre del archivo a comprimir
            
        Returns:
            dict: {
                'success': bool,
                'archivo_comprimido': str,
                'tamaño_original_mb': float,
                'tamaño_comprimido_mb': float,
                'porcentaje_reduccion': float,
                'error': str (si aplica)
            }
        """
        try:
            ruta_original = os.path.join(self.backup_dir, nombre_archivo)
            
            if not os.path.exists(ruta_original):
                return {
                    'success': False,
                    'error': f'Archivo no encontrado: {nombre_archivo}'
                }
            
            ruta_comprimida = f'{ruta_original}.gz'
            
            # Comprimir
            with open(ruta_original, 'rb') as f_in:
                with gzip.open(ruta_comprimida, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Calcular tamaños
            tamaño_original = os.path.getsize(ruta_original) / (1024 * 1024)
            tamaño_comprimido = os.path.getsize(ruta_comprimida) / (1024 * 1024)
            porcentaje = ((tamaño_original - tamaño_comprimido) / tamaño_original) * 100
            
            # Eliminar archivo original
            os.remove(ruta_original)
            
            logger.info(f'✅ Backup comprimido: {nombre_archivo}.gz ({porcentaje:.1f}% reducción)')
            
            return {
                'success': True,
                'archivo_comprimido': f'{nombre_archivo}.gz',
                'tamaño_original_mb': tamaño_original,
                'tamaño_comprimido_mb': tamaño_comprimido,
                'porcentaje_reduccion': porcentaje
            }
            
        except Exception as e:
            error_msg = f'❌ Error al comprimir backup: {str(e)}'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def listar_backups(self):
        """
        Lista todos los backups disponibles (ordenados por fecha descendente)
        
        Returns:
            list: [{
                'archivo': str,
                'tamaño_mb': float,
                'fecha_creacion': datetime,
                'dias_antigüedad': int,
                'ruta': str
            }, ...]
        """
        try:
            backups = []
            ahora = datetime.now()
            
            if not os.path.exists(self.backup_dir):
                return []
            
            for archivo in os.listdir(self.backup_dir):
                if archivo.startswith('backup_') and (archivo.endswith('.db') or archivo.endswith('.db.gz') or archivo.endswith('.zip')):
                    ruta_completa = os.path.join(self.backup_dir, archivo)
                    
                    # Obtener info del archivo
                    stat = os.stat(ruta_completa)
                    tamaño_mb = stat.st_size / (1024 * 1024)
                    fecha_creacion = datetime.fromtimestamp(stat.st_mtime)
                    dias_antigüedad = (ahora - fecha_creacion).days
                    
                    backups.append({
                        'archivo': archivo,
                        'tamaño_mb': tamaño_mb,
                        'fecha_creacion': fecha_creacion,
                        'dias_antigüedad': dias_antigüedad,
                        'ruta': ruta_completa,
                        'restaurable': archivo.endswith('.db') or archivo.endswith('.db.gz')
                    })
            
            # Ordenar por fecha (más reciente primero)
            backups.sort(key=lambda x: x['fecha_creacion'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f'❌ Error al listar backups: {str(e)}')
            return []
    
    def limpiar_backups_antiguos(self):
        """
        ✅ NUEVA LÓGICA: Mantiene últimos 30 backups, elimina los más antiguos
        
        En lugar de eliminar por fecha, mantiene un máximo de 30 backups.
        Cuando hay más de 30, elimina los más antiguos automáticamente.
        
        Returns:
            dict: {
                'success': bool,
                'eliminados': int (cantidad),
                'mantenidos': int (cantidad de backups que quedan),
                'detalles': [list de archivos eliminados],
                'error': str (si aplica)
            }
        """
        try:
            backups = self.listar_backups()
            
            # Si hay 30 o menos, no eliminar nada
            if len(backups) <= 30:
                return {
                    'success': True,
                    'eliminados': 0,
                    'mantenidos': len(backups),
                    'detalles': [],
                    'mensaje': f'✅ {len(backups)} backups mantenidos (máximo: 30)'
                }
            
            # Ordenar por fecha (más recientes primero)
            backups_ordenados = sorted(
                backups,
                key=lambda x: x['fecha_creacion'],
                reverse=True
            )
            
            # Guardar los últimos 30
            backups_a_mantener = backups_ordenados[:30]
            ids_mantener = {b['archivo'] for b in backups_a_mantener}
            
            # Eliminar los más antiguos (fuera del top 30)
            eliminados = []
            for backup in backups_ordenados[30:]:
                try:
                    ruta = backup['ruta']
                    if os.path.exists(ruta):
                        os.remove(ruta)
                        eliminados.append(backup['archivo'])
                        logger.info(f'🗑️ Backup eliminado (antiguo): {backup["archivo"]}')
                except Exception as e:
                    logger.error(f'❌ Error eliminando {backup["archivo"]}: {str(e)}')
            
            return {
                'success': True,
                'eliminados': len(eliminados),
                'mantenidos': len(backups_a_mantener),
                'detalles': eliminados,
                'mensaje': f'✅ Se mantienen {len(backups_a_mantener)} backups. '
                          f'Se eliminaron {len(eliminados)} antiguos.'
            }
            
        except Exception as e:
            error_msg = f'❌ Error en limpieza de backups: {str(e)}'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def restaurar_backup(self, nombre_archivo):
        """
        Restaura la BD desde un backup
        
        Args:
            nombre_archivo (str): Nombre del archivo backup
            
        Returns:
            dict: {
                'success': bool,
                'mensaje': str,
                'error': str (si aplica)
            }
        """
        try:
            ruta_backup = os.path.join(self.backup_dir, nombre_archivo)
            
            if not os.path.exists(ruta_backup):
                return {
                    'success': False,
                    'error': f'Backup no encontrado: {nombre_archivo}'
                }
            
            # Si está comprimido, descomprimir a temp
            if nombre_archivo.endswith('.gz'):
                import tempfile
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, 'backup_temp.db')
                
                with gzip.open(ruta_backup, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                ruta_backup = temp_path
            
            # ✅ COMENTADO: No crear backup de seguridad automático
            # (El usuario puede hacer click en "Crear Backup Ahora" manualmente si quiere)
            # backup_actual = self.crear_backup(descripcion="Backup antes de restauración")
            
            # Restaurar
            shutil.copy2(ruta_backup, self.db_path)
            
            # Limpiar temp si aplica
            if nombre_archivo.endswith('.gz'):
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            mensaje = f'✅ Base de datos restaurada desde {nombre_archivo}'
            logger.info(mensaje)
            
            return {
                'success': True,
                'mensaje': mensaje,
                'backup_seguridad': None  # ✅ Cambiado a None
            }
            
        except Exception as e:
            error_msg = f'❌ Error al restaurar backup: {str(e)}'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas del sistema de backups
        
        Returns:
            dict: {
                'total_backups': int,
                'espacio_usado_mb': float,
                'espacio_disponible_mb': float,
                'backup_mas_reciente': str,
                'backup_mas_antiguo': str,
                'db_tamaño_mb': float,
                'proxima_limpieza': str
            }
        """
        try:
            backups = self.listar_backups()
            
            # Espacio usado en backups
            espacio_usado = sum(b['tamaño_mb'] for b in backups)
            
            # Espacio disponible en disco
            import shutil as sh
            stat = sh.disk_usage(self.backup_dir)
            espacio_disponible = stat.free / (1024 * 1024)
            
            # Tamaño BD actual
            db_tamaño = os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            
            # Backup más reciente/antiguo
            backup_reciente = backups[0]['archivo'] if backups else 'N/A'
            backup_antiguo = backups[-1]['archivo'] if backups else 'N/A'
            
            # Próxima limpieza
            proxima = datetime.now() + timedelta(days=1)
            
            return {
                'total_backups': len(backups),
                'espacio_usado_mb': espacio_usado,
                'espacio_disponible_mb': espacio_disponible,
                'backup_mas_reciente': backup_reciente,
                'backup_mas_antiguo': backup_antiguo,
                'db_tamaño_mb': db_tamaño,
                'proxima_limpieza': proxima.strftime('%Y-%m-%d %H:%M:%S'),
                'retention_days': self.retention_days
            }
            
        except Exception as e:
            logger.error(f'❌ Error obteniendo estadísticas: {str(e)}')
            return {}


# Función auxiliar para programar backups automáticos (opcional con APScheduler)
def programar_backup_automatico():
    """
    Programa backups automáticos cada día a las 3 AM
    Requiere: pip install apscheduler
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = BackgroundScheduler()
        manager = BackupLocalManager()
        
        # Programa backup diario a las 3 AM
        scheduler.add_job(
            func=lambda: manager.crear_backup('Backup automático diario'),
            trigger=CronTrigger(hour=3, minute=0),
            id='backup_diario',
            name='Backup automático diario a las 3 AM',
            replace_existing=True
        )
        
        # Programa limpieza de backups antiguos cada lunes a las 4 AM
        scheduler.add_job(
            func=lambda: manager.limpiar_backups_antiguos(),
            trigger=CronTrigger(day_of_week='mon', hour=4, minute=0),
            id='limpieza_backups',
            name='Limpieza de backups antiguos',
            replace_existing=True
        )
        
        if not scheduler.running:
            scheduler.start()
            logger.info('✅ Scheduler de backups iniciado')
        
        return True
        
    except ImportError:
        logger.warning('⚠️ APScheduler no instalado. Backups automáticos deshabilitados.')
        logger.warning('   Instalar con: pip install apscheduler')
        return False
    except Exception as e:
        logger.error(f'❌ Error configurando scheduler: {str(e)}')
        return False


if __name__ == '__main__':
    # Ejemplo de uso
    manager = BackupLocalManager()
    
    print("=== DEMO: Sistema de Backups Locales ===\n")
    
    # Crear backup
    print("1. Creando backup...")
    resultado = manager.crear_backup('Backup de prueba')
    print(f"   {resultado}\n")
    
    # Listar backups
    print("2. Backups disponibles:")
    backups = manager.listar_backups()
    for b in backups:
        print(f"   - {b['archivo']} ({b['tamaño_mb']:.2f} MB) - {b['fecha_creacion']}")
    print()
    
    # Estadísticas
    print("3. Estadísticas:")
    stats = manager.obtener_estadisticas()
    for key, value in stats.items():
        print(f"   {key}: {value}")

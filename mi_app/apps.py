from django.apps import AppConfig


class MiAppConfig(AppConfig):
    name = 'mi_app'
    
    def ready(self):
        """Inicializa el sistema de backups y auditoría cuando Django inicia"""
        # Inicializar signals de auditoría
        try:
            import mi_app.signals
        except ImportError as e:
            print(f"⚠️ Error cargando signals de auditoría: {e}")
        
        # Inicializar backups automáticos
        try:
            from backup_local_manager import programar_backup_automatico
            programar_backup_automatico()
        except ImportError:
            # APScheduler no instalado - backups manuales funcionarán igual
            pass
        except Exception as e:
            print(f"⚠️ Advertencia al inicializar backups automáticos: {e}")


from django.urls import path
from . import views_core

app_name = 'backups'

# Backup/restauracion JSON completos (ver mi_app/services/backup_service.py).
# Las rutas viejas (restaurar/descargar/eliminar/subir por id) manejaban
# archivos db.sqlite3 en el disco del servidor, que en Render no existen.
urlpatterns = [
    path('', views_core.backups_list, name='list'),
    path('crear/', views_core.backup_create, name='crear'),
    path('restaurar/', views_core.backup_restore, name='restaurar'),
]

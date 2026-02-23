from django.urls import path
from . import views_core

app_name = 'backups'

urlpatterns = [
    path('', views_core.backups_list, name='list'),
    path('crear/', views_core.backup_create, name='crear'),
    path('restaurar/<str:backup_id>/', views_core.backup_restore, name='restaurar'),
    path('descargar/<str:backup_id>/', views_core.backup_descargar, name='descargar'),
    path('eliminar/<str:backup_id>/', views_core.backup_delete, name='eliminar'),
    path('subir/', views_core.backup_upload, name='subir'),
]

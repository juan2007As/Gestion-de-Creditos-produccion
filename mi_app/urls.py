from django.urls import path, include
from . import views
from . import auth_views
from . import api_views

urlpatterns = [
    # ==================== AUTENTICACIÓN ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),
    
    # ==================== INICIO ====================
    path('', views.inicio, name='inicio'),
    path('exportaciones/', views.centro_exportaciones, name='centro_exportaciones'),
    
    # ==================== CLIENTES (CRUD) ====================
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/importados/', views.clientes_importados, name='clientes_importados'),
    path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    
    # ==================== PERFIL DE CLIENTE ====================
    path('perfil/<int:cliente_id>/', views.perfil_cliente, name='perfil_cliente'),
    path('perfil/<int:cliente_id>/prestamos/', views.mis_prestamos, name='mis_prestamos'),
    
    # ==================== PRÉSTAMOS ====================
    path('prestamos/crear/', views.crear_prestamo, name='crear_prestamo'),
    path('clientes/<int:cliente_id>/prestamos/crear/', views.crear_prestamo, name='crear_prestamo_cliente'),
    path('prestamo/<int:prestamo_id>/', views.detalles_prestamo, name='detalles_prestamo'),
    
    # ==================== CUOTAS ====================
    path('cuota/<int:cuota_id>/', views.detalles_cuota, name='detalles_cuota'),
    path('clientes/<int:cliente_id>/cuotas-pendientes/', views.cuotas_pendientes, name='cuotas_pendientes'),
    
    # ==================== PAGOS ====================
    path('pagos/buscar/', views.buscar_cliente_pago, name='buscar_cliente_pago'),
    path('cuota/<int:cuota_id>/registrar-pago/', views.registrar_pago, name='registrar_pago'),  # ✅ NUEVA: Ruta faltante para registrar_pago (FASE 2.2)
    path('clientes/<int:cliente_id>/registrar-pago/', views.registrar_pago_mejorado, name='registrar_pago_mejorado'),
    path('cuota/<int:cuota_id>/pagar/', views.pagar_cuota_especifica, name='pagar_cuota_especifica'),  # BUG #7 FIX
    
    # ==================== AJAX / API ====================
    path('api/buscar-cliente/', views.buscar_cliente, name='api_buscar_cliente'),
    path('api/clientes/', views.lista_clientes_api, name='lista_clientes_api'),
    path('api/clientes/search/', api_views.api_clientes_search, name='api_clientes_search'),
    path('api/prestamos/search/', api_views.api_prestamos_search, name='api_prestamos_search'),
    path('api/mora-diaria/', views.mora_diaria_api, name='api_mora_diaria'),  # 🆕 Mora en tiempo real
    path('api/cuota/<int:cuota_id>/mora-actual/', views.api_cuota_mora_actual, name='api_cuota_mora_actual'),  # ✅ ALTO #4: Mora real-time
    
    # ==================== REPORTES ====================
    path('reportes/clientes/', views.reporte_clientes, name='reporte_clientes'),
    path('reportes/prestamos/', views.reporte_prestamos, name='reporte_prestamos'),
    path('reportes/cuotas/', views.reporte_cuotas_completo, name='reporte_cuotas'),
    path('reportes/cuotas-vencidas/', views.reporte_cuotas_vencidas, name='reporte_cuotas_vencidas'),
    path('reportes/estadisticas/', views.reporte_estadisticas, name='reporte_estadisticas'),
    path('reportes/prestamos-rapidos/', views.reporte_prestamos_rapidos, name='reporte_prestamos_rapidos'),  # BUG #5: Reporte PRs
    path('reportes/historico-pagos/', views.historico_pagos, name='historico_pagos'),  # BUG #8: Reporte Pagos
    path('importar/excel/', views.importar_excel, name='importar_excel'),
    
    # ==================== EXPORTAR ====================
    path('exportar/clientes/', views.exportar_clientes_excel, name='exportar_clientes'),
    path('exportar/prestamos/', views.exportar_prestamos_excel, name='exportar_prestamos'),
    path('exportar/cuotas/', views.exportar_cuotas_excel, name='exportar_cuotas'),
    path('exportar/cuotas-vencidas/', views.exportar_cuotas_vencidas_excel, name='exportar_cuotas_vencidas'),
    path('exportar/estadisticas/', views.exportar_estadisticas_excel, name='exportar_estadisticas'),
    path('exportar/prestamos-rapidos/', views.exportar_prestamos_rapidos_excel, name='exportar_prestamos_rapidos'),
    path('exportar/historico-pagos/', views.exportar_historico_pagos_excel, name='exportar_historico_pagos'),
    path('exportar/reporte-general/', views.exportar_reporte_general_excel, name='exportar_reporte_general'),
    
    # ==================== PRÉSTAMOS RÁPIDOS ====================
    path('prestamo-rapido/crear/', views.crear_prestamo_rapido, name='crear_prestamo_rapido'),
    path('prestamo-rapido/<int:prestamo_id>/', views.detalle_prestamo_rapido, name='detalle_prestamo_rapido'),
    path('prestamo-rapido/listar/', views.listar_prestamos_rapidos, name='listar_prestamos_rapidos'),
    path('prestamo-rapido/<int:prestamo_id>/pagar/', views.registrar_pago_rapido_prestamo, name='registrar_pago_rapido'),
    path('prestamo-rapido/cuota/<int:cuota_id>/pagar/', views.registrar_pago_rapido, name='registrar_pago_cuota_rapida'),
    path('prestamo-rapido/<int:prestamo_id>/pagar/directo/', views.registrar_pago_rapido_directo, name='registrar_pago_rapido_directo'),
    
    # ==================== CONFIGURACIÓN ====================
    path('configuracion/', views.editar_configuracion, name='editar_configuracion'),
    
    # ==================== BACKUPS ====================
    path('backups/', include('mi_app.urls_backups')),  # 🆕 Sistema de backups locales
    
    # ==================== AUDITORÍA ====================
    path('auditoria/', views.auditoria_cambios, name='auditoria_cambios'),
    path('auditoria/<int:cambio_id>/', views.auditoria_detalle, name='auditoria_detalle'),
    path('auditoria/estadisticas/', views.auditoria_estadisticas, name='auditoria_estadisticas'),
    path('exportar/auditoria/', views.exportar_auditoria_excel, name='exportar_auditoria'),

    # ==================== ADMIN / MANTENIMIENTO ====================
    path('mantenimiento/limpieza-prestamos/', views.ejecutar_limpieza_prestamos, name='limpieza_prestamos'),
    path('mantenimiento/auto-tagging-lista-negra/', views.auto_tagging_lista_negra, name='auto_tagging_lista_negra'),
    path('mantenimiento/auto-tagging-etiquetas/', views.auto_tagging_etiquetas, name='auto_tagging_etiquetas'),
    
    # ==================== REPORTES DE INTERÉS ====================
    path('reportes/interes-mensual/', views.reporte_interes_mensual, name='reporte_interes_mensual'),
    
    # ==================== EXPORTAR ====================
    path('exportar/lista-negra/', views.exportar_lista_negra_excel, name='exportar_lista_negra'),
    path('exportar/reporte-interes/', views.exportar_reporte_interes_excel, name='exportar_reporte_interes'),
    
    # ==================== BACKUP RÁPIDO (Nuevo) ====================
    path('backup/generar-rapido/', views.backup_rapido_generar, name='backup_rapido_generar'),
    path('backup/descargar/', views.backup_rapido_descargar, name='backup_rapido_descargar'),
    path('backup/descargar/<int:backup_id>/', views.backup_rapido_descargar, name='backup_rapido_descargar_id'),
    path('backup/enviar-correo/', views.backup_rapido_correo, name='backup_rapido_correo'),
]
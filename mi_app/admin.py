from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Prestamo, Cuota, Pago, Configuracion, PrestamoRapido, PagoPrestamoRapido, Rol, Permiso, RolPermiso, UsuarioProfile, AuditLog

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def formato_colombiano_display(valor):
    """
    Convierte un float a formato moneda colombiana: $1.000,00
    Usado en el admin para mostrar dinero correctamente
    """
    try:
        valor_float = float(valor)
        # Formato: miles con punto, decimales con coma
        formateado = f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"${formateado}"
    except (ValueError, TypeError):
        return "$0,00"

# ============================================================================
# INLINE CLASSES
# ============================================================================

class CuotaInline(admin.TabularInline):
    """Inline editing for loan quotes in loan detail view"""
    model = Cuota
    extra = 0
    fields = ['numero_cuota', 'fecha_pago_esperada', 'monto_original', 'monto_pendiente', 'interes_normal', 'pagado']
    readonly_fields = []



# ============================================================================
# CLIENTE ADMIN
# ============================================================================

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Enhanced Cliente administration with advanced filtering and search"""
    
    list_display = ['nombre_display', 'cedula_display', 'celular_display', 'email_display', 'estado_badge', 'total_prestamos', 'fecha_creacion']
    search_fields = ['nombre', 'cedula', 'celular', 'email']
    list_filter = ['estado', 'fecha_creacion']
    ordering = ['-fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ['fecha_creacion', 'fecha_ultima_modificacion']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'cedula', 'celular', 'email')
        }),
        ('Estado', {
            'fields': ('estado', 'rating')
        }),
        ('Finanzas', {
            'fields': ('total_prestado',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_ultima_modificacion', 'notas'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_display(self, obj):
        return obj.nombre.upper()
    nombre_display.short_description = 'Cliente'
    
    def cedula_display(self, obj):
        return obj.cedula or 'N/A'
    cedula_display.short_description = 'Cédula'
    
    def celular_display(self, obj):
        return obj.celular or 'N/A'
    celular_display.short_description = 'Celular'
    
    def email_display(self, obj):
        return obj.email or 'N/A'
    email_display.short_description = 'Email'
    
    def estado_badge(self, obj):
        """Display client status with color coding"""
        colors = {
            'activo': '#28a745',
            'inactivo': '#dc3545',
        }
        color = colors.get(obj.estado, '#6c757d')
        estado_text = 'Activo' if obj.estado == 'activo' else 'Inactivo'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            estado_text
        )
    estado_badge.short_description = 'Estado'
    
    def total_prestamos(self, obj):
        """Count total loans for this client"""
        return obj.prestamo_set.count()
    total_prestamos.short_description = 'Préstamos'


# ============================================================================
# PRESTAMO ADMIN
# ============================================================================

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    """Enhanced Prestamo administration with inline cuotas and payments"""
    
    list_display = ['id_prestamo', 'cliente_name', 'monto_display', 'estado_badge', 'fecha_inicio', 'tipo_pago', 'progreso_cuotas']
    search_fields = ['cliente__nombre', 'cliente__cedula', 'id']
    list_filter = ['estado', 'fecha_creacion', 'tipo_pago']
    ordering = ['-fecha_creacion']
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ['fecha_creacion', 'fecha_ultima_modificacion']
    inlines = [CuotaInline]
    
    fieldsets = (
        ('Información del Préstamo', {
            'fields': ('cliente', 'monto_total', 'interes_porcentaje', 'tipo_pago')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada')
        }),
        ('Configuración', {
            'fields': ('calendario_pagos', 'estado')
        }),
        ('Auditoría', {
            'fields': ('notas_admin', 'fecha_creacion', 'fecha_ultima_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def id_prestamo(self, obj):
        return f'Préstamo #{obj.id}'
    id_prestamo.short_description = 'ID'
    
    def cliente_name(self, obj):
        return obj.cliente.nombre.upper()
    cliente_name.short_description = 'Cliente'
    
    def monto_display(self, obj):
        return format_html('{}', formato_colombiano_display(obj.monto_total))
    monto_display.short_description = 'Monto'
    
    def estado_badge(self, obj):
        """Display loan status with color coding"""
        colors = {
            'ACTIVO': '#007bff',
            'COMPLETADO': '#28a745',
            'BORRADOR': '#6c757d'
        }
        color = colors.get(obj.estado, '#6c757d')
        estado_text = obj.get_estado_display() if hasattr(obj, 'get_estado_display') else obj.estado.title()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            estado_text
        )
    estado_badge.short_description = 'Estado'
    
    def progreso_cuotas(self, obj):
        """Display payment progress as percentage"""
        cuotas = obj.cuotas.all()
        if not cuotas:
            return 'N/A'
        
        pagadas = cuotas.filter(pagado=True).count()
        total = cuotas.count()
        porcentaje = (pagadas / total * 100) if total > 0 else 0
        
        return format_html(
            '<div style="width: 80px; background: #e9ecef; border-radius: 3px; display: inline-block; height: 18px;"><div style="width: {}%; background: #28a745; height: 100%; border-radius: 3px;"></div></div> {:.0f}%',
            porcentaje, porcentaje
        )
    progreso_cuotas.short_description = 'Progreso'


# ============================================================================
# CUOTA ADMIN
# ============================================================================

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    """Enhanced Cuota administration with payment details"""
    
    list_display = ['numero_display', 'prestamo_info', 'fecha_pago_esperada', 'monto_display', 'estado_badge', 'pagado_display']
    search_fields = ['prestamo__id', 'prestamo__cliente__nombre']
    list_filter = ['pagado', 'fecha_pago_esperada']
    ordering = ['prestamo', 'numero_cuota']
    
    fieldsets = (
        ('Información de Cuota', {
            'fields': ('prestamo', 'numero_cuota', 'fecha_pago_esperada', 'monto_original')
        }),
        ('Desglose de Pago', {
            'fields': ('monto_pendiente', 'interes_normal', 'interes_mora_acumulado', 'pagado')
        }),
        ('Tracking de Pagos', {
            'fields': ('monto_pagado_principal', 'monto_pagado_interes', 'monto_pagado_mora', 'fecha_pago_real'),
            'classes': ('collapse',)
        }),
    )
    
    def numero_display(self, obj):
        return f'Cuota #{obj.numero_cuota}'
    numero_display.short_description = 'Cuota'
    
    def prestamo_info(self, obj):
        return f"Préstamo #{obj.prestamo.id}"
    prestamo_info.short_description = 'Préstamo'
    
    def monto_display(self, obj):
        return format_html('{}', formato_colombiano_display(obj.monto_original))
    monto_display.short_description = 'Monto'
    
    def estado_badge(self, obj):
        """Display quote status with color coding"""
        if obj.pagado:
            estado = 'PAGADA'
            color = '#28a745'
        else:
            estado = 'PENDIENTE'
            color = '#dc3545'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            estado
        )
    estado_badge.short_description = 'Estado'
    
    def pagado_display(self, obj):
        total_pagado = float(obj.monto_pagado_principal) + float(obj.monto_pagado_interes) + float(obj.monto_pagado_mora)
        porcentaje = (total_pagado / float(obj.monto_original) * 100) if float(obj.monto_original) > 0 else 0
        return format_html(
            '${:,.2f} / ${:,.2f} ({:.1f}%)',
            total_pagado,
            float(obj.monto_original),
            porcentaje
        )
    pagado_display.short_description = 'Pagado'


# ============================================================================
# PAGO ADMIN
# ============================================================================

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """Enhanced Pago administration with detailed filtering"""
    
    list_display = ['id_pago', 'cuota_info', 'fecha_pago', 'monto_display', 'desglose_display']
    search_fields = ['cuota__prestamo__id', 'cuota__prestamo__cliente__nombre']
    list_filter = ['fecha_pago']
    ordering = ['-fecha_pago']
    date_hierarchy = 'fecha_pago'
    readonly_fields = ['cuota_info_detail', 'fecha_pago']
    
    fieldsets = (
        ('Información de Pago', {
            'fields': ('cuota', 'cuota_info_detail', 'fecha_pago')
        }),
        ('Montos', {
            'fields': ('monto_pagado', 'monto_principal', 'monto_interes', 'monto_mora')
        }),
        ('Auditoría', {
            'fields': ('usuario_registra', 'referencia', 'notas'),
            'classes': ('collapse',)
        }),
    )
    
    def id_pago(self, obj):
        return f'Pago #{obj.id}'
    id_pago.short_description = 'ID'
    
    def cuota_info(self, obj):
        return f"Cuota #{obj.cuota.numero_cuota}"
    cuota_info.short_description = 'Cuota'
    
    def monto_display(self, obj):
        return format_html('{}', formato_colombiano_display(obj.monto_pagado))
    monto_display.short_description = 'Monto Total'
    
    def desglose_display(self, obj):
        return format_html(
            'Prin: {} | Int: {} | Mora: {}',
            formato_colombiano_display(obj.monto_principal),
            formato_colombiano_display(obj.monto_interes),
            formato_colombiano_display(obj.monto_mora)
        )
    desglose_display.short_description = 'Desglose'
    
    def cuota_info_detail(self, obj):
        """Display detailed quote information"""
        return format_html(
            '<strong>Cliente:</strong> {} | <strong>Préstamo:</strong> #{} | <strong>Cuota:</strong> #{} | <strong>Monto Cuota:</strong> ${:,.2f}',
            obj.cuota.prestamo.cliente.nombre,
            obj.cuota.prestamo.id,
            obj.cuota.numero_cuota,
            float(obj.cuota.monto_original)
        )
    cuota_info_detail.short_description = 'Información de Cuota'


# ============================================================================
# PRÉSTAMOS RÁPIDOS ADMIN
# ============================================================================

class PagoPrestamoRapidoInline(admin.TabularInline):
    """Inline for payments in quick loans"""
    model = PagoPrestamoRapido
    extra = 0
    fields = ['monto_pagado', 'fecha_pago', 'usuario_registra', 'referencia']
    readonly_fields = ['fecha_pago']


@admin.register(PrestamoRapido)
class PrestamoRapidoAdmin(admin.ModelAdmin):
    """Administration for quick loans"""
    
    list_display = ['id_display', 'cliente_display', 'monto_display', 'interes_display', 'estado_badge', 'porcentaje_pagado_display', 'fecha_solicitud_display']
    search_fields = ['cliente__nombre', 'cliente__cedula']
    list_filter = ['estado', 'fecha_solicitud']
    ordering = ['-fecha_solicitud']
    date_hierarchy = 'fecha_solicitud'
    readonly_fields = ['fecha_solicitud', 'fecha_ultima_modificacion', 'porcentaje_pagado_display_detail', 'saldo_display']
    inlines = [PagoPrestamoRapidoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cliente', 'monto', 'interes_porcentaje', 'fecha_vencimiento')
        }),
        ('Estado del Pago', {
            'fields': ('estado', 'monto_pagado', 'saldo_display', 'porcentaje_pagado_display_detail')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Auditoría', {
            'fields': ('fecha_solicitud', 'fecha_ultima_modificacion', 'fecha_pago_real'),
            'classes': ('collapse',)
        }),
    )
    
    def id_display(self, obj):
        return f'#{obj.id}'
    id_display.short_description = 'ID'
    
    def cliente_display(self, obj):
        return obj.cliente.nombre
    cliente_display.short_description = 'Cliente'
    
    def monto_display(self, obj):
        return format_html('{}', formato_colombiano_display(obj.monto))
    monto_display.short_description = 'Monto'
    
    def interes_display(self, obj):
        return f'{obj.interes_porcentaje}%'
    interes_display.short_description = 'Interés'
    
    def estado_badge(self, obj):
        colors = {
            'PENDIENTE': '#ffc107',
            'PARCIALMENTE_PAGADO': '#0dcaf0',
            'PAGADO': '#198754',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def porcentaje_pagado_display(self, obj):
        porcentaje = round(obj.porcentaje_pagado, 1)
        color = '#198754' if porcentaje == 100 else '#0dcaf0' if porcentaje > 0 else '#ffc107'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            porcentaje
        )
    porcentaje_pagado_display.short_description = 'Pagado'
    
    def porcentaje_pagado_display_detail(self, obj):
        return f'{round(obj.porcentaje_pagado, 1)}%'
    porcentaje_pagado_display_detail.short_description = 'Porcentaje Pagado'
    
    def saldo_display(self, obj):
        return format_html('{}', formato_colombiano_display(obj.saldo_pendiente))
    saldo_display.short_description = 'Saldo Pendiente'
    
    def fecha_solicitud_display(self, obj):
        return obj.fecha_solicitud.strftime('%d/%m/%Y')
    fecha_solicitud_display.short_description = 'Solicitud'


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    """Administration for system configuration"""
    
    list_display = ['tasa_interes_normal_display', 'tasa_interes_rapido_display', 'tasa_mora_display', 'fecha_actualizacion_display']
    readonly_fields = ['fecha_actualizacion']
    
    fieldsets = (
        ('Tasas de Interés', {
            'fields': ('tasa_interes_prestamo_normal', 'tasa_interes_prestamo_rapido')
        }),
        ('Mora', {
            'fields': ('tasa_mora_diaria',)
        }),
        ('Auditoría', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )
    
    def tasa_interes_normal_display(self, obj):
        return f'{obj.tasa_interes_prestamo_normal}%'
    tasa_interes_normal_display.short_description = 'Interés Normal'
    
    def tasa_interes_rapido_display(self, obj):
        return f'{obj.tasa_interes_prestamo_rapido}%'
    tasa_interes_rapido_display.short_description = 'Interés Rápido'
    
    def tasa_mora_display(self, obj):
        return format_html('${:,.2f}', float(obj.tasa_mora_diaria))
    tasa_mora_display.short_description = 'Mora Diaria'
    
    def fecha_actualizacion_display(self, obj):
        return obj.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')
    fecha_actualizacion_display.short_description = 'Última Actualización'
    
    def has_add_permission(self, request):
        """Evitar agregar más configuraciones (singleton)"""
        return not Configuracion.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Evitar eliminar la configuración"""
        return False


# ============================================================================
# ADMIN PARA ROLES Y PERMISOS
# ============================================================================

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Admin para gestionar roles del sistema"""
    list_display = ['nombre', 'descripcion_corta', 'permisos_count', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'activo')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def permisos_count(self, obj):
        count = obj.rolpermiso_set.count()
        return format_html('<strong>{}</strong> permisos', count)
    permisos_count.short_description = 'Permisos Asignados'


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    """Admin para gestionar permisos del sistema"""
    list_display = ['codigo', 'descripcion_corta', 'categoria', 'activo', 'roles_count']
    list_filter = ['categoria', 'activo', 'fecha_creacion']
    search_fields = ['codigo', 'descripcion']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'categoria', 'activo')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def roles_count(self, obj):
        count = obj.en_roles.count()
        if count == 0:
            return format_html('<span style="color: red;">No asignado</span>')
        return format_html('<strong>{}</strong> roles', count)
    roles_count.short_description = 'En Roles'


class RolPermisoInline(admin.TabularInline):
    """Inline para asignar permisos a un rol"""
    model = RolPermiso
    extra = 1
    fields = ['permiso', 'fecha_asignacion']
    readonly_fields = ['fecha_asignacion']


@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    """Admin para gestionar asignación de permisos a roles"""
    list_display = ['rol', 'permiso', 'fecha_asignacion']
    list_filter = ['rol', 'permiso__categoria', 'fecha_asignacion']
    search_fields = ['rol__nombre', 'permiso__codigo']
    readonly_fields = ['fecha_asignacion']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('rol', 'permiso')
        }),
        ('Auditoría', {
            'fields': ('fecha_asignacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsuarioProfile)
class UsuarioProfileAdmin(admin.ModelAdmin):
    """Admin para gestionar perfiles de usuario"""
    list_display = ['usuario_full', 'rol_badge', 'activo', 'fecha_creacion']
    list_filter = ['rol', 'activo', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario__email']
    readonly_fields = ['usuario', 'fecha_creacion', 'fecha_ultima_modificacion', 'permisos_display']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario', 'rol')
        }),
        ('Estado', {
            'fields': ('activo', 'notas')
        }),
        ('Permisos Actuales', {
            'fields': ('permisos_display',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_ultima_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def usuario_full(self, obj):
        full_name = obj.usuario.get_full_name()
        return format_html(
            '<strong>{}</strong> ({}) - {}',
            full_name or obj.usuario.username,
            obj.usuario.username,
            obj.usuario.email
        )
    usuario_full.short_description = 'Usuario'
    
    def rol_badge(self, obj):
        if not obj.rol:
            return format_html('<span style="color: red;">Sin Rol</span>')
        
        colors = {
            'ADMIN': '#dc3545',      # Rojo
            'GERENTE': '#007bff',    # Azul
            'OPERARIO': '#28a745',   # Verde
        }
        color = colors.get(obj.rol.nombre, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.rol.get_nombre_display()
        )
    rol_badge.short_description = 'Rol'
    
    def permisos_display(self, obj):
        permisos = obj.permisos
        if not permisos:
            return "Sin permisos"
        html = '<ul style="list-style-type: none; padding: 0;">'
        for permiso in sorted(permisos):
            html += f'<li style="padding: 5px 0;">✓ <code>{permiso}</code></li>'
        html += '</ul>'
        return format_html(html)
    permisos_display.short_description = 'Permisos Asignados'


# ============================================================================
# AUDIT LOG ADMIN
# ============================================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Vista de administración para logs de auditoría - SOLO LECTURA"""
    
    list_display = ['timestamp_display', 'usuario_display', 'accion_badge', 'modelo_display', 'objeto_id', 'ip_address']
    list_filter = ['accion', 'modelo', 'timestamp', 'usuario']
    search_fields = ['descripcion', 'usuario__username', 'objeto_representacion', 'ip_address']
    readonly_fields = ['timestamp', 'usuario', 'accion', 'modelo', 'objeto_id', 'objeto_representacion', 'cambios_display', 'ip_address', 'descripcion', 'cambios_legibles_display']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    # Hacer que sea de solo lectura
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('timestamp', 'usuario_display', 'accion', 'modelo', 'objeto_id')
        }),
        ('Objeto Afectado', {
            'fields': ('objeto_representacion', 'ip_address')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Cambios Registrados', {
            'fields': ('cambios_display', 'cambios_legibles_display'),
            'classes': ('collapse',)
        }),
    )
    
    def timestamp_display(self, obj):
        """Muestra timestamp formateado"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Fecha/Hora'
    
    def usuario_display(self, obj):
        """Muestra usuario o SISTEMA"""
        if obj.usuario:
            return format_html(
                '<strong>{}</strong> <br/><small style="color: #666;">{}</small>',
                obj.usuario.username,
                obj.usuario.get_full_name() or obj.usuario.email
            )
        return format_html('<span style="color: #666;">SISTEMA</span>')
    usuario_display.short_description = 'Usuario'
    
    def accion_badge(self, obj):
        """Muestra acción con color"""
        colors = {
            'CREATE': '#28a745',    # Verde
            'UPDATE': '#007bff',    # Azul
            'DELETE': '#dc3545',    # Rojo
            'RESTORE': '#ffc107',   # Amarillo
        }
        color = colors.get(obj.accion, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.accion
        )
    accion_badge.short_description = 'Acción'
    
    def modelo_display(self, obj):
        """Muestra modelo"""
        return format_html(
            '<strong>{}</strong> <small style="color: #666;">#{}</small>',
            obj.modelo,
            obj.objeto_id
        )
    modelo_display.short_description = 'Modelo'
    
    def cambios_display(self, obj):
        """Muestra cambios en formato JSON"""
        if not obj.cambios:
            return format_html('<span style="color: #999;">Sin cambios</span>')
        
        import json
        cambios_formatted = json.dumps(obj.cambios, indent=2, ensure_ascii=False)
        return format_html(
            '<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto;">{}</pre>',
            cambios_formatted
        )
    cambios_display.short_description = 'Cambios (JSON)'
    
    def cambios_legibles_display(self, obj):
        """Muestra cambios en formato legible"""
        cambios_legibles = obj.get_cambios_legibles()
        if not cambios_legibles or cambios_legibles == "Sin cambios":
            return format_html('<span style="color: #999;">Sin cambios</span>')
        
        return format_html(
            '<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px; white-space: pre-wrap; word-wrap: break-word;">{}</pre>',
            cambios_legibles
        )
    cambios_legibles_display.short_description = 'Cambios (Legible)'


# ============================================================================
# ADMIN CONFIG
# ============================================================================

admin.site.site_header = "Administración - Sistema de Préstamos"
admin.site.site_title = "Admin Préstamos"
admin.site.index_title = "Bienvenido al Panel de Administración"
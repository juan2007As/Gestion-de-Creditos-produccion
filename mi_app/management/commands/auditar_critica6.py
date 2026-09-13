"""
CRÍTICA #6: AUDIT MANAGEMENT COMMAND
Herramienta para consultar, filtrar y reportar logs de auditoría
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
import json
from tabulate import tabulate

from mi_app.models import AuditLog
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Consulta y reporta logs de auditoría con múltiples filtros'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Filtrar por usuario (nombre de usuario)'
        )
        
        parser.add_argument(
            '--modelo',
            type=str,
            help='Filtrar por modelo (Cliente, Prestamo, Cuota, Pago, etc.)'
        )
        
        parser.add_argument(
            '--accion',
            type=str,
            help='Filtrar por acción (CREATE, UPDATE, DELETE, RESTORE)'
        )
        
        parser.add_argument(
            '--dias',
            type=int,
            default=7,
            help='Últimas N días (default: 7)'
        )
        
        parser.add_argument(
            '--fecha-inicio',
            type=str,
            help='Fecha inicio (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--fecha-fin',
            type=str,
            help='Fecha fin (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--objeto-id',
            type=int,
            help='Filtrar por ID de objeto'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Máximo número de registros (default: 50)'
        )
        
        parser.add_argument(
            '--formato',
            type=str,
            choices=['tabla', 'json', 'detallado'],
            default='tabla',
            help='Formato de salida'
        )
        
        parser.add_argument(
            '--resumen',
            action='store_true',
            help='Mostrar resumen estadístico'
        )
        
        parser.add_argument(
            '--usuario-sospechoso',
            type=int,
            help='Detectar actividad sospechosa de un usuario (búsqueda en últimas 24h)'
        )
    
    def handle(self, *args, **options):
        queryset = AuditLog.objects.all()
        
        # Filtrar por rango de fechas
        if options['fecha_inicio'] and options['fecha_fin']:
            try:
                from datetime import datetime
                inicio = datetime.strptime(options['fecha_inicio'], '%Y-%m-%d')
                fin = datetime.strptime(options['fecha_fin'], '%Y-%m-%d')
                queryset = queryset.filter(timestamp__range=[inicio, fin])
            except ValueError:
                raise CommandError('Formato de fecha inválido. Usar YYYY-MM-DD')
        else:
            # Default: últimos N días
            dias = options.get('dias', 7)
            fecha_limite = timezone.now() - timedelta(days=dias)
            queryset = queryset.filter(timestamp__gte=fecha_limite)
        
        # Filtro por usuario
        if options['usuario']:
            try:
                usuario = User.objects.get(username=options['usuario'])
                queryset = queryset.filter(usuario=usuario)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Usuario "{options["usuario"]}" no encontrado'))
        
        # Filtro por modelo
        if options['modelo']:
            queryset = queryset.filter(modelo=options['modelo'])
        
        # Filtro por acción
        if options['accion']:
            queryset = queryset.filter(accion=options['accion'])
        
        # Filtro por objeto_id
        if options['objeto_id']:
            queryset = queryset.filter(objeto_id=options['objeto_id'])
        
        # Ordenar por timestamp descendente
        queryset = queryset.order_by('-timestamp')
        
        # Limitar resultados
        limit = options.get('limit', 50)
        queryset = queryset[:limit]
        
        # Mostrar resultados
        if options['resumen']:
            self._mostrar_resumen(queryset)
        elif options['usuario_sospechoso']:
            self._detectar_actividad_sospechosa(options['usuario_sospechoso'])
        else:
            self._mostrar_resultados(queryset, options['formato'])
    
    def _mostrar_resultados(self, queryset, formato):
        """Muestra los resultados en el formato especificado"""
        
        if formato == 'json':
            self._mostrar_json(queryset)
        elif formato == 'detallado':
            self._mostrar_detallado(queryset)
        else:
            self._mostrar_tabla(queryset)
    
    def _mostrar_tabla(self, queryset):
        """Muestra los resultados en formato tabla"""
        
        datos = []
        for log in queryset:
            usuario = log.usuario.username if log.usuario else "SISTEMA"
            cambios = "Sí" if log.cambios else "No"
            datos.append([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                usuario,
                log.accion,
                log.modelo,
                log.objeto_id,
                cambios,
                log.descripcion[:50] + "..." if len(log.descripcion) > 50 else log.descripcion
            ])
        
        headers = ['Fecha/Hora', 'Usuario', 'Acción', 'Modelo', 'ID', 'Cambios', 'Descripción']
        
        if datos:
            self.stdout.write(self.style.SUCCESS('\n╔══════════════════════════════════════════════════════════════════════════════╗'))
            self.stdout.write(self.style.SUCCESS('║                        📊 LOGS DE AUDITORÍA                                  ║'))
            self.stdout.write(self.style.SUCCESS('╚══════════════════════════════════════════════════════════════════════════════╝\n'))
            self.stdout.write(tabulate(datos, headers=headers, tablefmt='grid'))
            self.stdout.write(self.style.SUCCESS(f'\n✅ Total: {len(datos)} registros encontrados\n'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  No se encontraron registros de auditoría\n'))
    
    def _mostrar_json(self, queryset):
        """Muestra los resultados en formato JSON"""
        
        logs_json = []
        for log in queryset:
            logs_json.append({
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'usuario': log.usuario.username if log.usuario else "SISTEMA",
                'accion': log.accion,
                'modelo': log.modelo,
                'objeto_id': log.objeto_id,
                'objeto_representacion': log.objeto_representacion,
                'cambios': log.cambios,
                'ip_address': log.ip_address,
                'descripcion': log.descripcion,
            })
        
        self.stdout.write(json.dumps(logs_json, indent=2, default=str))
    
    def _mostrar_detallado(self, queryset):
        """Muestra los resultados en formato detallado"""
        
        self.stdout.write(self.style.SUCCESS('\n╔══════════════════════════════════════════════════════════════════════════════╗'))
        self.stdout.write(self.style.SUCCESS('║                   📋 REPORTE DETALLADO DE AUDITORÍA                            ║'))
        self.stdout.write(self.style.SUCCESS('╚══════════════════════════════════════════════════════════════════════════════╝\n'))
        
        for i, log in enumerate(queryset, 1):
            usuario = log.usuario.username if log.usuario else "SISTEMA"
            
            self.stdout.write(f'\n{i}. ─────────────────────────────────────────')
            self.stdout.write(self.style.HTTP_INFO(f'   Timestamp: {log.timestamp}'))
            self.stdout.write(self.style.HTTP_INFO(f'   Usuario: {usuario}'))
            self.stdout.write(self.style.HTTP_INFO(f'   Acción: {log.accion}'))
            self.stdout.write(self.style.HTTP_INFO(f'   Modelo: {log.modelo}'))
            self.stdout.write(self.style.HTTP_INFO(f'   Objeto ID: {log.objeto_id}'))
            self.stdout.write(self.style.HTTP_INFO(f'   IP Address: {log.ip_address}'))
            self.stdout.write(self.style.HTTP_INFO(f'   Descripción: {log.descripcion}'))
            
            if log.cambios:
                self.stdout.write(self.style.WARNING(f'   Cambios: '))
                cambios_legibles = log.get_cambios_legibles()
                self.stdout.write(f'   {cambios_legibles}')
            
            if log.objeto_representacion:
                self.stdout.write(self.style.SUCCESS(f'   Objeto: {log.objeto_representacion}'))
        
        self.stdout.write(f'\n\n✅ Total: {queryset.count()} registros encontrados\n')
    
    def _mostrar_resumen(self, queryset):
        """Muestra un resumen estadístico"""
        
        self.stdout.write(self.style.SUCCESS('\n╔══════════════════════════════════════════════════════════════════════════════╗'))
        self.stdout.write(self.style.SUCCESS('║                       📊 RESUMEN DE AUDITORÍA                                 ║'))
        self.stdout.write(self.style.SUCCESS('╚══════════════════════════════════════════════════════════════════════════════╝\n'))
        
        # Por acción
        acciones = {}
        usuarios = {}
        modelos = {}
        
        for log in queryset:
            acciones[log.accion] = acciones.get(log.accion, 0) + 1
            
            usuario = log.usuario.username if log.usuario else "SISTEMA"
            usuarios[usuario] = usuarios.get(usuario, 0) + 1
            
            modelos[log.modelo] = modelos.get(log.modelo, 0) + 1
        
        self.stdout.write(self.style.HTTP_SUCCESS('📌 Acciones:'))
        for accion, count in sorted(acciones.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f'   {accion}: {count}')
        
        self.stdout.write(self.style.HTTP_SUCCESS('\n👤 Usuarios Activos:'))
        for usuario, count in sorted(usuarios.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f'   {usuario}: {count}')
        
        self.stdout.write(self.style.HTTP_SUCCESS('\n📚 Modelos:'))
        for modelo, count in sorted(modelos.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f'   {modelo}: {count}')
        
        self.stdout.write(self.style.SUCCESS(f'\n\n✅ Total: {queryset.count()} registros\n'))
    
    def _detectar_actividad_sospechosa(self, usuario_id):
        """Detecta patrones sospechosos de actividad"""
        
        # Buscar en últimas 24 horas
        hace_24h = timezone.now() - timedelta(hours=24)
        
        try:
            usuario = User.objects.get(id=usuario_id)
        except User.DoesNotExist:
            raise CommandError(f'Usuario con ID {usuario_id} no encontrado')
        
        logs = AuditLog.objects.filter(
            usuario=usuario,
            timestamp__gte=hace_24h
        ).order_by('-timestamp')
        
        self.stdout.write(self.style.SUCCESS(f'\n🔍 ANÁLISIS DE ACTIVIDAD SOSPECHOSA: {usuario.username}\n'))
        
        # Contar operaciones por tipo
        deletes = logs.filter(accion='DELETE').count()
        updates = logs.filter(accion='UPDATE').count()
        creates = logs.filter(accion='CREATE').count()
        
        self.stdout.write(f'   Última 24 horas:')
        self.stdout.write(f'   - DELETE: {deletes}')
        self.stdout.write(f'   - UPDATE: {updates}')
        self.stdout.write(f'   - CREATE: {creates}')
        
        # Detección de patrones sospechosos
        alertas = []
        
        if deletes > 10:
            alertas.append(f'⚠️  ALTO: {deletes} operaciones DELETE en 24h')
        
        if updates > 50:
            alertas.append(f'⚠️  MEDIO: {updates} operaciones UPDATE en 24h')
        
        # Múltiples IPs desde mismo usuario
        ips = logs.values('ip_address').distinct().count()
        if ips > 3:
            alertas.append(f'⚠️  MEDIO: {ips} direcciones IP diferentes')
        
        if alertas:
            self.stdout.write(self.style.WARNING('\n🚨 ALERTAS DETECTADAS:\n'))
            for alerta in alertas:
                self.stdout.write(f'   {alerta}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ No se detectó actividad sospechosa\n'))
        
        # Mostrar últimas 10 operaciones
        self.stdout.write(self.style.HTTP_INFO('\n📋 Últimas 10 operaciones:\n'))
        
        datos = []
        for log in logs[:10]:
            datos.append([
                log.timestamp.strftime('%H:%M:%S'),
                log.accion,
                log.modelo,
                log.ip_address,
                log.descripcion[:40] + "..." if len(log.descripcion) > 40 else log.descripcion
            ])
        
        headers = ['Hora', 'Acción', 'Modelo', 'IP', 'Descripción']
        self.stdout.write(tabulate(datos, headers=headers, tablefmt='grid'))
        self.stdout.write()

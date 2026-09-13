from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mi_app.models import Cliente, ClienteScoring
from datetime import datetime
import sys

class Command(BaseCommand):
    help = 'Calcula y actualiza automáticamente las etiquetas de todos los clientes (BUENO/MEDIO/MALO)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la ejecución sin hacer cambios reales'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra detalles de cada cliente procesado'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.WARNING('\n' + '='*70))
        self.stdout.write(self.style.WARNING('AUTO-TAGGING DE ETIQUETAS DE CLIENTES'))
        self.stdout.write(self.style.WARNING('='*70))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('🔍 MODO DRY-RUN (sin cambios reales)'))
        
        # Estadísticas
        stats = {
            'total_procesados': 0,
            'cambios_realizados': 0,
            'por_etiqueta': {
                'BUENO': 0,
                'MEDIO': 0,
                'MALO': 0,
                'SIN_HISTORIAL': 0,
            },
            'cambios_por_tipo': {
                'BUENO_a_MEDIO': 0,
                'BUENO_a_MALO': 0,
                'MEDIO_a_BUENO': 0,
                'MEDIO_a_MALO': 0,
                'MALO_a_BUENO': 0,
                'MALO_a_MEDIO': 0,
                'SIN_HISTORIAL_cambios': 0,
            },
            'errores': 0,
        }
        
        # Procesar todos los clientes
        clientes = Cliente.objects.all().order_by('nombre')
        
        self.stdout.write(f'\n📊 Procesando {clientes.count()} clientes...\n')
        
        for cliente in clientes:
            stats['total_procesados'] += 1
            
            try:
                # Calcular nueva etiqueta
                etiqueta_nueva = cliente.calcular_etiqueta()
                etiqueta_vieja = cliente.etiqueta_cliente
                
                # Registrar destino
                stats['por_etiqueta'][etiqueta_nueva] += 1
                
                # Detectar cambios
                if etiqueta_vieja != etiqueta_nueva:
                    stats['cambios_realizados'] += 1
                    
                    # Registrar tipo de cambio
                    cambio_key = f'{etiqueta_vieja}_a_{etiqueta_nueva}'
                    if cambio_key.startswith('SIN_HISTORIAL'):
                        stats['cambios_por_tipo']['SIN_HISTORIAL_cambios'] += 1
                    elif cambio_key in stats['cambios_por_tipo']:
                        stats['cambios_por_tipo'][cambio_key] += 1
                    
                    # Mostrar detalle si verbose
                    if verbose:
                        color = self.get_color_etiqueta(etiqueta_nueva)
                        reset = '\033[0m'  # Código ANSI para resetear color
                        self.stdout.write(
                            f'  {color}{cliente.nombre:30} '
                            f'{etiqueta_vieja:15} → {etiqueta_nueva:15} '
                            f'(Cumpl: {cliente.tasa_cumplimiento:.1f}%, Mora: {cliente.dias_mora_promedio:.1f}d){reset}'
                        )
                    
                    # Aplicar cambio si no es dry-run
                    if not dry_run:
                        cliente.etiqueta_cliente = etiqueta_nueva
                        cliente.save(update_fields=['etiqueta_cliente'])
                        
            except Exception as e:
                stats['errores'] += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error procesando {cliente.nombre}: {str(e)}')
                )
        
        # ===== RESUMEN FINAL =====
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('📋 RESUMEN DE RESULTADOS'))
        self.stdout.write('='*70)
        
        self.stdout.write(f'\n📊 Estadísticas Generales:')
        self.stdout.write(f'   Total procesados: {stats["total_procesados"]}')
        self.stdout.write(f'   Cambios realizados: {stats["cambios_realizados"]}')
        self.stdout.write(f'   Errores: {stats["errores"]}')
        
        self.stdout.write(f'\n🏷️  Distribución Final de Etiquetas:')
        for etiqueta, cantidad in sorted(stats['por_etiqueta'].items()):
            color = self.get_color_etiqueta(etiqueta)
            reset = '\033[0m'  # Código ANSI para resetear color
            porcentaje = (cantidad / stats['total_procesados'] * 100) if stats['total_procesados'] > 0 else 0
            self.stdout.write(f'   {color}{etiqueta:15}{reset}: {cantidad:3d} ({porcentaje:5.1f}%)')
        
        if stats['cambios_realizados'] > 0:
            self.stdout.write(f'\n🔄 Cambios de Clasificación:')
            for cambio, cantidad in sorted(stats['cambios_por_tipo'].items()):
                if cantidad > 0:
                    self.stdout.write(f'   {cambio}: {cantidad}')
        
        # Modo de ejecución
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  MODO DRY-RUN: Los cambios NO fueron aplicados.'))
            self.stdout.write(self.style.WARNING('   Ejecuta sin --dry-run para aplicar los cambios.'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Todos los cambios fueron aplicados a la BD.'))
        
        self.stdout.write(self.style.WARNING('\n' + '='*70 + '\n'))
    
    def get_color_etiqueta(self, etiqueta):
        """Retorna el color ANSI para cada etiqueta"""
        colores = {
            'BUENO': '\033[92m',  # Verde
            'MEDIO': '\033[93m',  # Amarillo
            'MALO': '\033[91m',   # Rojo
            'SIN_HISTORIAL': '\033[94m',  # Azul
        }
        return colores.get(etiqueta, '')

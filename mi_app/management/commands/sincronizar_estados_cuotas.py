"""
✅ OPCIÓN C PASO 5: Management Command para sincronizar estados de cuotas

Corrije cuotas importadas que tienen mora calculada pero estado incorrecto.
Por ejemplo: Cuota con mora=$20,000 pero estado='PENDIENTE' en lugar de 'VENCIDA'.

Uso:
    python manage.py sincronizar_estados_cuotas           # Aplicar cambios
    python manage.py sincronizar_estados_cuotas --dry-run  # Vista previa
    python manage.py sincronizar_estados_cuotas --cliente-id=61 --dry-run  # Un cliente
"""

from django.core.management.base import BaseCommand, CommandError
from mi_app.models import Cuota
from mi_app.utils import determinar_estado_cuota_al_crear
from datetime import date


class Command(BaseCommand):
    help = 'Sincronizar estados de cuotas importadas que tienen estado incorrecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Mostrar qué cambios se haría SIN aplicarlos',
        )
        
        parser.add_argument(
            '--cliente-id',
            type=int,
            dest='cliente_id',
            default=None,
            help='Sincronizar solo cuotas de un cliente específico (ej: 61)',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        cliente_id = options.get('cliente_id')
        
        # ===== OBTENER CUOTAS A SINCRONIZAR =====
        if cliente_id:
            cuotas = Cuota.objects.filter(
                prestamo__cliente_id=cliente_id
            ).select_related('prestamo__cliente')
        else:
            cuotas = Cuota.objects.all().select_related('prestamo__cliente')
        
        cuotas = cuotas.order_by('prestamo__cliente__nombre', 'numero_cuota')
        
        # ===== VERIFICAR Y REGISTRAR CAMBIOS =====
        cambios = []
        total_revisadas = 0
        total_cambios = 0
        
        for cuota in cuotas:
            total_revisadas += 1
            
            # Determinar estado correcto
            estado_correcto = determinar_estado_cuota_al_crear(
                pagado=cuota.pagado,
                fecha_pago_esperada=cuota.fecha_pago_esperada,
                monto_pagado_principal=cuota.monto_pagado_principal,
                monto_original=cuota.monto_original
            )
            
            # Si es diferente, registrar cambio
            if cuota.estado != estado_correcto:
                cliente = cuota.prestamo.cliente
                cambios.append({
                    'cuota_id': cuota.id,
                    'cliente': cliente.nombre,
                    'cliente_id': cliente.id,
                    'prestamo_id': cuota.prestamo.id,
                    'numero_cuota': cuota.numero_cuota,
                    'estado_actual': cuota.estado,
                    'estado_nuevo': estado_correcto,
                    'fecha_pago_esperada': cuota.fecha_pago_esperada,
                    'dias_atraso': (date.today() - cuota.fecha_pago_esperada).days if cuota.fecha_pago_esperada else 'N/A',
                    'monto_pagado': str(cuota.monto_pagado_principal),
                    'monto_total': str(cuota.monto_original),
                })
                total_cambios += 1
        
        # ===== MOSTRAR RESUMEN =====
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 RESUMEN DE SINCRONIZACIÓN'
            )
        )
        self.stdout.write(f'Cuotas revisadas: {total_revisadas}')
        self.stdout.write(f'Cambios a aplicar: {total_cambios}')
        
        if not cambios:
            self.stdout.write(
                self.style.WARNING(
                    '\n✅ Todas las cuotas ya tienen estado correcto.'
                )
            )
            return
        
        # ===== MOSTRAR CAMBIOS DETALLADOS =====
        self.stdout.write(f'\n📝 CAMBIOS DETECTADOS:\n')
        
        for cambio in cambios:
            self.stdout.write(
                f"  • Cuota #{cambio['numero_cuota']} (ID={cambio['cuota_id']})"
            )
            self.stdout.write(
                f"    Cliente: {cambio['cliente']} (ID={cambio['cliente_id']})"
            )
            self.stdout.write(
                f"    Estado: {cambio['estado_actual']} → {cambio['estado_nuevo']}"
            )
            self.stdout.write(
                f"    Fecha vencimiento: {cambio['fecha_pago_esperada']} (Hace {cambio['dias_atraso']} días)"
            )
            self.stdout.write(
                f"    Pagado: ${cambio['monto_pagado']} de ${cambio['monto_total']}"
            )
            self.stdout.write()
        
        # ===== SI ES DRY-RUN, TERMINAR AQUÍ =====
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  DRY-RUN ACTIVADO: Se mostró qué sucedería.\n'
                    f'   Para aplicar, ejecutar SIN --dry-run'
                )
            )
            return
        
        # ===== APLICAR CAMBIOS EN BD =====
        self.stdout.write(
            self.style.WARNING(
                f'\n🔄 Aplicando {total_cambios} cambios en BD...'
            )
        )
        
        try:
            for cambio in cambios:
                Cuota.objects.filter(id=cambio['cuota_id']).update(
                    estado=cambio['estado_nuevo']
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ ¡Sincronización completada exitosamente!'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'   {total_cambios} estados actualizados en BD'
                )
            )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'\n❌ Error al aplicar cambios: {str(e)}'
                )
            )
            raise CommandError(f'Error de sincronización: {str(e)}')

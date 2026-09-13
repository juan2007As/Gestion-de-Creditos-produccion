"""
Management command para ejecutar auto-tagging de lista negra.
Marca/desmarcar clientes automáticamente basado en comportamiento de pagos.

USO:
    python manage.py auto_tagging_lista_negra [--dias=30] [--dry-run]

OPCIONES:
    --dias=X        Días de mora para considerar en lista negra (default: 30)
    --dry-run       Mostrar cambios sin aplicarlos
    --verbose       Mostrar detalles de cada cliente
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from mi_app.models import Cliente, ListaNegra
from datetime import date
import sys


class Command(BaseCommand):
    help = 'Auto-tagging de lista negra: marca/desmarcar clientes según comportamiento de pagos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Días de mora para considerar en lista negra (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar cambios sin aplicarlos'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar detalles de cada cliente'
        )

    def handle(self, *args, **options):
        """Ejecuta el auto-tagging"""
        dias_mora = options.get('dias', 30)
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        # Header
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*70}"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"AUTO-TAGGING LISTA NEGRA"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"{'='*70}"
        ))
        self.stdout.write(f"Modo: {'DRY-RUN (sin aplicar cambios)' if dry_run else 'EJECUCIÓN (aplicar cambios)'}")
        self.stdout.write(f"Días de mora: {dias_mora} días\n")
        
        # Obtener cliente admin para usar como usuario_creador
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
        except:
            admin_user = None
        
        # Estadísticas
        stats = {
            'total_clientes': 0,
            'marcados': 0,
            'desmarcados': 0,
            'sin_cambios': 0,
            'errores': 0,
        }
        
        cambios = []  # Log de cambios
        
        # Procesar cada cliente
        clientes = Cliente.objects.all().order_by('nombre')
        
        for cliente in clientes:
            stats['total_clientes'] += 1
            
            try:
                # Ejecutar auto-tagging
                cambio_realizado, mensaje = cliente.actualizar_lista_negra_automatica(
                    dias_mora=dias_mora,
                    usuario=admin_user
                )
                
                if cambio_realizado:
                    if 'MARCADO' in mensaje or 'REACTIVADO' in mensaje:
                        stats['marcados'] += 1
                    elif 'DESACTIVADO' in mensaje:
                        stats['desmarcados'] += 1
                    
                    cambios.append(mensaje)
                    if verbose or cambio_realizado:
                        self.stdout.write(self.style.WARNING(f"  {mensaje}"))
                else:
                    stats['sin_cambios'] += 1
                    if verbose:
                        self.stdout.write(f"  {mensaje}")
                        
            except Exception as e:
                stats['errores'] += 1
                self.stdout.write(self.style.ERROR(
                    f"  ❌ ERROR procesando {cliente.nombre}: {str(e)}"
                ))
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS("RESUMEN DE AUTO-TAGGING"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}"))
        self.stdout.write(f"Total de clientes procesados: {stats['total_clientes']}")
        self.stdout.write(self.style.WARNING(f"Marcados en lista negra:     {stats['marcados']}"))
        self.stdout.write(self.style.SUCCESS(f"Desmarcados de lista negra:  {stats['desmarcados']}"))
        self.stdout.write(f"Sin cambios:                 {stats['sin_cambios']}")
        
        if stats['errores'] > 0:
            self.stdout.write(self.style.ERROR(f"Errores:                     {stats['errores']}"))
        
        # Mostrar cambios si los hay
        if cambios:
            self.stdout.write(f"\n{'='*70}")
            self.stdout.write("REGISTRO DE CAMBIOS:")
            self.stdout.write(f"{'='*70}")
            for i, cambio in enumerate(cambios, 1):
                self.stdout.write(f"\n{i}. {cambio}")
        
        # Advertencia si es dry-run
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️  MODO DRY-RUN: Los cambios NO fueron aplicados."
            ))
            self.stdout.write(self.style.WARNING(
                f"Ejecuta sin --dry-run para aplicar los cambios reales."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Auto-tagging completado exitosamente."
            ))
        
        self.stdout.write(f"\n{'='*70}\n")

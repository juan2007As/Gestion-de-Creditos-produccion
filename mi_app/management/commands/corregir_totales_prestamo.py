from django.core.management.base import BaseCommand
from mi_app.models import Cliente

class Command(BaseCommand):
    help = 'Recalcula y corrige el campo total_prestado para todos los clientes basándose en sus préstamos reales.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Iniciando la corrección de totales prestados de clientes ---'))
        
        clientes = Cliente.objects.all()
        clientes_corregidos = 0
        inconsistencias_encontradas = 0
        
        for cliente in clientes:
            self.stdout.write(f'Procesando cliente: {cliente.nombre} (ID: {cliente.id})')
            
            tiene_inconsistencia, diferencia = cliente.tiene_inconsistencia_totales()
            
            if tiene_inconsistencia:
                inconsistencias_encontradas += 1
                self.stdout.write(self.style.WARNING(f'  -> Inconsistencia encontrada. Diferencia: ${diferencia}'))
                
                total_anterior, total_nuevo, _ = cliente.corregir_totales()
                
                msg = f'  -> CORREGIDO. Total anterior: ${total_anterior}, Nuevo total: ${total_nuevo}'
                self.stdout.write(self.style.SUCCESS(msg))
                clientes_corregidos += 1
            else:
                self.stdout.write('  -> Sin inconsistencias. No se necesita corrección.')

        self.stdout.write(self.style.SUCCESS('\\n--- Proceso de corrección finalizado ---'))
        self.stdout.write(f'Clientes revisados: {clientes.count()}')
        self.stdout.write(f'Inconsistencias encontradas: {inconsistencias_encontradas}')
        self.stdout.write(f'Clientes corregidos: {clientes_corregidos}')

        if inconsistencias_encontradas == 0:
            self.stdout.write(self.style.SUCCESS('¡Excelente! No se encontraron datos corruptos.'))
        else:
            self.stdout.write(self.style.WARNING('Se corrigieron las inconsistencias encontradas.'))

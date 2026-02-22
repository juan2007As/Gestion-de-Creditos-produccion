"""
AUDITOR DE VALIDACIONES - CRÍTICA #4
=====================================

Audita el estado actual de validaciones en el sistema.
Identifica qué validaciones están implementadas y cuáles faltan.

Ejecutar: python manage.py auditar_validaciones

Propósito:
- Verificar que las 7 validaciones críticas estén implementadas
- Detectar datos basura que ya existen en BD
- Generar reporte de inconsistencias
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Count, Sum
from decimal import Decimal
from datetime import date, timedelta
from mi_app.models import Cliente, Prestamo, Cuota, Pago, ListaNegra, Configuracion


class Command(BaseCommand):
    help = 'Audita el estado actual de validaciones del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Modo reparación: intenta corregir problemas encontrados'
        )

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write("🔍 AUDITOR DE VALIDACIONES - CRÍTICA #4")
        self.stdout.write("="*80 + "\n")
        
        fix_mode = options.get('fix', False)
        
        # Auditar cada validación
        self.validacion_1_fechas(fix_mode)
        self.validacion_2_limite_prestamos(fix_mode)
        self.validacion_3_capacidad_pago(fix_mode)
        self.validacion_4_num_cuotas(fix_mode)
        self.validacion_5_tasa_interes(fix_mode)
        self.validacion_6_pago_pendiente(fix_mode)
        self.validacion_7_lista_negra(fix_mode)
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write("✅ Auditoría completada")
        self.stdout.write("="*80 + "\n")
    
    # =========================================================================
    # VALIDACIÓN #1: Fecha de inicio debe ser >= hoy
    # =========================================================================
    
    def validacion_1_fechas(self, fix_mode):
        """
        VALIDACIÓN #1: Fecha de inicio debe ser >= hoy
        
        Problema: Préstamos con fecha_inicio en el pasado
        Causa: Sin validación en crear_prestamo()
        Impacto: Reportes con fechas inválidas
        """
        self.stdout.write("\n📋 VALIDACIÓN #1: Fechas de inicio")
        self.stdout.write("-" * 80)
        
        # Buscar préstamos con fecha_inicio anterior a hoy
        prestamos_pasado = Prestamo.objects.filter(
            fecha_inicio__lt=date.today()
        ).count()
        
        if prestamos_pasado == 0:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: Ningún préstamo en el pasado"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ ERROR: {prestamos_pasado} préstamos con fecha en el pasado"))
            for prestamo in Prestamo.objects.filter(fecha_inicio__lt=date.today())[:5]:
                self.stdout.write(f"   - Préstamo #{prestamo.id}: fecha={prestamo.fecha_inicio} (Hoy={date.today()})")
    
    # =========================================================================
    # VALIDACIÓN #2: Máximo 5 préstamos activos por cliente
    # =========================================================================
    
    def validacion_2_limite_prestamos(self, fix_mode):
        """
        VALIDACIÓN #2: Máximo 5 préstamos activos simultáneos por cliente
        
        Problema: Cliente podría tener 50 préstamos simultáneos
        Causa: Sin límite implementado
        Impacto: Cliente no puede pagar todos, mora exponencial
        """
        self.stdout.write("\n📋 VALIDACIÓN #2: Límite de préstamos activos")
        self.stdout.write("-" * 80)
        
        # Buscar clientes con > 5 préstamos activos
        clientes_exceso = {}
        for cliente in Cliente.objects.all():
            prestamos_activos = Prestamo.objects.filter(
                cliente=cliente,
                estado__in=['ACTIVO', 'VIGENTE']
            ).count()
            
            if prestamos_activos > 5:
                clientes_exceso[cliente] = prestamos_activos
        
        if not clientes_exceso:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: Ningún cliente con >5 préstamos activos"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ ERROR: {len(clientes_exceso)} clientes con >5 préstamos"))
            for cliente, count in list(clientes_exceso.items())[:5]:
                self.stdout.write(f"   - {cliente.nombre}: {count} préstamos activos")
    
    # =========================================================================
    # VALIDACIÓN #3: Monto vs Capacidad de pago
    # =========================================================================
    
    def validacion_3_capacidad_pago(self, fix_mode):
        """
        VALIDACIÓN #3: Monto desembolsado debe validarse contra capacidad de pago
        
        Problema: Préstamo de $1M a vendedor callejero con ingresos $500K
        Causa: Sin validación de capacidad
        Impacto: Cliente no puede pagar, mora predestinada
        """
        self.stdout.write("\n📋 VALIDACIÓN #3: Capacidad de pago vs Monto")
        self.stdout.write("-" * 80)
        
        # Este auditor es informativo (no tenemos campo de ingresos)
        # Suponemos que una regla simple es: capacidad_pago = total_prestado_historico * 0.5
        # (No puede tomar más prestado de lo que ya ha pagado)
        
        prestamos_riesgosos = []
        for cliente in Cliente.objects.all():
            # Historico de pagos / 2 = capacidad estimada
            total_pagado = Pago.objects.filter(cuota__prestamo__cliente=cliente).aggregate(
                total=Sum('monto_principal')
            )['total'] or Decimal('0')
            
            capacidad_estimada = total_pagado / Decimal('2')
            total_vigente = Prestamo.objects.filter(
                cliente=cliente,
                estado__in=['ACTIVO', 'VIGENTE']
            ).aggregate(total=Sum('monto_total'))['total'] or Decimal('0')
            
            if total_vigente > capacidad_estimada > 0:
                prestamos_riesgosos.append((cliente, total_vigente, capacidad_estimada))
        
        if not prestamos_riesgosos:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: Préstamos dentro de capacidad estimada"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  {len(prestamos_riesgosos)} clientes con préstamos > capacidad estimada"))
            for cliente, vigente, capacidad in prestamos_riesgosos[:5]:
                self.stdout.write(f"   - {cliente.nombre}: Vigente ${vigente} > Capacidad ${capacidad}")
    
    # =========================================================================
    # VALIDACIÓN #4: Número de cuotas entre 2, 4, 6, 8 solamente
    # =========================================================================
    
    def validacion_4_num_cuotas(self, fix_mode):
        """
        VALIDACIÓN #4: Número de cuotas debe ser 2, 4, 6 u 8 solamente
        
        Problema: Cuota de 1 día o 1000 días
        Causa: Sin validación de rango
        Impacto: Calendario de pagos sin sentido
        """
        self.stdout.write("\n📋 VALIDACIÓN #4: Número de cuotas válidas")
        self.stdout.write("-" * 80)
        
        # Contar cuotas por préstamo
        cuotas_inválidas = {}
        for prestamo in Prestamo.objects.all():
            num_cuotas = prestamo.cuotas.count()
            if num_cuotas not in [2, 4, 6, 8]:
                cuotas_inválidas[prestamo] = num_cuotas
        
        if not cuotas_inválidas:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: Todos los préstamos tienen 2,4,6 u 8 cuotas"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ ERROR: {len(cuotas_inválidas)} préstamos con número de cuotas inválido"))
            for prestamo, count in list(cuotas_inválidas.items())[:5]:
                self.stdout.write(f"   - Préstamo #{prestamo.id}: {count} cuotas (debe ser 2,4,6 u 8)")
    
    # =========================================================================
    # VALIDACIÓN #5: Tasa de interés entre 1.5% y 10%
    # =========================================================================
    
    def validacion_5_tasa_interes(self, fix_mode):
        """
        VALIDACIÓN #5: Tasa de interés debe estar entre 1.5% y 10%
        
        Problema: Interés de 500% o -5%
        Causa: Sin validación de rango
        Impacto: Mora calculada incorrectamente
        """
        self.stdout.write("\n📋 VALIDACIÓN #5: Rango de tasa de interés")
        self.stdout.write("-" * 80)
        
        # Buscar préstamos con tasa fuera del rango 1.5% - 10%
        Min_TASA = Decimal('1.5')
        MAX_TASA = Decimal('10.0')
        
        prestamos_tasa_invalida = Prestamo.objects.filter(
            Q(interes_porcentaje__lt=Min_TASA) | Q(interes_porcentaje__gt=MAX_TASA)
        )
        
        if prestamos_tasa_invalida.count() == 0:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: Todas las tasas entre 1.5% y 10%"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ ERROR: {prestamos_tasa_invalida.count()} préstamos con tasa fuera de rango"))
            for prestamo in prestamos_tasa_invalida[:5]:
                self.stdout.write(f"   - Préstamo #{prestamo.id}: {prestamo.interes_porcentaje}% (debe ser 1.5%-10%)")
    
    # =========================================================================
    # VALIDACIÓN #6: Monto de pago no puede exceder monto pendiente
    # =========================================================================
    
    def validacion_6_pago_pendiente(self, fix_mode):
        """
        VALIDACIÓN #6: Monto pagado en cuota no puede exceder monto pendiente
        
        Problema: Pagar $999,999 en cuota de $5,000
        Causa: Sin validación en vista de pago
        Impacto: Datos inconsistentes, más mora que lo pactado
        """
        self.stdout.write("\n📋 VALIDACIÓN #6: Monto pagado vs Monto pendiente")
        self.stdout.write("-" * 80)
        
        # Buscar cuotas donde monto_pagado > monto_pendiente
        cuotas_overpayment = 0
        for cuota in Cuota.objects.all():
            pagos = Pago.objects.filter(cuota=cuota).aggregate(total=Sum('monto_principal'))
            total_pagado = pagos['total'] or Decimal('0')
            
            if total_pagado > cuota.monto_original:
                cuotas_overpayment += 1
                if cuotas_overpayment <= 5:
                    self.stdout.write(f"   - Cuota #{cuota.id}: Pagado ${total_pagado} > Original ${cuota.monto_original}")
        
        if cuotas_overpayment == 0:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: Ningún overpayment de cuotas"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ ERROR: {cuotas_overpayment} cuotas con pago > monto original"))
    
    # =========================================================================
    # VALIDACIÓN #7: Cliente en lista negra no puede tomar préstamos
    # =========================================================================
    
    def validacion_7_lista_negra(self, fix_mode):
        """
        VALIDACIÓN #7: Cliente en lista negra NO puede crear/modificar préstamos
        
        Problema: Cliente en lista negra puede seguir pidiendo prestado
        Causa: Sin verificación de lista negra
        Impacto: Fraude potencial, cobranza más difícil
        """
        self.stdout.write("\n📋 VALIDACIÓN #7: Clientes en lista negra")
        self.stdout.write("-" * 80)
        
        # Buscar préstamos de clientes que están (o estuvieron) en lista negra
        clientes_en_lista = ListaNegra.objects.filter(activa=True).values_list('cliente_id', flat=True)
        prestamos_lista_negra = Prestamo.objects.filter(
            cliente_id__in=clientes_en_lista
        ).count()
        
        if prestamos_lista_negra == 0:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: Ningún préstamo de clientes en lista negra vigente"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ ERROR: {prestamos_lista_negra} préstamos de clientes en lista negra"))
            for prestamo in Prestamo.objects.filter(cliente_id__in=clientes_en_lista)[:5]:
                lista = ListaNegra.objects.get(cliente=prestamo.cliente)
                self.stdout.write(f"   - {prestamo.cliente.nombre}: Préstamo #{prestamo.id} (Razón: {lista.razon})")
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    
    def print_summary(self):
        """Imprime resumen de validaciones"""
        self.stdout.write("\n" + "="*80)
        self.stdout.write("📊 RESUMEN DE VALIDACIONES")
        self.stdout.write("="*80)

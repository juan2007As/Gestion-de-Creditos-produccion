from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

# ===============================================================================
# FUNCIONES AUXILIARES
# ===============================================================================

def calcular_fechas_pago(tipo_pago, num_cuotas, fecha_inicio=None):
    """
    Calcula las fechas de pago automáticamente según el tipo.
    PROBLEMA #11 CORREGIDO: Garantiza MÍNIMO 15 días entre CADA pareja de cuotas
    
    Args:
        tipo_pago: 'QUINCENAL' o 'MENSUAL'
        num_cuotas: Número de cuotas a generar
        fecha_inicio: Fecha inicial (default: hoy)
    
    Returns:
        Lista de fechas de pago con garantía de 15+ días entre cada una
    """
    if fecha_inicio is None:
        fecha_inicio = date.today()
    
    fechas = []
    
    if tipo_pago == 'QUINCENAL':
        # Días preferidos para pago (en orden de preferencia dentro del mes)
        dias_pago = [5, 15, 20, 30]
        
        # Primera cuota: mínimo 15 días desde fecha_inicio
        fecha_minima = fecha_inicio + timedelta(days=15)
        fecha_actual = fecha_minima
        
        for i in range(num_cuotas):
            # Buscar el día de pago más próximo >= fecha_actual
            dia_encontrado = None
            mes_actual = fecha_actual.month
            año_actual = fecha_actual.year
            
            # Intentar encontrar un día en el mes actual
            for dia in dias_pago:
                try:
                    fecha_candidata = date(año_actual, mes_actual, dia)
                    if fecha_candidata >= fecha_actual:
                        dia_encontrado = fecha_candidata
                        break
                except ValueError:
                    # Día inválido para este mes (ej: 30 en febrero)
                    pass
            
            # Si no hay día disponible este mes, ir al siguiente
            if dia_encontrado is None:
                mes_siguiente = mes_actual + 1
                año_siguiente = año_actual
                if mes_siguiente > 12:
                    mes_siguiente = 1
                    año_siguiente += 1
                
                # Buscar el primer día disponible en el siguiente mes
                for dia in dias_pago:
                    try:
                        fecha_candidata = date(año_siguiente, mes_siguiente, dia)
                        dia_encontrado = fecha_candidata
                        break
                    except ValueError:
                        pass
            
            if dia_encontrado:
                fechas.append(dia_encontrado)
                # Siguiente cuota debe ser al menos 15 días después
                fecha_actual = dia_encontrado + timedelta(days=15)
    
    elif tipo_pago == 'MENSUAL':
        # Próximo día 1 del mes, respetando mínimo 15 días
        fecha_actual = fecha_inicio + timedelta(days=15)
        
        for i in range(num_cuotas):
            # Ir al primer día del siguiente mes
            if fecha_actual.month == 12:
                proxima_fecha = date(fecha_actual.year + 1, 1, 1)
            else:
                proxima_fecha = date(fecha_actual.year, fecha_actual.month + 1, 1)
            
            fechas.append(proxima_fecha)
            fecha_actual = proxima_fecha + timedelta(days=15)
    
    return fechas

# Create your models here.

class Cliente(models.Model):
    cedula = models.CharField(max_length=20, blank=True, null=True, default='')
    nombre = models.CharField(max_length=100)
    celular = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    estado = models.CharField(
        max_length=20,
        choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')],
        default='ACTIVO'
    )
    rating = models.FloatField(default=0.0)
    total_prestado = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, null=True)
    importado_excel = models.BooleanField(default=False)  # Marca si fue importado desde Excel
    
    # ===== ERROR #3: CAMPOS PARA SCORING HISTÓRICO =====
    # Se actualizan automáticamente al limpiar préstamos antiguos
    total_prestado_historico = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Total acumulado HISTÓRICO (incluye préstamos eliminados)")
    total_pagado_historico = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Total pagado HISTÓRICO")
    tasa_cumplimiento = models.FloatField(default=100.0, help_text="% de cuotas pagadas a tiempo")
    dias_mora_promedio = models.FloatField(default=0.0, help_text="Promedio de días de mora")
    ultima_evaluacion = models.DateTimeField(null=True, blank=True, help_text="Última fecha de limpieza de histórico")
    
    # ===== ERROR #6: ETIQUETACIÓN DE CLIENTES =====
    # Clasificación automática: BUENO, MEDIO, MALO basada en comportamiento de pagos
    etiqueta_cliente = models.CharField(
        max_length=15,
        choices=[
            ('BUENO', 'Bueno'),
            ('MEDIO', 'Medio'),
            ('MALO', 'Malo'),
            ('SIN_HISTORIAL', 'Sin Historial'),
        ],
        default='SIN_HISTORIAL',
        help_text="Etiqueta automática: BUENO (95%+ cum, <5d mora), MEDIO (70-94%, 5-15d), MALO (<70%, >15d), SIN_HISTORIAL (sin préstamos)"
    )
    
    def __str__(self):
        return f"{self.nombre} - {self.celular}"
    
    @property
    def total_prestado_real(self):
        """
        Calcula en TIEMPO REAL el total prestado (suma de todos los monto_total de préstamos)
        Esta es la FUENTE DE VERDAD. El campo total_prestado es solo caché.
        """
        from django.db.models import Sum
        total = self.prestamo_set.aggregate(total=Sum('monto_total'))['total']
        return total or Decimal('0')
    
    @property
    def total_prestado_activo(self):
        """Total de préstamos activos (no completados ni cancelados)"""
        from django.db.models import Sum
        total = self.prestamo_set.filter(
            estado__in=['ACTIVO', 'EN_PROCESO']
        ).aggregate(total=Sum('monto_total'))['total']
        return total or Decimal('0')
    
    @property
    def total_prestado_completado(self):
        """Total de préstamos completados (pagados en su totalidad)"""
        from django.db.models import Sum
        total = self.prestamo_set.filter(
            estado='COMPLETADO'
        ).aggregate(total=Sum('monto_total'))['total']
        return total or Decimal('0')
    
    def tiene_inconsistencia_totales(self):
        """
        Verifica si hay inconsistencia entre total_prestado (caché) y total_prestado_real
        Retorna: (bool, diferencia)
        """
        diferencia = abs(self.total_prestado - self.total_prestado_real)
        tiene_inconsistencia = diferencia > Decimal('0.01')  # Tolerancia de 1 centavo
        return tiene_inconsistencia, diferencia
    
    def corregir_totales(self):
        """
        Recalcula y corrige los totales del cliente basándose en la BD
        Retorna: (total_prestado_anterior, total_prestado_nuevo, diferencia)
        """
        total_anterior = self.total_prestado
        self.total_prestado = self.total_prestado_real
        self.save()
        diferencia = abs(self.total_prestado - total_anterior)
        return total_anterior, self.total_prestado, diferencia

    def calcular_rating(self):
        """
        Calcula el rating del cliente basado en su historial de pagos.
        ★★★★★ = Pagó todo a tiempo
        ★★★ = Pagó con algunos retrasos
        ★ = Muchos retrasos
        """
        
        if not self.prestamo_set.exists():
            return 0.0
        
        prestamos_total = self.prestamo_set.count()
        prestamos_completados = self.prestamo_set.filter(estado='COMPLETADO').count()
        
        cuotas_vencidas = 0
        for prestamo in self.prestamo_set.all():
            for cuota in prestamo.cuotas.all():
                if not cuota.pagado and cuota.fecha_pago_esperada and cuota.fecha_pago_esperada < date.today():
                    cuotas_vencidas += 1

        if prestamos_total == 0:
            return 0.0
        porcentaje_completados = (prestamos_completados / prestamos_total) * 100
        
        if cuotas_vencidas > 3:
            rating = 1.0
        elif cuotas_vencidas > 1:
            rating = 2.0
        elif cuotas_vencidas == 1:
            rating = 3.0
        elif porcentaje_completados == 100:
            rating = 5.0
        else:
            rating = 4.0
            
        return rating
    
    # ✅ VALIDACIONES AGREGADAS
    def validar_cedula(self):
        """Valida que la cédula tenga formato correcto (números, sin caracteres especiales)"""
        if self.cedula:
            # Limpiar espacios
            cedula_limpia = self.cedula.strip().replace(' ', '-')
            # Validar que contenga solo números y guiones
            if not re.match(r'^[\d\-]+$', cedula_limpia):
                raise ValidationError("La cédula debe contener solo números y guiones")
            # Validar longitud mínima
            if len(cedula_limpia.replace('-', '')) < 6:
                raise ValidationError("La cédula debe tener al menos 6 dígitos")
            self.cedula = cedula_limpia
    
    def validar_email_unico(self):
        """Valida que el email sea único si existe"""
        if self.email:
            # Buscar otro cliente con el mismo email
            clientes_mismo_email = Cliente.objects.filter(
                email=self.email.lower()
            ).exclude(id=self.id)
            if clientes_mismo_email.exists():
                raise ValidationError(
                    f"Ya existe un cliente con el email '{self.email}'"
                )
    
    def validar_celular(self):
        """Valida que el celular sea válido"""
        if self.celular:
            # Remover espacios y caracteres especiales
            celular_limpio = re.sub(r'[^\d+]', '', self.celular)
            if len(celular_limpio) < 7:
                raise ValidationError("El celular debe tener al menos 7 dígitos")
            if not re.match(r'^(\+\d{1,3})?\d{7,}$', celular_limpio):
                raise ValidationError("El formato del celular no es válido")
            self.celular = celular_limpio
    
    def clean(self):
        """Ejecuta todas las validaciones del modelo"""
        errores = {}
        
        # Validar nombre
        if not self.nombre or not self.nombre.strip():
            errores['nombre'] = "El nombre es requerido"
        elif len(self.nombre.strip()) < 3:
            errores['nombre'] = "El nombre debe tener al menos 3 caracteres"
        
        # Validar celular
        try:
            self.validar_celular()
        except ValidationError as e:
            errores['celular'] = str(e.message)
        
        # Validar cédula
        try:
            self.validar_cedula()
        except ValidationError as e:
            errores['cedula'] = str(e.message)
        
        # Validar email único
        try:
            self.validar_email_unico()
        except ValidationError as e:
            errores['email'] = str(e.message)
        
        if errores:
            raise ValidationError(errores)
        
    def save(self, *args, **kwargs):
        """Ejecuta validaciones antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)
        
    def obtener_prestamos_activos(self):
        """Retorna solo los prestamos que estan activos"""
        return self.prestamo_set.filter(estado='ACTIVO')
    
    def obtener_cuotas_vencidas(self):
        """Retorna las cuotas vencidas del cliente"""
        from datetime import date
        cuotas_vencidas = []
        for prestamos in self.prestamo_set.all():
            for cuota in prestamos.cuotas.all():
                if not cuota.pagado and cuota.fecha_pago_esperada and cuota.fecha_pago_esperada < date.today():
                    cuotas_vencidas.append(cuota)
        return cuotas_vencidas
    
    @property
    def total_pagado(self):
        """Calcula dinámicamente el total pagado (suma de todos los pagos registrados)"""
        from decimal import Decimal
        total = Decimal('0')
        # Sumar todos los pagos de todas las cuotas de todos los préstamos del cliente
        for prestamo in self.prestamo_set.all():
            for cuota in prestamo.cuotas.all():
                for pago in cuota.pagos.all():  # related_name='pagos'
                    total += pago.monto_principal + pago.monto_interes + pago.monto_mora
        return total
    
    @property
    def total_pagado_principal(self):
        """Total pagado solo en capital"""
        from decimal import Decimal
        total = Decimal('0')
        for prestamo in self.prestamo_set.all():
            for cuota in prestamo.cuotas.all():
                for pago in cuota.pagos.all():  # related_name='pagos'
                    total += pago.monto_principal
        return total
    
    # ===== ERROR #5: AUTO-TAGGING PARA LISTA NEGRA =====
    def obtener_cuotas_vencidas_por_dias(self, dias_minimos=30):
        """
        Obtiene todas las cuotas vencidas por más de X días sin pago.
        Por defecto: 30 días de mora = va a lista negra
        """
        from datetime import date, timedelta
        cuotas_vencidas_mora = []
        fecha_limite = date.today() - timedelta(days=dias_minimos)
        
        for prestamo in self.prestamo_set.all():
            for cuota in prestamo.cuotas.all():
                # Si NO está pagada y la fecha esperada pasó más de X días
                if not cuota.pagado and cuota.fecha_pago_esperada:
                    if cuota.fecha_pago_esperada <= fecha_limite:
                        cuotas_vencidas_mora.append(cuota)
        
        return cuotas_vencidas_mora
    
    def debe_estar_en_lista_negra(self, dias_mora=30):
        """
        Verifica si el cliente DEBE estar en lista negra.
        Criterio: Tiene cuotas vencidas por más de X días
        """
        cuotas_mora = self.obtener_cuotas_vencidas_por_dias(dias_mora)
        return len(cuotas_mora) > 0
    
    def actualizar_lista_negra_automatica(self, dias_mora=30, usuario=None):
        """
        Marca/desmarcar automáticamente al cliente en lista negra basándose en comportamiento.
        - Si tiene cuotas vencidas por > X días: MARCAR
        - Si regularizó todos sus pagos: DESMARCAR
        
        Retorna: (accion_realizada, mensaje)
        """
        from django.contrib.auth.models import User
        
        debe_estar = self.debe_estar_en_lista_negra(dias_mora)
        
        try:
            lista_negra_actual = self.lista_negra
            esta_en_lista_negra = lista_negra_actual.esta_vigente
        except:
            lista_negra_actual = None
            esta_en_lista_negra = False
        
        # ✅ CASO 1: DEBE estar pero NO está → MARCAR
        if debe_estar and not esta_en_lista_negra:
            cuotas_mora = self.obtener_cuotas_vencidas_por_dias(dias_mora)
            dias_atraso = max([
                (date.today() - c.fecha_pago_esperada).days 
                for c in cuotas_mora
            ])
            
            # Si ya existe entrada inactiva, reactivarla
            if lista_negra_actual:
                lista_negra_actual.activa = True
                lista_negra_actual.razon = 'MOROSO'
                lista_negra_actual.fecha_desde = date.today()
                lista_negra_actual.fecha_hasta = None
                lista_negra_actual.save()
                accion = 'REACTIVADO'
            else:
                # Crear nueva entrada
                ListaNegra.objects.get_or_create(
                    cliente=self,
                    defaults={
                        'razon': 'MOROSO',
                        'descripcion': f'Automático: {len(cuotas_mora)} cuota(s) vencida(s) por {dias_atraso} días',
                        'fecha_desde': date.today(),
                        'activa': True,
                        'importado_excel': False,
                        'usuario_creador': usuario,
                    }
                )
                accion = 'MARCADO'
            
            return True, f"✅ Cliente {self.nombre} {accion} en lista negra (mora de {dias_atraso} días)"
        
        # ✅ CASO 2: NO debe estar pero SÍ está → DESMARCAR
        elif not debe_estar and esta_en_lista_negra:
            lista_negra_actual.activa = False
            lista_negra_actual.save()
            return True, f"✅ Cliente {self.nombre} DESACTIVADO de lista negra (regularizó pagos)"
        
        # ✅ CASO 3: Situación sin cambios
        else:
            if debe_estar and esta_en_lista_negra:
                return False, f"ℹ️ Cliente {self.nombre} ya está en lista negra (sin cambios)"
            else:
                return False, f"ℹ️ Cliente {self.nombre} no debe estar en lista negra (sin cambios)"
    
    # ===== ERROR #6: ETIQUETACIÓN AUTOMÁTICA DE CLIENTES =====
    
    def calcular_etiqueta(self):
        """
        Calcula la etiqueta del cliente según criterios de comportamiento:
        - BUENO: 95%+ cumplimiento, <5 días mora promedio (incl. 100% cumplimiento)
        - MEDIO: 70-94% cumplimiento, 5-15 días mora
        - MALO: <70% cumplimiento, >15 días mora
        - SIN_HISTORIAL: Sin préstamos o sin ningún pago registrado
        
        Retorna: etiqueta_calculada
        """
        # Sin préstamos → SIN_HISTORIAL
        if not self.prestamo_set.exists():
            return 'SIN_HISTORIAL'
        
        # Sin historial de pagos (ninguna cuota pagada) → SIN_HISTORIAL
        tiene_pagos = any(c.pagado for p in self.prestamo_set.all() for c in p.cuotas.all())
        if not tiene_pagos:
            return 'SIN_HISTORIAL'
        
        cumplimiento = self.tasa_cumplimiento
        morosidad = self.dias_mora_promedio
        
        # 100% cumplimiento y 0 mora = cliente bueno, no "sin historial"
        if cumplimiento >= 95.0 and morosidad < 5.0:
            return 'BUENO'
        elif 70.0 <= cumplimiento < 95.0 and morosidad >= 5.0 and morosidad <= 15.0:
            return 'MEDIO'
        elif cumplimiento < 70.0 or morosidad > 15.0:
            return 'MALO'
        else:
            # Casos grises: más cumplimiento = más bueno
            if cumplimiento >= 85.0:
                return 'BUENO'
            elif cumplimiento >= 75.0:
                return 'MEDIO'
            else:
                return 'MALO'
    
    def actualizar_etiqueta(self):
        """
        Actualiza el campo etiqueta_cliente basado en el cálculo automático.
        Se llama automáticamente después de registrar pagos.
        
        Retorna: (cambio_realizado, etiqueta_vieja, etiqueta_nueva)
        """
        etiqueta_vieja = self.etiqueta_cliente
        etiqueta_nueva = self.calcular_etiqueta()
        
        if etiqueta_vieja != etiqueta_nueva:
            self.etiqueta_cliente = etiqueta_nueva
            self.save(update_fields=['etiqueta_cliente'])
            return True, etiqueta_vieja, etiqueta_nueva
        else:
            return False, etiqueta_vieja, etiqueta_nueva
    
    class Meta:
        ordering = ['-fecha_creacion']
        constraints = [
            # ✅ CRÍTICA #8: Validaciones de datos financieros
            models.CheckConstraint(
                check=models.Q(total_prestado__gte=0),
                name='cliente_total_prestado_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(total_pagado_historico__gte=0),
                name='cliente_total_pagado_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(tasa_cumplimiento__gte=0) & models.Q(tasa_cumplimiento__lte=100),
                name='cliente_tasa_cumplimiento_rango_valido'
            ),
            models.CheckConstraint(
                check=models.Q(dias_mora_promedio__gte=0),
                name='cliente_dias_mora_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(rating__gte=0),
                name='cliente_rating_no_negativo'
            ),
        ]
        
class Prestamo(models.Model):
    CALENDARIO_CHOICES = [
        ('5_21', '5 y 21 de cada mes'),
        ('15_30', '15 y 30 de cada mes'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    interes_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin_estimada = models.DateField()
    calendario_pagos = models.CharField(
        max_length=10,
        choices=CALENDARIO_CHOICES,
        default='15_30'
    )
    tipo_pago = models.CharField(
        max_length=20,
        choices=[('QUINCENAL', 'Quincenal'), ('MENSUAL', 'Mensual')],
        default='QUINCENAL'
    )
    estado = models.CharField(
    max_length=20,
    choices=[('BORRADOR', 'Borrador'), ('ACTIVO', 'Activo'), ('COMPLETADO', 'Completado')],
    default='BORRADOR'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    notas_admin = models.TextField(blank=True)
    

    def __str__(self):
        return f"Préstamo {self.id} - {self.cliente.nombre} - {self.monto_total}"
    
    # ✅ VALIDACIONES AGREGADAS
    def clean(self):
        """Ejecuta validaciones del modelo Prestamo"""
        errores = {}
        
        # Validar monto > 0
        if self.monto_total and self.monto_total <= 0:
            errores['monto_total'] = "El monto debe ser mayor a 0"
        
        # Validar interés >= 0
        if self.interes_porcentaje and self.interes_porcentaje < 0:
            errores['interes_porcentaje'] = "El interés no puede ser negativo"
        
        # Validar fechas (solo al CREAR préstamo nuevo; al actualizar, fecha_inicio puede estar en el pasado)
        if self.fecha_inicio and self.pk is None:
            if self.fecha_inicio < date.today():
                errores['fecha_inicio'] = (
                    "La fecha de inicio no puede ser anterior a hoy. "
                    "No se permite crear préstamos retroactivos."
                )
        
        if self.fecha_fin_estimada and self.fecha_inicio:
            if self.fecha_fin_estimada <= self.fecha_inicio:
                errores['fecha_fin_estimada'] = (
                    "La fecha fin debe ser posterior a la fecha inicio"
                )
        
        # Validar que cliente no esté inactivo
        if self.cliente and self.cliente.estado != 'ACTIVO':
            errores['cliente'] = (
                f"No se puede crear préstamo a cliente inactivo ({self.cliente.nombre})"
            )
        
        if errores:
            raise ValidationError(errores)
    
    def save(self, *args, **kwargs):
        """Ejecuta validaciones antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def total_credito(self):
        """Monto + Interés (suma real de todas las cuotas)"""
        # Sumar el principal de todas las cuotas
        principal_total = sum(float(c.monto_original) for c in self.cuotas.all())
        # Sumar el interés de todas las cuotas
        interes_total = sum(float(c.interes_normal) for c in self.cuotas.all())
        return principal_total + interes_total
    @property
    def total_pagado(self):
        """Suma de todo lo pagado en todas las cuotas (principal + interés + mora)"""
        total = 0
        for cuota in self.cuotas.all():
            # Sumar principal pagado
            total += float(cuota.monto_pagado_principal)
            # Sumar interés pagado
            total += float(cuota.monto_pagado_interes)
            # Sumar mora pagada
            total += float(cuota.monto_pagado_mora)
        return total
    @property
    def total_pendiente(self):
        """total_credito - total_pagado"""
        return self.total_credito - self.total_pagado
    @property
    def total_mora(self):
        """Suma de mora de todas las cuotas"""
        total = Decimal('0')
        for cuota in self.cuotas.all():
            total += cuota.calcular_mora_diaria()
        return total
    @property
    def num_cuotas_pagadas(self):
        """Cuotas completamente pagadas"""
        return self.cuotas.filter(pagado=True).count()
    @property
    def num_cuotas_vencidas(self):
        """Cuotas vencidas sin pagar"""
        from datetime import date
        vencidas = 0
        for cuota in self.cuotas.all():
            if not cuota.pagado and cuota.fecha_pago_esperada and cuota.fecha_pago_esperada < date.today():
                vencidas += 1
        return vencidas
    def resumen_financiero(self):
        """Retorna dict con desglose como en el mockup"""
        from datetime import date
        # Calcular interés total sumando interes_normal de TODAS las cuotas
        interes_total = sum(float(c.interes_normal) for c in self.cuotas.all())
        # Si no hay cuotas aún, calcular basado en estructura: 2 cuotas por mes
        if not self.cuotas.exists():
            num_dias = (self.fecha_fin_estimada - self.fecha_inicio).days
            num_meses = num_dias / 30.0
            # Capital por mes
            capital_por_mes = float(self.monto_total) / num_meses
            # Interés total: 15% del capital por mes × número de meses
            interes_total = capital_por_mes * float(self.interes_porcentaje / 100) * num_meses
        
        # Calcular totales pagados por concepto
        total_pagado_principal = sum(float(c.monto_pagado_principal) for c in self.cuotas.all())
        total_pagado_interes = sum(float(c.monto_pagado_interes) for c in self.cuotas.all())
        total_pagado_mora = sum(float(c.monto_pagado_mora) for c in self.cuotas.all())
    
        return {
            'monto_original': float(self.monto_total),
            'tasa_interes_quincena': float(self.interes_porcentaje),
            'tasa_mora_diaria': 2000,
            'interes_total_credito': interes_total,
            'total_credito': float(self.monto_total) + interes_total,
            'total_pagado_principal': total_pagado_principal,
            'total_pagado_interes': total_pagado_interes,
            'total_pendiente_principal': float(self.monto_total) - total_pagado_principal,
            'total_pendiente_interes': interes_total - total_pagado_interes,
            'total_mora_acumulada': self.total_mora,
        }
    class Meta:
        ordering = ['-fecha_creacion']
        constraints = [
            # ✅ CRÍTICA #8: Validaciones de datos financieros
            models.CheckConstraint(
                check=models.Q(monto_total__gt=0),
                name='prestamo_monto_total_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(interes_porcentaje__gte=0),
                name='prestamo_interes_no_negativo'
            ),
        ]

class Cuota(models.Model):
    # Estados posibles para una cuota
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PARCIALMENTE_PAGADA', 'Parcialmente Pagada'),
        ('PAGADA', 'Completamente Pagada'),
        ('VENCIDA', 'Vencida sin Pago'),
        ('VENCIDA_PARCIAL', 'Vencida Parcialmente Pagada'),
    ]
    
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='cuotas')
    numero_cuota = models.IntegerField()
    monto_original = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Capital original
    monto_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Lo que falta pagar
    interes_normal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 7.5% (15% anual / 2)
    interes_mora_acumulado = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Mora acumulada
    fecha_pago_esperada = models.DateField(null=True, blank=True)  # Fecha de vencimiento (cada 15 días)
    pagado = models.BooleanField(default=False)  # Si está completamente pagado
    fecha_pago_real = models.DateField(blank=True, null=True)  # Fecha en que se pagó
    
    # BUG #9 ARREGLADO: Agregar estado y porcentaje pagado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        help_text='Estado actual de la cuota'
    )
    porcentaje_pagado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Porcentaje del monto original que ya se pagó (0-100)'
    )
    
    # DESGLOSE DE PAGOS (para el mockup)
    monto_pagado_principal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Principal pagado
    monto_pagado_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Interés pagado
    monto_pagado_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Mora pagada
    monto_pendiente_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Interés pendiente
    
    def __str__(self):
        return f"Cuota {self.numero_cuota} - Préstamo {self.prestamo.id} - ${self.monto_original}"
    
    def calcular_mora_diaria(self):
        """
        Calcula la mora acumulada según días de atraso.
        PROBLEMA #12 SOLUCIONADO: Incluye período de gracia antes de cobrar mora
        """
        if self.pagado or not self.fecha_pago_esperada:
            return Decimal('0')
        
        config = Configuracion.obtener_configuracion()
        dias_atraso = (date.today() - self.fecha_pago_esperada).days
        
        # Los primeros N días: No hay mora (período de gracia)
        if dias_atraso <= config.dias_gracia_mora:
            return Decimal('0')
        
        # Después del período de gracia: Cobrar mora
        dias_mora = dias_atraso - config.dias_gracia_mora
        return Decimal(str(dias_mora)) * config.tasa_mora_diaria
    
    def obtener_estado_cuota(self):
        """
        Estado visual de la cuota considerando moratoria y período de gracia.
        Retorna: PAGADA, PENDIENTE, DEMORADA (vencida sin mora), MOROSA (vencida con mora)
        """
        from datetime import date
        
        if self.pagado:
            return 'PAGADA'
        
        if not self.fecha_pago_esperada:
            return 'PENDIENTE'
        
        dias_atraso = (date.today() - self.fecha_pago_esperada).days
        config = Configuracion.obtener_configuracion()
        
        if dias_atraso < 0:
            return 'PENDIENTE'
        elif dias_atraso <= config.dias_gracia_mora:
            return 'DEMORADA'  # Vencida pero sin mora (en período de gracia)
        else:
            return 'MOROSA'  # Vencida con mora activa
    
    def actualizar_estado(self):
        """
        BUG #9 ARREGLADO: Recalcula automáticamente el estado y porcentaje pagado.
        Se debe llamar después de cada pago.
        """
        from datetime import date
        
        # Calcular porcentaje pagado
        if self.monto_original > 0:
            pagado_total = self.monto_pagado_principal
            self.porcentaje_pagado = (pagado_total / self.monto_original) * 100
        else:
            self.porcentaje_pagado = 0
        
        # Determinar estado
        # PRIMERO: Si monto_pendiente = 0, entonces está PAGADA (mayor prioridad)
        if self.monto_pendiente <= 0 and self.monto_pendiente_interes <= 0:
            self.estado = 'PAGADA'
            self.pagado = True
        elif self.pagado:
            self.estado = 'PAGADA'
        elif self.porcentaje_pagado > 0 and self.porcentaje_pagado < 100:
            # Pagada parcialmente
            if self.fecha_pago_esperada and (date.today() > self.fecha_pago_esperada):
                self.estado = 'VENCIDA_PARCIAL'
            else:
                self.estado = 'PARCIALMENTE_PAGADA'
        elif self.porcentaje_pagado == 0:
            # Sin pagar
            if self.fecha_pago_esperada and (date.today() > self.fecha_pago_esperada):
                self.estado = 'VENCIDA'
            else:
                self.estado = 'PENDIENTE'
        
        self.save()
        
    def save(self, *args, **kwargs):
        """
        AUTO-CORRECCIÓN: Al guardar una cuota, automáticamente:
        1. Actualiza la mora acumulada (si no está pagada)
        2. Actualiza el estado de la cuota
        
        Previene inconsistencias financieras (CRÍTICA #3)
        """
        # PASO 1: Auto-actualizar mora si no está completamente pagada
        if not self.pagado and self.fecha_pago_esperada:
            mora_calculada = self.calcular_mora_diaria()
            self.interes_mora_acumulado = mora_calculada
        
        # PASO 2: Auto-actualizar estado y porcentaje pagado
        if self.monto_original > 0:
            self.porcentaje_pagado = (self.monto_pagado_principal / self.monto_original) * 100
        else:
            self.porcentaje_pagado = 0
        
        # Determinar estado automáticamente
        if self.monto_pendiente <= 0 and self.monto_pendiente_interes <= 0:
            self.estado = 'PAGADA'
            self.pagado = True
        elif self.pagado:
            self.estado = 'PAGADA'
        elif self.porcentaje_pagado > 0 and self.porcentaje_pagado < 100:
            if self.fecha_pago_esperada and (date.today() > self.fecha_pago_esperada):
                self.estado = 'VENCIDA_PARCIAL'
            else:
                self.estado = 'PARCIALMENTE_PAGADA'
        elif self.porcentaje_pagado == 0:
            if self.fecha_pago_esperada and (date.today() > self.fecha_pago_esperada):
                self.estado = 'VENCIDA'
            else:
                self.estado = 'PENDIENTE'
        
        # PASO 3: Guardar
        super().save(*args, **kwargs)
    
    def total_a_pagar(self):
        """Retorna el total que debe pagar en esta cuota"""
        mora = self.calcular_mora_diaria()
        return float(self.monto_pendiente) + float(self.interes_normal) + float(mora)
    
    def total_pagado(self):
        """Calcula cuánto ya se pagó de esta cuota"""
        return float(self.monto_original) - float(self.monto_pendiente)
    
    def detalles_completos(self):
        """
        Retorna detalles desglosados de la cuota para el mockup
        Incluye: Original / Pagado / Pendiente
        """
        mora_actual = float(self.calcular_mora_diaria())
        
        # Lo pendiente de interés - usar el campo monto_pendiente_interes que se actualiza con cada pago
        interes_pendiente = float(self.monto_pendiente_interes) if self.monto_pendiente_interes else 0
        
        # Calcular días de atraso
        dias_para_vencer = None
        dias_vencidos_positivo = None
        if self.fecha_pago_esperada:
            dias_para_vencer = (self.fecha_pago_esperada - date.today()).days
            dias_vencidos_positivo = abs((self.fecha_pago_esperada - date.today()).days)
        
        return {
            # INFORMACIÓN GENERAL
            'numero_cuota': self.numero_cuota,
            'fecha_vencimiento': self.fecha_pago_esperada,
            'estado': 'PAGADA' if self.pagado else 'PENDIENTE',
            'dias_para_vencer': dias_para_vencer,
            'dias_vencidos_positivo': dias_vencidos_positivo,
            
            # ORIGINAL (Lo que se debe pagar inicialmente)
            'original_principal': float(self.monto_original) if self.monto_original else 0,
            'original_interes': float(self.interes_normal) if self.interes_normal else 0,
            'original_mora': 0,
            'original_total': float(self.monto_original or 0) + float(self.interes_normal or 0),
            
            # PAGADO (Lo que ya se pagó)
            'pagado_principal': float(self.monto_pagado_principal) if self.monto_pagado_principal else 0,
            'pagado_interes': float(self.monto_pagado_interes) if self.monto_pagado_interes else 0,
            'pagado_mora': float(self.monto_pagado_mora) if self.monto_pagado_mora else 0,
            'pagado_total': float(self.monto_pagado_principal or 0) + float(self.monto_pagado_interes or 0) + float(self.monto_pagado_mora or 0),
            
            # PENDIENTE (Lo que falta pagar)
            'pendiente_principal': float(self.monto_pendiente) if self.monto_pendiente else 0,
            'pendiente_interes': interes_pendiente,
            'pendiente_mora': mora_actual,
            'pendiente_total': float(self.monto_pendiente or 0) + interes_pendiente + mora_actual,
        }
    
    class Meta:
        ordering = ['numero_cuota']
        constraints = [
            # ✅ CRÍTICA #8: Validaciones de datos financieros
            models.CheckConstraint(
                check=models.Q(numero_cuota__gt=0),
                name='cuota_numero_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_original__gt=0),
                name='cuota_monto_original_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(interes_normal__gte=0),
                name='cuota_interes_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pagado_principal__gte=0),
                name='cuota_monto_pagado_principal_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pagado_interes__gte=0),
                name='cuota_monto_pagado_interes_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pagado_mora__gte=0),
                name='cuota_monto_pagado_mora_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pendiente__gte=0),
                name='cuota_monto_pendiente_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(porcentaje_pagado__gte=0) & models.Q(porcentaje_pagado__lte=100),
                name='cuota_porcentaje_pagado_rango_valido'
            ),
        ]


class Pago(models.Model):
    """
    Modelo para registrar cada transacción de pago realizado.
    Proporciona auditoría completa de quién pagó, cuándo y cuánto.
    """
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, related_name='pagos')
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)  # Total pagado en esta transacción
    monto_principal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Desglose: principal
    monto_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Desglose: interés
    monto_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Desglose: mora
    
    fecha_pago = models.DateTimeField(auto_now_add=True)  # Cuándo se registró
    usuario_registra = models.CharField(max_length=100, blank=True)  # Quién registró (nombre o user)
    referencia = models.CharField(max_length=100, blank=True)  # P.ej: número de comprobante, referencia bancaria
    notas = models.TextField(blank=True, null=True)  # Observaciones del pago
    
    @property
    def cliente(self):
        """Retorna el cliente del préstamo asociado a esta cuota"""
        return self.cuota.prestamo.cliente
    
    def __str__(self):
        return f"Pago de ${self.monto_pagado} - Cuota {self.cuota.numero_cuota} - {self.fecha_pago.strftime('%d/%m/%Y')}"
    
    def comprobante_texto(self):
        """Genera un texto formateado del comprobante para mostrar"""
        return f"""
COMPROBANTE DE PAGO
═══════════════════════════════════════
Fecha: {self.fecha_pago.strftime('%d/%m/%Y %H:%M')}
Usuario: {self.usuario_registra}
Referencia: {self.referencia}

Cliente: {self.cuota.prestamo.cliente.nombre}
Préstamo: #{self.cuota.prestamo.id}
Cuota: {self.cuota.numero_cuota} de {self.cuota.prestamo.cuotas.count()}

DESGLOSE:
Principal: ${float(self.monto_principal):.2f}
Interés: ${float(self.monto_interes):.2f}
Mora: ${float(self.monto_mora):.2f}
───────────────────────────────────────
TOTAL: ${float(self.monto_pagado):.2f}

Notas: {self.notas or 'N/A'}
═══════════════════════════════════════
        """
    
    class Meta:
        ordering = ['-fecha_pago']
        constraints = [
            # ✅ CRÍTICA #8: Validaciones de datos financieros
            models.CheckConstraint(
                check=models.Q(monto_pagado__gt=0),
                name='pago_monto_pagado_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_principal__gte=0),
                name='pago_monto_principal_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_interes__gte=0),
                name='pago_monto_interes_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_mora__gte=0),
                name='pago_monto_mora_no_negativo'
            ),
        ]


# ===============================================================================
# MODELOS PARA PRÉSTAMOS RÁPIDOS Y CONFIGURACIÓN
# ===============================================================================

class Configuracion(models.Model):
    """
    Modelo Singleton para almacenar configuración global del sistema.
    Tasas de interés, parámetros, etc.
    """
    tasa_interes_prestamo_normal = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=15.0,
        help_text="Tasa de interés anual para préstamos normales (%)"
    )
    tasa_interes_prestamo_rapido = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=20.0,
        help_text="Tasa de interés anual para préstamos rápidos (%)"
    )
    tasa_mora_diaria = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2000,
        help_text="Mora diaria por cuota vencida"
    )
    cuotas_por_defecto = models.IntegerField(
        default=2,
        help_text="Número de cuotas por defecto al crear un préstamo"
    )
    dias_gracia_mora = models.IntegerField(
        default=5,
        help_text="Días de gracia antes de empezar a cobrar mora (PROBLEMA #12)"
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Configuración Global del Sistema"
    
    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"
    
    @classmethod
    def obtener_configuracion(cls):
        """Retorna la única instancia de configuración"""
        config, created = cls.objects.get_or_create(pk=1)
        return config
    
    def save(self, *args, **kwargs):
        """Asegurar que solo existe una configuración"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevenir eliminación de la configuración"""
        pass


class PrestamoRapido(models.Model):
    """
    Modelo para préstamos rápidos/dinero extra.
    Independiente de los préstamos regulares.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('PARCIALMENTE_PAGADO', 'Parcialmente Pagado'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='prestamos_rapidos')
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    interes_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tasa de interés (%)")
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True, help_text="Fecha de vencimiento (opcional)")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    notas = models.TextField(blank=True, null=True, help_text="Notas adicionales (opcional)")
    monto_pagado = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fecha_pago_real = models.DateField(blank=True, null=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Préstamo Rápido ${self.monto} - {self.cliente.nombre}"
    
    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de pago"""
        monto_total = float(self.monto) + self.calcular_interes_total()
        return monto_total - float(self.monto_pagado)
    
    def calcular_interes_total(self):
        """Calcula el interés total del préstamo rápido"""
        monto_float = float(self.monto)
        interes = (monto_float * float(self.interes_porcentaje)) / 100
        return interes
    
    @property
    def total_a_pagar(self):
        """Total monto + interés"""
        return float(self.monto) + self.calcular_interes_total()
    
    @property
    def porcentaje_pagado(self):
        """Porcentaje del préstamo que ya se pagó"""
        if self.total_a_pagar == 0:
            return 0
        return (float(self.monto_pagado) / self.total_a_pagar) * 100
    
    def actualizar_estado(self):
        """Actualiza automáticamente el estado según el pago"""
        from decimal import Decimal
        
        monto_pagado_decimal = Decimal(str(self.monto_pagado))
        total_a_pagar_decimal = Decimal(str(self.total_a_pagar))
        
        # Comparar con tolerancia de 0.01 para redondeos
        # Usar quantize para asegurar precisión
        diferencia = total_a_pagar_decimal - monto_pagado_decimal
        
        if diferencia <= Decimal('0.01'):
            self.estado = 'PAGADO'
        elif monto_pagado_decimal > 0:
            self.estado = 'PARCIALMENTE_PAGADO'
        else:
            self.estado = 'PENDIENTE'
        self.save()
    
    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = "Préstamo Rápido"
        verbose_name_plural = "Préstamos Rápidos"
        constraints = [
            # ✅ CRÍTICA #8: Validaciones de datos financieros
            models.CheckConstraint(
                check=models.Q(monto__gt=0),
                name='prestamo_rapido_monto_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(interes_porcentaje__gte=0),
                name='prestamo_rapido_interes_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pagado__gte=0),
                name='prestamo_rapido_monto_pagado_no_negativo'
            ),
        ]


class CuotaRapida(models.Model):
    # Estados posibles para una cuota rápida
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PARCIALMENTE_PAGADA', 'Parcialmente Pagada'),
        ('PAGADA', 'Completamente Pagada'),
        ('VENCIDA', 'Vencida sin Pago'),
        ('VENCIDA_PARCIAL', 'Vencida Parcialmente Pagada'),
    ]

    prestamo_rapido = models.ForeignKey(
        PrestamoRapido,
        on_delete=models.CASCADE,
        related_name='cuotas_rapidas'
    )
    numero_cuota = models.IntegerField()
    monto_original = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interes_normal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interes_mora_acumulado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_pago_esperada = models.DateField(null=True, blank=True)
    pagado = models.BooleanField(default=False)
    fecha_pago_real = models.DateField(blank=True, null=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        help_text='Estado actual de la cuota'
    )
    porcentaje_pagado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Porcentaje del monto original que ya se pagó (0-100)'
    )

    monto_pagado_principal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_pagado_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_pagado_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_pendiente_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cuota Rápida {self.numero_cuota} - Préstamo {self.prestamo_rapido.id}"

    def calcular_mora_diaria(self):
        """
        Calcula la mora acumulada según días de atraso.
        Respeta período de gracia configurado.
        """
        if self.pagado or not self.fecha_pago_esperada:
            return Decimal('0')

        config = Configuracion.obtener_configuracion()
        dias_atraso = (date.today() - self.fecha_pago_esperada).days

        if dias_atraso <= config.dias_gracia_mora:
            return Decimal('0')

        dias_mora = dias_atraso - config.dias_gracia_mora
        return Decimal(str(dias_mora)) * config.tasa_mora_diaria

    def actualizar_estado(self):
        """
        Recalcula automáticamente el estado y porcentaje pagado.
        Se debe llamar después de cada pago.
        """
        from datetime import date

        if self.monto_original > 0:
            pagado_total = self.monto_pagado_principal
            self.porcentaje_pagado = (pagado_total / self.monto_original) * 100
        else:
            self.porcentaje_pagado = 0

        if self.monto_pendiente <= 0 and self.monto_pendiente_interes <= 0:
            self.estado = 'PAGADA'
            self.pagado = True
        elif self.pagado:
            self.estado = 'PAGADA'
        elif self.porcentaje_pagado > 0 and self.porcentaje_pagado < 100:
            if self.fecha_pago_esperada and (date.today() > self.fecha_pago_esperada):
                self.estado = 'VENCIDA_PARCIAL'
            else:
                self.estado = 'PARCIALMENTE_PAGADA'
        elif self.porcentaje_pagado == 0:
            if self.fecha_pago_esperada and (date.today() > self.fecha_pago_esperada):
                self.estado = 'VENCIDA'
            else:
                self.estado = 'PENDIENTE'

        self.save()

    def total_a_pagar(self):
        """Retorna el total que debe pagar en esta cuota"""
        mora = self.calcular_mora_diaria()
        return float(self.monto_pendiente) + float(self.monto_pendiente_interes) + float(mora)

    def detalles_completos(self):
        """
        Retorna detalles desglosados de la cuota rápida.
        """
        mora_actual = float(self.calcular_mora_diaria())
        interes_pendiente = float(self.monto_pendiente_interes) if self.monto_pendiente_interes else 0

        dias_para_vencer = None
        dias_vencidos_positivo = None
        if self.fecha_pago_esperada:
            dias_para_vencer = (self.fecha_pago_esperada - date.today()).days
            dias_vencidos_positivo = abs((self.fecha_pago_esperada - date.today()).days)

        return {
            'numero_cuota': self.numero_cuota,
            'fecha_vencimiento': self.fecha_pago_esperada,
            'estado': 'PAGADA' if self.pagado else 'PENDIENTE',
            'dias_para_vencer': dias_para_vencer,
            'dias_vencidos_positivo': dias_vencidos_positivo,
            'original_principal': float(self.monto_original) if self.monto_original else 0,
            'original_interes': float(self.interes_normal) if self.interes_normal else 0,
            'original_mora': 0,
            'original_total': float(self.monto_original or 0) + float(self.interes_normal or 0),
            'pagado_principal': float(self.monto_pagado_principal) if self.monto_pagado_principal else 0,
            'pagado_interes': float(self.monto_pagado_interes) if self.monto_pagado_interes else 0,
            'pagado_mora': float(self.monto_pagado_mora) if self.monto_pagado_mora else 0,
            'pagado_total': float(self.monto_pagado_principal or 0) + float(self.monto_pagado_interes or 0) + float(self.monto_pagado_mora or 0),
            'pendiente_principal': float(self.monto_pendiente) if self.monto_pendiente else 0,
            'pendiente_interes': interes_pendiente,
            'pendiente_mora': mora_actual,
            'pendiente_total': float(self.monto_pendiente or 0) + interes_pendiente + mora_actual,
        }

    class Meta:
        ordering = ['numero_cuota']
        constraints = [
            # ✅ CRÍTICA #8: Validaciones de datos financieros
            models.CheckConstraint(
                check=models.Q(numero_cuota__gt=0),
                name='cuota_rapida_numero_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_original__gt=0),
                name='cuota_rapida_monto_original_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(interes_normal__gte=0),
                name='cuota_rapida_interes_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pendiente__gte=0),
                name='cuota_rapida_monto_pendiente_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pagado_principal__gte=0),
                name='cuota_rapida_monto_pagado_principal_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pagado_interes__gte=0),
                name='cuota_rapida_monto_pagado_interes_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(monto_pagado_mora__gte=0),
                name='cuota_rapida_monto_pagado_mora_no_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(porcentaje_pagado__gte=0) & models.Q(porcentaje_pagado__lte=100),
                name='cuota_rapida_porcentaje_pagado_rango_valido'
            ),
        ]


class PagoPrestamoRapido(models.Model):
    """
    Modelo para registrar pagos de préstamos rápidos.
    Similar al modelo Pago pero para préstamos rápidos.
    """
    prestamo_rapido = models.ForeignKey(PrestamoRapido, on_delete=models.CASCADE, related_name='pagos')
    cuota_rapida = models.ForeignKey(
        CuotaRapida,
        on_delete=models.CASCADE,
        related_name='pagos',
        null=True,
        blank=True
    )
    monto_pagado = models.DecimalField(max_digits=15, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    usuario_registra = models.CharField(max_length=100, blank=True)
    referencia = models.CharField(max_length=100, blank=True, help_text="Número de comprobante o referencia")
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Pago ${self.monto_pagado} - {self.prestamo_rapido.cliente.nombre}"

    class Meta:
        ordering = ['-fecha_pago']
        verbose_name = "Pago Préstamo Rápido"
        verbose_name_plural = "Pagos Préstamos Rápidos"
        constraints = [
            # ✅ CRÍTICA #8: Validaciones de datos financieros
            models.CheckConstraint(
                check=models.Q(monto_pagado__gt=0),
                name='pago_prestamo_rapido_monto_positivo'
            ),
        ]


# ===============================================================================
# SIGNALS - AUTOMATIZACIONES
# ===============================================================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Prestamo)
def actualizar_total_prestado_cliente(sender, instance, created, **kwargs):
    """
    Signal que se dispara cuando se crea o modifica un Préstamo.
    Actualiza automáticamente el total_prestado del cliente y su etiqueta.
    """
    if created:  # Solo si es nuevo
        cliente = instance.cliente
        cliente.total_prestado += instance.monto_total
        cliente.actualizar_etiqueta()
        cliente.save()


@receiver(post_delete, sender=Prestamo)
def revertir_total_prestado_cliente(sender, instance, **kwargs):
    """
    Signal que se dispara cuando se elimina un Préstamo.
    Revierte el total_prestado del cliente y actualiza su etiqueta.
    """
    cliente = instance.cliente
    cliente.total_prestado -= instance.monto_total
    if cliente.total_prestado < 0:
        cliente.total_prestado = 0
    cliente.actualizar_etiqueta()
    cliente.save()


@receiver(post_save, sender=Pago)
def actualizar_cliente_post_pago(sender, instance, created, **kwargs):
    """
    Signal que se dispara al registrar un pago.
    Actualiza automáticamente la etiqueta del cliente y su estado de lista negra.
    """
    if created:
        cliente = instance.cuota.prestamo.cliente
        # Actualizar etiqueta (Bueno/Medio/Malo) según el nuevo pago
        cliente.actualizar_etiqueta()
        # Verificar si debe salir de lista negra si ya pagó
        cliente.actualizar_lista_negra_automatica(dias_mora=30)


@receiver(post_save, sender=PagoPrestamoRapido)
def actualizar_cliente_post_pago_rapido(sender, instance, created, **kwargs):
    """Signal para pagos rápidos"""
    if created:
        cliente = instance.prestamo_rapido.cliente
        cliente.actualizar_etiqueta()
        cliente.actualizar_lista_negra_automatica(dias_mora=30)


# Signal removed: total_pagado is now a calculated @property
# It's computed dynamically from all registered payments


# ===============================================================================
# AUDITORÍA DE CAMBIOS
# ===============================================================================

class HistorioCambios(models.Model):
    """
    Registra todos los cambios realizados en el sistema.
    Permite rastrear QUIÉN cambió QUÉ, CUÁNDO y POR QUÉ.
    
    Campos:
    - usuario: Quién hizo el cambio
    - accion: Tipo de cambio (CREAR, EDITAR, ELIMINAR, CONDONAR, etc.)
    - modelo: Modelo afectado (Cliente, Préstamo, Cuota, etc.)
    - objeto_id: ID del objeto modificado
    - objeto_str: Representación del objeto (ej: "Cliente: Juan Pérez")
    - campo_modificado: Qué campo cambió (ej: "monto", "fecha_pago")
    - valor_anterior: Valor antes del cambio
    - valor_nuevo: Valor después del cambio
    - razon: Por qué se hizo el cambio (justificación)
    - fecha_cambio: Cuándo se hizo
    - ip_address: IP de quién lo hizo (para seguridad)
    - notas: Notas adicionales
    """
    
    TIPOS_ACCION = [
        ('CREAR', 'Creación'),
        ('EDITAR', 'Edición'),
        ('ELIMINAR', 'Eliminación'),
        ('CONDONAR', 'Condonación'),
        ('PAGAR', 'Pago'),
        ('REVERTIR', 'Reversión'),
        ('OTRO', 'Otro'),
    ]
    
    usuario = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='cambios_realizados')
    accion = models.CharField(max_length=20, choices=TIPOS_ACCION, db_index=True)
    modelo = models.CharField(max_length=100, db_index=True)  # Ej: "Cliente", "Préstamo", "Cuota"
    objeto_id = models.PositiveIntegerField(db_index=True)
    objeto_str = models.CharField(max_length=255)  # Representación del objeto para visualización
    
    campo_modificado = models.CharField(max_length=100, blank=True)
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    
    razon = models.CharField(max_length=255, blank=True)  # Justificación del cambio
    fecha_cambio = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = "Cambio"
        verbose_name_plural = "Auditoría de Cambios"
        indexes = [
            models.Index(fields=['usuario', '-fecha_cambio']),
            models.Index(fields=['modelo', '-fecha_cambio']),
            models.Index(fields=['accion', '-fecha_cambio']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.objeto_str} por {self.usuario.first_name or self.usuario.username} ({self.fecha_cambio.strftime('%d/%m/%Y %H:%M')})"
    
    def resumen(self):
        """Retorna un resumen legible del cambio"""
        if self.valor_anterior and self.valor_nuevo:
            return f"{self.campo_modificado}: {self.valor_anterior} → {self.valor_nuevo}"
        return f"{self.get_accion_display()}: {self.objeto_str}"


# ===============================================================================
# MODELOS DE ROLES Y PERMISOS (Nuevo Sistema de Autorización)
# ===============================================================================

class Rol(models.Model):
    """
    Rol del sistema - Define un conjunto de permisos agrupados.
    Ejemplos: ADMIN, GERENTE, OPERARIO
    
    Un usuario tiene UNO Y SOLO UN rol.
    Un rol tiene MÚLTIPLES permisos.
    """
    nombre = models.CharField(
        max_length=50,
        unique=True,
        choices=[
            ('ADMIN', 'Administrador'),
            ('GERENTE', 'Gerente'),
            ('OPERARIO', 'Operario'),
        ]
    )
    descripcion = models.TextField(
        help_text="Descripción clara del rol y sus responsabilidades"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return f"{self.get_nombre_display()}"
    
    @property
    def permisos_list(self):
        """Obtiene lista de permisos para este rol"""
        return self.rolpermiso_set.filter(
            permiso__activo=True
        ).values_list('permiso__codigo', flat=True)


class Permiso(models.Model):
    """
    Permiso granular del sistema.
    Formato: 'entidad.accion'
    Ejemplos: 'cliente.view', 'prestamo.create', 'config.edit'
    
    Estos permisos se asignan a Roles mediante RolPermiso.
    """
    codigo = models.CharField(
        max_length=100,
        unique=True,
        help_text="Formato: 'entidad.accion' (ej: cliente.view)"
    )
    descripcion = models.TextField()
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('LECTURA', 'Lectura'),
            ('CREACION', 'Creación'),
            ('EDICION', 'Edición'),
            ('ELIMINACION', 'Eliminación'),
            ('IMPORTACION', 'Importación'),
            ('EXPORTACION', 'Exportación'),
            ('SISTEMA', 'Sistema'),
        ],
        default='LECTURA'
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['categoria', 'codigo']
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
    
    def __str__(self):
        return f"{self.codigo} ({self.get_categoria_display()})"


class RolPermiso(models.Model):
    """
    Relación M:M entre Rol y Permiso.
    Define QUÉ permisos tiene CADA rol.
    
    Ejemplo:
      - Rol ADMIN tiene permiso 'cliente.create'
      - Rol GERENTE tiene permiso 'cliente.create'
      - Rol OPERARIO tiene permiso 'cliente.create'
    pero
      - Rol OPERARIO NO tiene permiso 'cliente.edit'
    """
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name='rolpermiso_set'
    )
    permiso = models.ForeignKey(
        Permiso,
        on_delete=models.CASCADE,
        related_name='en_roles'
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('rol', 'permiso')
        verbose_name = "Rol - Permiso"
        verbose_name_plural = "Roles - Permisos"
    
    def __str__(self):
        return f"{self.rol.nombre} → {self.permiso.codigo}"


class UsuarioProfile(models.Model):
    """
    Extensión del modelo User de Django.
    Agrega rol del sistema y metadata de usuario.
    
    Relación 1:1 con django.contrib.auth.models.User
    El User existente se usa para login/contraseña.
    El UsuarioProfile agrega rol y permisos.
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        help_text="Rol del usuario en el sistema"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.rol.nombre if self.rol else 'Sin Rol'})"
    
    def tiene_permiso(self, codigo_permiso):
        """
        Verifica si este usuario tiene un permiso específico.
        
        Args:
            codigo_permiso (str): Código del permiso (ej: 'cliente.create')
            
        Returns:
            bool: True si tiene permiso, False si no
        """
        if not self.rol:
            return False
        
        if not self.activo:
            return False
        
        return Permiso.objects.filter(
            codigo=codigo_permiso,
            activo=True,
            en_roles__rol=self.rol
        ).exists()
    
    def tiene_rol(self, nombre_rol):
        """
        Verifica si el usuario tiene un rol específico.
        
        Args:
            nombre_rol (str): Nombre del rol (ej: 'ADMIN', 'GERENTE')
            
        Returns:
            bool: True si tiene el rol, False si no
        """
        if not self.activo:
            return False
        
        return self.rol and self.rol.nombre == nombre_rol
    
    @property
    def permisos(self):
        """Retorna lista de códigos de permiso que tiene este usuario"""
        if not self.rol:
            return []
        return list(self.rol.permisos_list)


# Crear signal para auto-crear UsuarioProfile cuando se crea un User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_user_profile(sender, instance, created, **kwargs):
    """Auto-crea UsuarioProfile cuando se crea un User"""
    if created:
        # Solo crear si no existe admin user (caso especial)
        rol_operario = Rol.objects.filter(nombre='OPERARIO').first()
        if rol_operario:
            UsuarioProfile.objects.get_or_create(
                usuario=instance,
                defaults={'rol': rol_operario}
            )


# ===============================================================================
# ERROR #3: MODELO DE SCORING HISTÓRICO
# ===============================================================================

class ClienteScoring(models.Model):
    """
    Registro histórico de scoring del cliente
    Se crea cada vez que se ejecuta la limpieza automática
    Permite mantener auditoría de comportamiento del cliente
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='scoring_history')
    
    # Agregados guardados en este registro
    total_prestado_acumulado = models.DecimalField(max_digits=15, decimal_places=2)
    total_pagado_acumulado = models.DecimalField(max_digits=15, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Métricas de comportamiento
    cuotas_pagadas_a_tiempo = models.IntegerField(default=0)
    cuotas_vencidas = models.IntegerField(default=0)
    tasa_cumplimiento = models.FloatField(default=100.0)  # %
    dias_mora_promedio = models.FloatField(default=0.0)
    
    # Metadata
    fecha_registro = models.DateTimeField(auto_now_add=True)
    prestamos_limpiados = models.IntegerField(default=0, help_text="Cuántos préstamos se eliminaron en esta limpieza")
    periodo_inicio = models.DateField(null=True, blank=True)
    periodo_fin = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_registro']
        verbose_name_plural = "Cliente Scorings"
    
    def __str__(self):
        return f"{self.cliente.nombre} - {self.fecha_registro.strftime('%d/%m/%Y')}"


# ===============================================================================
# ERROR #5: LISTA NEGRA DE CLIENTES
# ===============================================================================

class ListaNegra(models.Model):
    """
    Modelo para mantener lista negra de clientes
    Previene crear préstamos a clientes en lista negra
    """
    
    RAZON_CHOICES = [
        ('FRAUDE', 'Fraude'),
        ('MOROSO', 'Moroso'),
        ('COBRANZA', 'En cobranza judicial'),
        ('INCUMPLIMIENTO', 'Incumplimiento de contrato'),
        ('OTRO', 'Otro motivo'),
    ]
    
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        related_name='lista_negra',
        help_text="Cliente en lista negra"
    )
    razon = models.CharField(
        max_length=50,
        choices=RAZON_CHOICES,
        default='OTRO',
        help_text="Razón por la que está en lista negra"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del motivo"
    )
    fecha_agregacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en que se agregó a la lista negra"
    )
    fecha_desde = models.DateField(
        help_text="Fecha a partir de la cual está en lista negra"
    )
    fecha_hasta = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha hasta la cual está en lista negra (si es temporal)"
    )
    activa = models.BooleanField(
        default=True,
        help_text="Indica si la entrada en lista negra está activa"
    )
    usuario_creador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lista_negra_creadas'
    )
    importado_excel = models.BooleanField(
        default=False,
        help_text="Indica si fue importado desde Excel"
    )
    
    class Meta:
        verbose_name = "Entrada Lista Negra"
        verbose_name_plural = "Entradas Lista Negra"
        ordering = ['-fecha_agregacion']
        indexes = [
            models.Index(fields=['cliente', 'activa']),
            models.Index(fields=['activa', 'fecha_desde']),
        ]
    
    def __str__(self):
        return f"{self.cliente.nombre} - {self.razon}"
    
    @property
    def esta_vigente(self):
        """Retorna True si la entrada está vigente (activa y dentro del período)"""
        if not self.activa:
            return False
        
        hoy = date.today()
        
        # Verificar que hoy sea >= fecha_desde
        if hoy < self.fecha_desde:
            return False
        
        # Si tiene fecha_hasta, verificar que hoy <= fecha_hasta
        if self.fecha_hasta and hoy > self.fecha_hasta:
            return False
        
        return True
    
    def desactivar(self, razon=""):
        """Desactiva la entrada en lista negra"""
        self.activa = False
        self.save()
    
    def reactivar(self):
        """Reactiva la entrada en lista negra"""
        self.activa = True
        self.save()


# ===============================================================================
# AUDITORÍA DE BACKUPS - Nuevo (Feb 21, 2026)
# ===============================================================================

class AuditoriaBackup(models.Model):
    """
    Registra todos los eventos de backup realizados en el sistema.
    Permite rastrear QUIÉN hizo el backup, CUÁNDO, DÓNDE se guardó y ESTADO.
    
    Campos:
    - usuario: Quién ejecutó el backup
    - tipo_backup: RAPIDO, LOCAL, DESCARGA, CORREO
    - ubicacion: Dónde se guardó (local, descarga, email)
    - nombre_archivo: Nombre del archivo ZIP generado
    - tamano_mb: Tamaño en MB del backup
    - estado: SUCCESS, PENDIENTE, ERROR
    - razon_error: Si falló, por qué
    - fecha_inicio: Cuándo comenzó
    - fecha_finalizacion: Cuándo terminó
    - correo_destino: Si se envió por correo, a dónde
    - ip_address: IP desde donde se ejecutó
    """
    
    TIPOS_BACKUP = [
        ('RAPIDO', 'Backup Rápido'),
        ('LOCAL', 'Guardar Local'),
        ('DESCARGA', 'Descarga Navegador'),
        ('CORREO', 'Envío Correo'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('SUCCESS', 'Exitoso'),
        ('ERROR', 'Error'),
    ]
    
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='backups_realizados'
    )
    
    tipo_backup = models.CharField(
        max_length=20,
        choices=TIPOS_BACKUP,
        db_index=True,
        default='RAPIDO'
    )
    
    ubicacion = models.CharField(
        max_length=255,
        help_text="Dónde se guardó o envió (ej: /backups/, correo@cliente.com)"
    )
    
    nombre_archivo = models.CharField(
        max_length=255,
        help_text="Nombre del ZIP generado (ej: backup_20260221_144530.zip)"
    )
    
    tamano_mb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tamaño en MB del archivo ZIP"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        db_index=True,
        default='PENDIENTE'
    )
    
    razon_error = models.TextField(
        blank=True,
        help_text="Descripción del error si falló"
    )
    
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    fecha_finalizacion = models.DateTimeField(
        null=True,
        blank=True
    )
    
    correo_destino = models.EmailField(
        null=True,
        blank=True,
        help_text="Email destino si se envió por correo"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre el backup"
    )
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Auditoría Backup"
        verbose_name_plural = "Auditoría de Backups"
        indexes = [
            models.Index(fields=['usuario', '-fecha_inicio']),
            models.Index(fields=['tipo_backup', '-fecha_inicio']),
            models.Index(fields=['estado', '-fecha_inicio']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_backup_display()} - {self.usuario.username} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"
    
    def resumen(self):
        """Retorna un resumen del backup"""
        return f"{self.get_tipo_backup_display()}: {self.nombre_archivo} ({self.tamano_mb} MB) - {self.get_estado_display()}"


# ===============================================================================
# CRÍTICA #6: AUDIT LOG MODEL
# ===============================================================================

class AuditLog(models.Model):
    """
    Registro de auditoría completo de todas las operaciones en el sistema.
    ¿QUIÉN hizo QUÉ, CUÁNDO, y ANTES/DESPUÉS?
    
    Campos:
    - usuario: Quién realizó la acción
    - accion: CREATE, UPDATE, DELETE, RESTORE
    - modelo: Qué modelo fue afectado (Prestamo, Cuota, Pago, Cliente, etc)
    - objeto_id: ID del objeto afectado
    - cambios: JSON con before/after de los campos modificados
    - timestamp: Cuándo se realizó (auto_now_add)
    - ip_address: De dónde vino la solicitud
    """
    
    ACCIONES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('RESTORE', 'Restaurar'),
    ]
    
    MODELOS = [
        ('Cliente', 'Cliente'),
        ('Prestamo', 'Préstamo'),
        ('Cuota', 'Cuota'),
        ('Pago', 'Pago'),
        ('ListaNegra', 'Lista Negra'),
        ('Configuracion', 'Configuración'),
        ('User', 'Usuario'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        db_index=True,
        help_text="Usuario que realizó la acción"
    )
    
    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        db_index=True,
        help_text="Tipo de acción realizada"
    )
    
    modelo = models.CharField(
        max_length=50,
        choices=MODELOS,
        db_index=True,
        help_text="Modelo/tabla afectada"
    )
    
    objeto_id = models.IntegerField(
        help_text="ID del objeto afectado"
    )
    
    objeto_representacion = models.CharField(
        max_length=255,
        blank=True,
        help_text="Representación legible del objeto (ej: Prestamo #123)"
    )
    
    cambios = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON con cambios: {'campo': ['antes', 'después']}"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Fecha y hora de la acción"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP de origen de la solicitud"
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción legible en formato texto"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        indexes = [
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['modelo', '-timestamp']),
            models.Index(fields=['accion', '-timestamp']),
            models.Index(fields=['objeto_id', 'modelo']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} {self.objeto_representacion} por {self.usuario.username if self.usuario else 'Sistema'} ({self.timestamp.strftime('%d/%m/%Y %H:%M')})"
    
    def get_cambios_legibles(self):
        """Retorna los cambios en formato legible"""
        if not self.cambios:
            return "Sin cambios registrados"
        
        cambios_texto = []
        for campo, [antes, despues] in self.cambios.items():
            cambios_texto.append(f"{campo}: '{antes}' → '{despues}'")
        
        return "; ".join(cambios_texto)
    
    @property
    def resumen(self):
        """Resumen de la auditoría"""
        return f"{self.get_accion_display()}: {self.objeto_representacion} - {self.get_cambios_legibles()}"


# ===============================================================================
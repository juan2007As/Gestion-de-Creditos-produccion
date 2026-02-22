from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente, Prestamo, Cuota, Configuracion, PrestamoRapido, PagoPrestamoRapido
import re
from datetime import datetime, timedelta

class ClienteForm(forms.ModelForm):
    """Formulario mejorado para crear/editar clientes con validación robusta"""
    
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombre', 'celular', 'email', 'estado', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula/Pasaporte'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de celular'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales...'}),
        }
        
        labels = {
            'nombre': 'Nombre Completo',
            'cedula': 'Cédula/Pasaporte',
            'celular': 'Número de Celular',
            'email': 'Correo Electrónico',
            'estado': 'Estado del Cliente',
            'notas': 'Notas/Anotaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].required = True
        self.fields['cedula'].required = False
        self.fields['celular'].required = True
        self.fields['email'].required = False
        self.fields['estado'].required = True
        self.fields['notas'].required = False
    
    def clean_nombre(self):
        """Validar nombre: mínimo 3 caracteres, máximo 100"""
        nombre = self.cleaned_data.get('nombre', '').strip()
        
        if not nombre:
            raise ValidationError('El nombre es requerido.')
        
        if len(nombre) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        
        if len(nombre) > 100:
            raise ValidationError('El nombre no puede exceder 100 caracteres.')
        
        # Verificar que no sea solo números
        if nombre.isdigit():
            raise ValidationError('El nombre no puede ser solo números.')
        
        return nombre.strip()
    
    def clean_cedula(self):
        """Validar cédula: formato válido, sin duplicados (opcional)"""
        cedula = (self.cleaned_data.get('cedula') or '').strip()
        
        # Si no se proporciona cédula, es válido
        if not cedula:
            return cedula
        
        # Remover espacios y caracteres especiales
        cedula = re.sub(r'[^\d]', '', cedula)
        
        if len(cedula) < 8:
            raise ValidationError('La cédula debe tener al menos 8 dígitos.')
        
        # Verificar duplicados (excepto si es la misma instancia)
        existente = Cliente.objects.filter(cedula=cedula)
        if self.instance.pk:
            existente = existente.exclude(pk=self.instance.pk)
        
        if existente.exists():
            raise ValidationError('Ya existe un cliente registrado con esta cédula.')
        
        return cedula
    
    def clean_celular(self):
        """Validar celular: debe ser obligatorio y con formato válido"""
        celular = (self.cleaned_data.get('celular') or '').strip()
        
        if not celular:
            raise ValidationError('El celular es requerido.')
        
        # Remover espacios y caracteres especiales
        celular = re.sub(r'[^\d\+]', '', celular)
        
        if len(celular) < 10:
            raise ValidationError('El celular debe tener al menos 10 dígitos.')
        
        return celular
    
    def clean_email(self):
        """Validar email: formato válido y sin duplicados si se proporciona"""
        email = (self.cleaned_data.get('email') or '').strip()
        
        if not email:
            return ''
        
        # Validar formato básico
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError('Formato de correo inválido.')
        
        # Verificar duplicados
        existente = Cliente.objects.filter(email=email)
        if self.instance.pk:
            existente = existente.exclude(pk=self.instance.pk)
        
        if existente.exists():
            raise ValidationError('Ya existe un cliente con este correo electrónico.')
        
        return email.lower().strip()
    
    def clean(self):
        """Validaciones generales"""
        cleaned_data = super().clean()
        return cleaned_data


class PrestamoForm(forms.ModelForm):
    """Formulario mejorado para crear/editar préstamos con validaciones"""
    
    class Meta:
        model = Prestamo
        fields = ['cliente', 'monto_total', 'interes_porcentaje', 'fecha_inicio', 'fecha_fin_estimada', 'tipo_pago', 'calendario_pagos', 'notas_admin']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'monto_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'interes_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '15', 'step': '0.01', 'min': '0'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin_estimada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-control'}),
            'calendario_pagos': forms.Select(attrs={'class': 'form-control'}),
            'notas_admin': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas internas...'}),
        }
        
        labels = {
            'cliente': 'Cliente',
            'monto_total': 'Monto Total ($)',
            'interes_porcentaje': 'Tasa de Interés (%)',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin_estimada': 'Fecha Estimada de Fin',
            'tipo_pago': 'Tipo de Pago',
            'calendario_pagos': 'Calendario de Pagos',
            'notas_admin': 'Notas Internas',
        }
    
    def clean_monto_total(self):
        """Validar monto: debe ser positivo y razonable"""
        monto = self.cleaned_data.get('monto_total')
        
        if monto is None:
            raise ValidationError('El monto es requerido.')
        
        monto = float(monto)
        
        if monto <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
        
        if monto > 1000000:
            raise ValidationError('El monto parece demasiado alto (máx 1,000,000).')
        
        return monto
    
    def clean_interes_porcentaje(self):
        """Validar tasa de interés: entre 0 y 100%"""
        interes = self.cleaned_data.get('interes_porcentaje')
        
        if interes is None:
            raise ValidationError('La tasa de interés es requerida.')
        
        interes = float(interes)
        
        if interes < 0:
            raise ValidationError('La tasa de interés no puede ser negativa.')
        
        if interes > 100:
            raise ValidationError('La tasa de interés no puede exceder 100%.')
        
        return interes
    
    def clean_fecha_inicio(self):
        """Validar fecha inicio: no puede ser en el pasado"""
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        
        if not fecha_inicio:
            raise ValidationError('La fecha de inicio es requerida.')
        
        # Permitir hoy o fechas futuras
        if fecha_inicio < datetime.now().date():
            raise ValidationError('La fecha de inicio no puede ser en el pasado.')
        
        return fecha_inicio
    
    def clean(self):
        """Validaciones generales del formulario"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin_estimada')
        
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
            
            # Validar que la duración sea razonable (entre 15 días y 5 años)
            duracion = (fecha_fin - fecha_inicio).days
            if duracion < 15:
                raise ValidationError('El plazo del préstamo es muy corto (mínimo 15 días).')
            
            if duracion > 1825:  # 5 años
                raise ValidationError('El plazo del préstamo es muy largo (máximo 5 años).')
        
        return cleaned_data


class CuotaForm(forms.ModelForm):
    """Formulario mejorado para cuotas individuales"""
    
    class Meta:
        model = Cuota
        fields = ['numero_cuota', 'monto_original', 'interes_normal', 'fecha_pago_esperada', 'pagado']
        widgets = {
            'numero_cuota': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'readonly': True}),
            'monto_original': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'interes_normal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'readonly': True}),
            'fecha_pago_esperada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'numero_cuota': 'Número',
            'monto_original': 'Monto ($)',
            'interes_normal': 'Interés ($)',
            'fecha_pago_esperada': 'Fecha de Pago',
            'pagado': 'Pagada',
        }
    
    def clean_monto_original(self):
        """Validar monto de cuota"""
        monto = self.cleaned_data.get('monto_original')
        
        if monto is None:
            raise ValidationError('El monto es requerido.')
        
        monto = float(monto)
        
        if monto <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
        
        return monto
    
    def clean_fecha_pago_esperada(self):
        """Validar fecha de pago"""
        fecha = self.cleaned_data.get('fecha_pago_esperada')
        
        if not fecha:
            raise ValidationError('La fecha de pago es requerida.')
        
        # Debe ser en el futuro o hoy
        if fecha < datetime.now().date():
            raise ValidationError('La fecha de pago no puede ser en el pasado.')
        
        return fecha
    
    def clean(self):
        """Validaciones generales"""
        cleaned_data = super().clean()
        return cleaned_data


# FormSet para manejar cuotas
CuotaFormSet = forms.formset_factory(CuotaForm, extra=0, can_delete=True)


# ===============================================================================
# FORMULARIOS PARA PRÉSTAMOS RÁPIDOS Y CONFIGURACIÓN
# ===============================================================================

class ConfiguracionForm(forms.ModelForm):
    """Formulario para editar la configuración global del sistema"""
    
    class Meta:
        model = Configuracion
        fields = ['tasa_interes_prestamo_normal', 'tasa_interes_prestamo_rapido', 'tasa_mora_diaria']
        widgets = {
            'tasa_interes_prestamo_normal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 15.00'
            }),
            'tasa_interes_prestamo_rapido': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 20.00'
            }),
            'tasa_mora_diaria': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 2000'
            }),
        }
        labels = {
            'tasa_interes_prestamo_normal': 'Tasa de Interés Préstamo Normal (%)',
            'tasa_interes_prestamo_rapido': 'Tasa de Interés Préstamo Rápido (%)',
            'tasa_mora_diaria': 'Mora Diaria (en dinero)',
        }
    
    def clean_tasa_interes_prestamo_normal(self):
        """Validar tasa de interés normal"""
        tasa = self.cleaned_data.get('tasa_interes_prestamo_normal')
        if tasa is None:
            raise ValidationError('La tasa de interés es requerida.')
        if float(tasa) < 0:
            raise ValidationError('La tasa de interés no puede ser negativa.')
        if float(tasa) > 100:
            raise ValidationError('La tasa de interés no puede ser mayor a 100%.')
        return tasa
    
    def clean_tasa_interes_prestamo_rapido(self):
        """Validar tasa de interés rápido"""
        tasa = self.cleaned_data.get('tasa_interes_prestamo_rapido')
        if tasa is None:
            raise ValidationError('La tasa de interés es requerida.')
        if float(tasa) < 0:
            raise ValidationError('La tasa de interés no puede ser negativa.')
        if float(tasa) > 100:
            raise ValidationError('La tasa de interés no puede ser mayor a 100%.')
        return tasa
    
    def clean_tasa_mora_diaria(self):
        """Validar tasa de mora"""
        tasa = self.cleaned_data.get('tasa_mora_diaria')
        if tasa is None:
            raise ValidationError('La mora diaria es requerida.')
        if float(tasa) < 0:
            raise ValidationError('La mora diaria no puede ser negativa.')
        return tasa


class PrestamoRapidoForm(forms.ModelForm):
    """Formulario para crear/editar préstamos rápidos"""

    usar_cuotas = forms.BooleanField(
        required=False,
        initial=True,
        label='¿Crear en cuotas?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    num_cuotas = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=12,
        initial=2,
        label='Número de cuotas',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '12',
            'step': '1',
            'placeholder': 'Ej: 2'
        })
    )
    
    class Meta:
        model = PrestamoRapido
        fields = ['monto', 'interes_porcentaje', 'fecha_vencimiento', 'notas']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Monto del préstamo'
            }),
            'interes_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Porcentaje de interés (%)'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Fecha de vencimiento'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)...'
            }),
        }
        labels = {
            'monto': 'Monto del Préstamo',
            'interes_porcentaje': 'Tasa de Interés (%)',
            'fecha_vencimiento': 'Fecha de Vencimiento (opcional)',
            'notas': 'Notas',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_vencimiento'].required = False
        self.fields['notas'].required = False
        
        # Si estamos editando, llenar automáticamente el interés si viene de configuración
        if not self.instance.pk:
            try:
                from .models import Configuracion
                config = Configuracion.obtener_configuracion()
                self.fields['interes_porcentaje'].initial = config.tasa_interes_prestamo_rapido
                self.fields['num_cuotas'].initial = max(int(config.cuotas_por_defecto or 1), 1)
            except:
                pass
    
    def clean_monto(self):
        """Validar monto"""
        monto = self.cleaned_data.get('monto')
        if monto is None:
            raise ValidationError('El monto es requerido.')
        if float(monto) <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
        if float(monto) > 100000000:
            raise ValidationError('El monto no puede ser mayor a 100,000,000.')
        return monto
    
    def clean_interes_porcentaje(self):
        """Validar interés"""
        interes = self.cleaned_data.get('interes_porcentaje')
        if interes is None:
            raise ValidationError('El interés es requerido.')
        if float(interes) < 0:
            raise ValidationError('El interés no puede ser negativo.')
        if float(interes) > 100:
            raise ValidationError('El interés no puede ser mayor a 100%.')
        return interes
    
    def clean_fecha_vencimiento(self):
        """Validar fecha de vencimiento"""
        fecha = self.cleaned_data.get('fecha_vencimiento')
        if fecha and fecha < datetime.now().date():
            raise ValidationError('La fecha de vencimiento no puede ser en el pasado.')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        usar_cuotas = cleaned_data.get('usar_cuotas')
        num_cuotas = cleaned_data.get('num_cuotas')

        if usar_cuotas and not num_cuotas:
            self.add_error('num_cuotas', 'Debe indicar cuántas cuotas desea generar.')

        if not usar_cuotas:
            cleaned_data['num_cuotas'] = None

        return cleaned_data


class PagoPrestamoRapidoForm(forms.Form):
    """Formulario para registrar pagos de préstamos rápidos"""
    
    monto_pagado = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Monto a pagar'
        }),
        label='Monto a Pagar'
    )
    usuario_registra = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario que registra (opcional)'
        }),
        label='Usuario que Registra'
    )
    referencia = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Referencia/Comprobante (opcional)'
        }),
        label='Referencia'
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas adicionales (opcional)...'
        }),
        label='Notas'
    )
    
    def clean_monto_pagado(self):
        """Validar monto"""
        monto = self.cleaned_data.get('monto_pagado')
        if monto is None or float(monto) <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
        return monto
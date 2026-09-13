#!/usr/bin/env python
"""
🔍 AUDITORÍA PROFUNDA TOTAL - BÚSQUEDA DE TODAS LAS INCONSISTENCIAS
======================================================================
Detecta configuraciones, lógica duplicada, hardcodes, vistas sin protección,
campos/métodos no usados, cálculos inconsistentes, y mucho más
"""

import os
import re
import django
from datetime import date
from decimal import Decimal
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion, PrestamoRapido
from django.db.models import Sum, Count, Q
from django.db import models as django_models

# ===============================================================================
# UTILIDADES
# ===============================================================================

class Issues:
    total = 0
    por_categoria = defaultdict(list)
    
    @classmethod
    def agregar(cls, categoria, mensaje):
        cls.por_categoria[categoria].append(mensaje)
        cls.total += 1

def imprimir_header(texto):
    print(f"\n{'='*120}")
    print(f"{texto:^120}")
    print(f"{'='*120}\n")

def imprimir_seccion(texto, nivel=1):
    prefix = "►" * nivel
    print(f"\n{prefix} {texto}")
    print("-" * 120)

def print_ok(texto, indent=0):
    prefix = "  " * indent
    print(f"{prefix}✓ {texto}")

def print_warn(texto, indent=0):
    prefix = "  " * indent
    print(f"{prefix}⚠ {texto}")

def print_error(texto, indent=0):
    prefix = "  " * indent
    print(f"{prefix}✗ {texto}")

def print_info(texto, indent=0):
    prefix = "  " * indent
    print(f"{prefix}ℹ {texto}")

# ===============================================================================
# AUDITORÍA 1: VISTAS SIN PROTECCIÓN @login_required
# ===============================================================================

imprimir_header("AUDITORÍA 1: VISTAS SIN PROTECCIÓN @login_required")

imprimir_seccion("Analizando protección de vistas", 1)

try:
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # Encontrar todas las funciones de vista
    vista_pattern = r"^def (\w+)\(.*?\):"
    vistas = re.findall(vista_pattern, views_content, re.MULTILINE)
    
    vistas_sin_proteccion = []
    
    for vista in vistas:
        # Buscar la vista y ver si tiene @login_required arriba
        # Patrón: buscar @login_required antes de def vista_name
        patron_busqueda = rf"@login_required\s+def {vista}|def {vista}"
        
        # Encontrar la posición de la vista
        pos = views_content.find(f"def {vista}(")
        if pos > 0:
            # Buscar hacia arriba 500 caracteres
            codigo_anterior = views_content[max(0, pos-500):pos]
            
            if '@login_required' not in codigo_anterior:
                vistas_sin_proteccion.append(vista)
                print_error(f"{vista} - NO TIENE @login_required", 1)
                Issues.agregar("Vistas sin protección", f"{vista}: No tiene @login_required")
            else:
                print_ok(f"{vista} - Protegida", 1)
    
    print_info(f"Total vistas sin protección: {len(vistas_sin_proteccion)}", 1)
    
except Exception as e:
    print_error(f"Error analizando vistas: {e}")

# ===============================================================================
# AUDITORÍA 2: MÉTODOS EN MODELOS NO LLAMADOS DESDE NINGÚN LADO
# ===============================================================================

imprimir_header("AUDITORÍA 2: MÉTODOS EN MODELOS NO USADOS EN VISTAS")

imprimir_seccion("Buscando métodos huérfanos", 1)

# Métodos importantes que DEBERÍAN estar en uso
metodos_importantes = {
    'calcular_mora_diaria': ['Cuota', 'models.py'],
    'calcular_monto_pendiente': ['Cuota', 'models.py'],
    'obtener_configuracion': ['Configuracion', 'models.py'],
    'generar_calendario_pagos': ['Prestamo', 'models.py'],
}

try:
    with open('mi_app/models.py', 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    metodos_sin_usar = []
    
    for metodo, info in metodos_importantes.items():
        if metodo in models_content:
            # Verificar si se usa en views
            if metodo in views_content:
                print_ok(f"{metodo} - Usado en views.py", 1)
            else:
                print_error(f"{metodo} - NO USADO en views.py", 1)
                metodos_sin_usar.append(metodo)
                Issues.agregar("Métodos no usados", f"Método {metodo} definido pero no usado en vistas")
    
except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 3: CAMPOS EN MODELOS NO REFLEJADOS EN FORMULARIOS
# ===============================================================================

imprimir_header("AUDITORÍA 3: CAMPOS EN MODELOS vs FORMULARIOS")

imprimir_seccion("Comparando campos de modelos con formularios", 1)

try:
    with open('mi_app/models.py', 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    with open('mi_app/forms.py', 'r', encoding='utf-8') as f:
        forms_content = f.read()
    
    # Buscar campos de Prestamo model
    prestamo_fields_pattern = r"class Prestamo\(.*?\):(.*?)(?=class\s|\Z)"
    prestamo_match = re.search(prestamo_fields_pattern, models_content, re.DOTALL)
    
    if prestamo_match:
        prestamo_content = prestamo_match.group(1)
        campos_prestamo = re.findall(r"(\w+)\s*=\s*models\.", prestamo_content)
        
        print_info("Campos en modelo Prestamo:", 1)
        campos_no_en_form = []
        
        for campo in campos_prestamo:
            if campo not in forms_content:
                print_error(f"{campo} - NO está en PrestamoForm", 2)
                campos_no_en_form.append(campo)
                Issues.agregar("Campos no reflejados", f"Prestamo.{campo}: En modelo pero NO en formulario")
            else:
                print_ok(f"{campo} - En formulario", 2)
        
        print_info(f"Total campos no en formulario: {len(campos_no_en_form)}", 1)

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 4: LÓGICA DE CÁLCULOS DUPLICADA Y/O INCONSISTENTE
# ===============================================================================

imprimir_header("AUDITORÍA 4: LÓGICA DUPLICADA Y CÁLCULOS INCONSISTENTES")

imprimir_seccion("Buscando cálculos repetidos en diferentes lugares", 1)

try:
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    with open('mi_app/models.py', 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    # Buscar patrones de cálculos
    calculos = {
        'monto_pendiente': r"monto_pendiente\s*=|monto_original\s*-\s*monto_pagado",
        'mora': r"mora\s*=|dias.*?\*.*?2000|\*.*?2000",
        'interes': r"interes\s*=|monto.*?\*.*?interes",
        'total_pagable': r"total_pagable\s*=|monto_original\s*\+\s*interes",
    }
    
    for calculo, patron in calculos.items():
        ocurrencias_models = len(re.findall(patron, models_content, re.IGNORECASE))
        ocurrencias_views = len(re.findall(patron, views_content, re.IGNORECASE))
        
        print_info(f"{calculo}:", 1)
        print_info(f"Apariciones en models.py: {ocurrencias_models}", 2)
        print_info(f"Apariciones en views.py: {ocurrencias_views}", 2)
        
        if ocurrencias_views > 2:
            print_error(f"LÓGICA DUPLICADA: Se repite {ocurrencias_views}x en views.py", 2)
            Issues.agregar("Lógica duplicada", f"Cálculo de {calculo} repetido {ocurrencias_views}x en views.py")

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 5: ATRIBUTOS HARDCODEADOS EN VISTAS/TEMPLATES
# ===============================================================================

imprimir_header("AUDITORÍA 5: VALORES HARDCODEADOS EN VISTAS Y TEMPLATES")

imprimir_seccion("Buscando números mágicos", 1)

hardcodes_patterns = {
    '2000': 'Mora diaria',
    '30.00': 'Tasa interés normal',
    '12.00': 'Tasa interés rápido',
    '0.30': 'Interés como decimal',
    '5_21': 'Calendario quincena',
    '15_30': 'Calendario segundo quincena',
}

try:
    archivos = [
        ('mi_app/views.py', 'views'),
        ('mi_app/models.py', 'models'),
        ('mi_app/forms.py', 'forms'),
    ]
    
    for filepath, nombre in archivos:
        print_info(f"\nArchivo: {nombre}.py", 1)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        hardcodes_encontrados = defaultdict(list)
        
        for valor, descripcion in hardcodes_patterns.items():
            for i, linea in enumerate(lineas, 1):
                if valor in linea and 'config' not in linea.lower():
                    hardcodes_encontrados[descripcion].append((i, linea.strip()[:100]))
        
        if hardcodes_encontrados:
            for desc, ocurrencias in hardcodes_encontrados.items():
                print_error(f"{desc}: {len(ocurrencias)} veces", 2)
                for linea_num, contenido in ocurrencias[:2]:
                    print_info(f"Línea {linea_num}: {contenido}", 3)
                Issues.agregar("Hardcodes", f"{nombre}.py: {desc} hardcodeado {len(ocurrencias)}x")

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 6: CONFIGURACIÓN GUARDADA PERO NO USADA
# ===============================================================================

imprimir_header("AUDITORÍA 6: CONFIGURACIÓN GUARDADA PERO NO USADA")

imprimir_seccion("Verificando uso de cada campo de Configuracion", 1)

try:
    config = Configuracion.obtener_configuracion()
    
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # Campos de configuración
    campos_config = [
        'tasa_interes_prestamo_normal',
        'tasa_interes_prestamo_rapido',
        'tasa_mora_diaria',
        'cuotas_por_defecto',
    ]
    
    campos_no_usados = []
    
    for campo in campos_config:
        valor = getattr(config, campo, None)
        print_info(f"{campo}: {valor}", 1)
        
        if campo in views_content:
            print_ok(f"  Usado en views.py", 2)
        else:
            print_error(f"  NO USADO en views.py", 2)
            campos_no_usados.append(campo)
            Issues.agregar("Config no usada", f"Configuracion.{campo}: Definido pero no usado en views")
    
    print_info(f"Total campos no usados: {len(campos_no_usados)}", 1)

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 7: INCONSISTENCIAS EN DATOS (Préstamos vs Cuotas vs Pagos)
# ===============================================================================

imprimir_header("AUDITORÍA 7: INCONSISTENCIAS DE DATOS")

imprimir_seccion("Validando coherencia de datos en BD", 1)

inconsistencias_datos = 0

# Auditoría de Préstamos
print_info("Analizando Préstamos:", 1)
for prestamo in Prestamo.objects.all()[:20]:
    # ¿Suma de cuotas = monto total?
    suma_cuotas = sum(Decimal(str(c.monto_original)) for c in prestamo.cuotas.all())
    
    if abs(suma_cuotas - prestamo.monto_total) > Decimal('0.01'):
        print_error(f"Prestamo #{prestamo.id}: Suma cuotas ${suma_cuotas} ≠ Monto ${prestamo.monto_total}", 2)
        Issues.agregar("Inconsistencia datos", f"Prestamo {prestamo.id}: Suma cuotas inconsistente")
        inconsistencias_datos += 1
    
    # ¿Tasa coincide con config? (si es nuevo)
    dias_antiguedad = (date.today() - prestamo.fecha_creacion.date()).days
    if dias_antiguedad < 7:  # Si es reciente
        if float(prestamo.interes_porcentaje) != 30.0 and float(prestamo.interes_porcentaje) != 12.0:
            if 'rapido' not in prestamo.tipo.lower():
                print_warn(f"Prestamo #{prestamo.id}: Tasa {prestamo.interes_porcentaje}% inusual", 2)

print_info(f"Total inconsistencias encontradas: {inconsistencias_datos}", 1)

# ===============================================================================
# AUDITORÍA 8: VISTAS QUE MANIPULAN DATOS PERO USAN LÓGICA DUPLICADA
# ===============================================================================

imprimir_header("AUDITORÍA 8: FUNCIONES MANIPULANDO DATOS DE FORMA INCONSISTENTE")

imprimir_seccion("Buscando manipulaciones de datos en vistas", 1)

try:
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # Buscar funciones que crean/actualizan cuotas
    funciones_criticas = [
        'crear_prestamo',
        'registrar_pago',
        'editar_cliente',
    ]
    
    for func in funciones_criticas:
        if func in views_content:
            # Buscar la función
            patron = rf"def {func}\(.*?\):(.*?)(?=\ndef|\Z)"
            match = re.search(patron, views_content, re.DOTALL)
            
            if match:
                contenido_func = match.group(1)
                
                # Contar operaciones
                operaciones_db = len(re.findall(r"\.save\(\)|\.create\(|\.update\(", contenido_func))
                lineas = len(contenido_func.split('\n'))
                
                print_info(f"{func}:", 1)
                print_info(f"  Líneas: {lineas}", 2)
                print_info(f"  Operaciones BD: {operaciones_db}", 2)
                
                if operaciones_db > 5:
                    print_warn(f"  Muchas operaciones de BD - considerar refactorizar", 2)
                    Issues.agregar("Complejidad", f"Vista {func}: {operaciones_db} operaciones BD (muy complicada)")

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 9: CAMPOS EN FORMULARIOS NO GUARDADOS EN BD
# ===============================================================================

imprimir_header("AUDITORÍA 9: CAMPOS EN FORMULARIOS NO PROCESADOS EN VISTAS")

imprimir_seccion("Comparando formularios con guardar en BD", 1)

try:
    with open('mi_app/forms.py', 'r', encoding='utf-8') as f:
        forms_content = f.read()
    
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # Buscar campos en ConfiguracionForm
    config_form_pattern = r"class ConfiguracionForm.*?fields\s*=\s*\[(.*?)\]"
    config_form_match = re.search(config_form_pattern, forms_content, re.DOTALL)
    
    if config_form_match:
        campos_str = config_form_match.group(1)
        campos = [c.strip().strip("'\"") for c in campos_str.split(',') if c.strip()]
        
        print_info("Campos en ConfiguracionForm:", 1)
        campos_sin_procesar = []
        
        for campo in campos:
            print_info(f"{campo}", 2)
            
            # Buscar si se procesa en la vista
            patron_save = rf"config\.{campo}\s*=|\.{campo}\s*=\s*form\.cleaned"
            
            if re.search(patron_save, views_content):
                print_ok(f"  Procesado en views", 3)
            else:
                print_error(f"  NO PROCESADO en views", 3)
                campos_sin_procesar.append(campo)
                Issues.agregar("Form no procesado", f"ConfiguracionForm.{campo}: En form pero no procesado")
        
        print_info(f"Total campos no procesados: {len(campos_sin_procesar)}", 1)

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 10: ESTADOS DE OBJETOS NO SINCRONIZADOS
# ===============================================================================

imprimir_header("AUDITORÍA 10: ESTADOS DE OBJETOS DESINCRONIZADOS")

imprimir_seccion("Validando coherencia de estados (pagado, estado, etc)", 1)

inconsistencias_estado = 0

print_info("Analizando Cuotas:", 1)
for cuota in Cuota.objects.all()[:30]:
    # Si está marcada como pagada, debería tener monto_pagado = monto_original + interés
    total_pagable = cuota.monto_original + cuota.interes_normal
    total_pagado = cuota.monto_pagado_principal + cuota.monto_pagado_interes
    
    if cuota.pagado:
        # Debería estar completamente pagada
        if abs(total_pagado - total_pagable) > Decimal('0.01'):
            print_error(f"Cuota #{cuota.numero_cuota}: Marcada PAGADA pero pagado ${total_pagado} ≠ pagable ${total_pagable}", 2)
            Issues.agregar("Estado desincronizado", f"Cuota {cuota.id}: Marcada pagada pero incompleta")
            inconsistencias_estado += 1
    else:
        # Si NO está pagada, no debería tener más pagado que el monto
        if total_pagado > total_pagable:
            print_error(f"Cuota #{cuota.numero_cuota}: NO pagada pero tiene pagos ${total_pagado} > ${total_pagable}", 2)
            Issues.agregar("Estado desincronizado", f"Cuota {cuota.id}: Pagos inconsistentes con estado")
            inconsistencias_estado += 1

print_info(f"Total inconsistencias de estado: {inconsistencias_estado}", 1)

# ===============================================================================
# AUDITORÍA 11: LÓGICA EN TEMPLATES NO REFLEJADA EN VISTAS
# ===============================================================================

imprimir_header("AUDITORÍA 11: TEMPLATES CON LÓGICA COMPLEJA NO REFLEJADA EN VISTAS")

imprimir_seccion("Analizando templates para lógica huérfana", 1)

try:
    templates_dir = 'mi_app/templates/mi_app'
    
    if os.path.exists(templates_dir):
        for template_file in os.listdir(templates_dir):
            if template_file.endswith('.html'):
                with open(os.path.join(templates_dir, template_file), 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Buscar lógica compleja en templates
                if 'if' in template_content.lower() and 'endif' not in template_content:
                    # Contar condicionales
                    condicionales = len(re.findall(r"{%\s*if", template_content))
                    
                    if condicionales > 5:
                        print_warn(f"{template_file}: {condicionales} condicionales (considerar simplificar)", 2)
                        Issues.agregar("Template complejo", f"{template_file}: Mucha lógica en template ({condicionales} ifs)")

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# AUDITORÍA 12: CAMPOS DE MODELO NUNCA ACTUALIZADOS
# ===============================================================================

imprimir_header("AUDITORÍA 12: CAMPOS EN MODELOS NUNCA ACTUALIZADOS")

imprimir_seccion("Buscando campos que nunca cambian", 1)

try:
    with open('mi_app/models.py', 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # Campos que podrían no usarse
    campos_potencial = [
        'fecha_ultima_modificacion',
        'notas',
        'comentarios',
        'estado_cliente',
        'referencia_externa',
    ]
    
    campos_no_actualizados = []
    
    for campo in campos_potencial:
        if campo in models_content:
            # Buscar si se actualiza en views
            patron_actualizar = rf"\.{campo}\s*=|{campo}\s*=\s*"
            
            if not re.search(patron_actualizar, views_content):
                print_error(f"{campo}: NUNCA se actualiza en views", 2)
                campos_no_actualizados.append(campo)
                Issues.agregar("Campo no actualizado", f"Modelo.{campo}: Definido pero nunca actualizado")
            else:
                print_ok(f"{campo}: Se actualiza en views", 2)

except Exception as e:
    print_error(f"Error: {e}")

# ===============================================================================
# REPORTE FINAL RESUMIDO
# ===============================================================================

imprimir_header("REPORTE FINAL - TODAS LAS INCONSISTENCIAS")

print_info(f"Total de inconsistencias encontradas: {Issues.total}", 0)
print()

for categoria in sorted(Issues.por_categoria.keys()):
    problemas = Issues.por_categoria[categoria]
    print_error(f"{categoria}: {len(problemas)} problemas", 1)
    
    for i, problema in enumerate(problemas[:3], 1):
        print_info(f"{i}. {problema}", 2)
    
    if len(problemas) > 3:
        print_info(f"... y {len(problemas) - 3} más", 2)
    print()

imprimir_header("FIN DE AUDITORÍA PROFUNDA TOTAL")

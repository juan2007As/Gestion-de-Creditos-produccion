#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para agregar @login_required a todas las vistas que no lo tengan
"""
import re

# Leer el archivo
with open('mi_app/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Lista de todas las funciones de vista (excepto login/logout que ya están protegidas)
# Buscar patrones: def nombre_vista(request o def nombre_vista(request,
pattern_vistas = r'^((?:@[^\n]+\n)*)def\s+(\w+)\s*\(request'

# Encontrar todas las funciones de vista
matches = list(re.finditer(pattern_vistas, content, re.MULTILINE))

# Contador de protecciones agregadas
count = 0

# Procesar de atrás hacia adelante para no mover índices
for match in reversed(matches):
    full_match = match.group(0)
    decorators = match.group(1)
    func_name = match.group(2)
    
    # Funciones a NO proteger (ya están protegidas o son auxiliares)
    skip_functions = {
        'login_view', 'logout_view',  # Ya protegidas
        'obtener_estadisticas_sistema', 'calcular_fecha_pago_esperada',  # Auxiliares
        '_obtener_estado_visual_cuota',  # Auxiliares privadas
    }
    
    if func_name in skip_functions:
        continue
    
    # Si ya tiene @login_required, saltar
    if '@login_required' in decorators:
        continue
    
    # Agregar el decorador
    new_decorators = decorators + "@login_required(login_url='login')\n"
    new_match = new_decorators + "def " + func_name + "(request"
    
    # Reemplazar en el contenido
    content = content.replace(full_match, new_match, 1)
    count += 1
    print(f"✓ Protegido: {func_name}")

# Escribir el archivo actualizado
with open('mi_app/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total de vistas protegidas: {count}")
print("✅ Archivo guardado correctamente")

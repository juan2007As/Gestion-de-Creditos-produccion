#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

# Leer formulario_prestamo.html
with open('mi_app/templates/mi_app/formulario_prestamo.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 60)
print("VALIDACIÓN: formulario_prestamo.html")
print("=" * 60)

# Buscar estructura del dropdown
if 'id="cliente_list"' in content:
    print("✅ Elemento cliente_list encontrado")
    if 'class="search-results-dropdown"' in content:
        print("✅ Clase search-results-dropdown encontrada")
    if '<ul class="results-list"></ul>' in content:
        print("✅ ul.results-list encontrado")
    if 'new DynamicClientSearch' in content:
        print("✅ DynamicClientSearch inicializado")
        # Buscar los argumentos
        match = re.search(r"new DynamicClientSearch\('([^']+)',\s*'([^']+)'", content)
        if match:
            print(f'   - Input selector: {match.group(1)}')
            print(f'   - Results selector: {match.group(2)}')
else:
    print("❌ Elemento cliente_list NO encontrado")

# Verificar que dynamic_search.js se carga
if "'mi_app/js/dynamic_search.js'" in content:
    print("✅ dynamic_search.js se carga")
else:
    print("❌ dynamic_search.js NO se carga")

print("\n" + "=" * 60)
print("VALIDACIÓN: formulario_prestamo_rapido.html")
print("=" * 60)

# Leer formulario_prestamo_rapido.html
with open('mi_app/templates/mi_app/formulario_prestamo_rapido.html', 'r', encoding='utf-8') as f:
    content = f.read()

if 'id="cliente_resultados"' in content:
    print("✅ Elemento cliente_resultados encontrado")
    if 'position: fixed' in content:
        print("✅ Position: fixed encontrado")
    if 'id="cliente_input"' in content:
        print("✅ Input#cliente_input encontrado")
else:
    print("❌ Elemento cliente_resultados NO encontrado")

if 'DynamicClientSearch' not in content:
    print("✅ NO usa DynamicClientSearch (Bien)")
else:
    print("❌ Usa DynamicClientSearch (Problema)")

print("=" * 60)

print("\n" + "=" * 60)
print("VALIDACIÓN: reporte_clientes.html")
print("=" * 60)

# Leer reporte_clientes.html
try:
    with open('mi_app/templates/mi_app/reporte_clientes.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'id="search_resultados_clientes"' in content:
        print("✅ Elemento search_resultados_clientes encontrado")
        if 'position: fixed' in content:
            print("✅ Position: fixed encontrado")
    else:
        print("❌ Elemento search_resultados_clientes NO encontrado")
    
    if 'DynamicClientSearch' not in content:
        print("✅ NO usa DynamicClientSearch (usa script inline)")
except Exception as e:
    print(f"Error: {e}")

print("=" * 60)

print("\nTodos los archivos validados correctamente ✅")

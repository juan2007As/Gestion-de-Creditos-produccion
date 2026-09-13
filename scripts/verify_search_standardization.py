#!/usr/bin/env python
"""
Script de verificación post-actualización
Verifica que todos los templates usen el nuevo sistema unificado de búsqueda
"""

import os
import re
from pathlib import Path

# Directorio de templates
TEMPLATES_DIR = Path("mi_app/templates/mi_app")

# Templates que DEBEN tener búsqueda dinámica
SEARCH_TEMPLATES = [
    "formulario_prestamo.html",
    "formulario_prestamo_rapido.html",
    "reporte_clientes.html",
    "lista_clientes.html",
    "buscar_cliente_pago.html",
    "clientes_importados.html",
    "lista_prestamos_rapidos.html",
    "reporte_prestamos.html",
    "reporte_cuotas.html",
    "reporte_cuotas_vencidas.html",
]

def check_template(template_name):
    """Verifica que un template use los IDs estándar"""
    template_path = TEMPLATES_DIR / template_name
    
    if not template_path.exists():
        return f"❌ {template_name}: NO EXISTE"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = []
    
    # Verificar IDs estándar
    has_search_input = 'id="search_input"' in content
    has_search_results = 'id="search_results"' in content
    has_search_event = 'searchSelected' in content
    
    # Verificar que NO tenga IDs viejos
    no_old_search_ids = all([
        'id="cliente_search"' not in content,
        'id="clientSearch"' not in content,
        'id="cliente_busqueda"' not in content,
        'id="search_cuotas"' not in content,
        'id="search_prestamos"' not in content,
        'id="search_clientes"' not in content,
        'id="search_cuotas_clientes"' not in content,
        'id="search_lista"' not in content,
    ])
    
    all_good = has_search_input and has_search_results and has_search_event and no_old_search_ids
    
    status = "✅" if all_good else "❌"
    
    details = []
    if has_search_input:
        details.append("✓ id='search_input'")
    else:
        details.append("✗ id='search_input' FALTA")
    
    if has_search_results:
        details.append("✓ id='search_results'")
    else:
        details.append("✗ id='search_results' FALTA")
    
    if has_search_event:
        details.append("✓ searchSelected event")
    else:
        details.append("✗ searchSelected event FALTA")
    
    if no_old_search_ids:
        details.append("✓ Sin IDs viejos")
    else:
        details.append("✗ CONTIENE IDs VIEJOS")
    
    return f"{status} {template_name}\n      {' | '.join(details)}"

def check_base_html():
    """Verifica que base.html cargue el nuevo script"""
    base_path = TEMPLATES_DIR / "base.html"
    
    if not base_path.exists():
        return "❌ base.html: NO EXISTE"
    
    with open(base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_unified_search = 'unified_search.js' in content
    has_search_css = '#search_results' in content or '#search_input' in content
    
    all_good = has_unified_search and has_search_css
    status = "✅" if all_good else "❌"
    
    details = []
    if has_unified_search:
        details.append("✓ Carga unified_search.js")
    else:
        details.append("✗ NO CARGA unified_search.js")
    
    if has_search_css:
        details.append("✓ Tiene CSS para #search_input/results")
    else:
        details.append("✗ Falta CSS")
    
    return f"{status} base.html\n      {' | '.join(details)}"

def check_unified_search_js():
    """Verifica que el script unified_search.js exista"""
    js_path = Path("mi_app/static/mi_app/js/unified_search.js")
    
    if not js_path.exists():
        return "❌ unified_search.js: NO EXISTE"
    
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_class = 'class UnifiedSearch' in content
    has_init = 'init()' in content
    has_api = '/api/buscar-cliente/' in content
    
    all_good = has_class and has_init and has_api
    status = "✅" if all_good else "❌"
    
    details = []
    if has_class:
        details.append("✓ Clase UnifiedSearch")
    else:
        details.append("✗ Falta clase")
    
    if has_init:
        details.append("✓ Método init")
    else:
        details.append("✗ Falta método init")
    
    if has_api:
        details.append("✓ API endpoint correcto")
    else:
        details.append("✗ Falta API endpoint")
    
    return f"{status} unified_search.js\n      {' | '.join(details)}"

def main():
    print("=" * 70)
    print("VERIFICACIÓN POST-ACTUALIZACIÓN - SISTEMA DE BÚSQUEDA UNIFICADO")
    print("=" * 70)
    print()
    
    # Verificar archivos principales
    print("📄 ARCHIVOS CLAVE:")
    print(check_base_html())
    print(check_unified_search_js())
    print()
    
    # Verificar templates
    print("📋 TEMPLATES CON BÚSQUEDA:")
    for template in SEARCH_TEMPLATES:
        print(check_template(template))
    
    print()
    print("=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    main()

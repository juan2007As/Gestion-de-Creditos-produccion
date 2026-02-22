#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar dropdowns en templates a la nueva solución estándar
"""

import os
import re

# Ruta base
BASE_PATH = r"c:\Users\Juancho\Desktop\proyecto_john\mi_app\templates\mi_app"

# Templates a actualizar
TEMPLATES = [
    "historico_pagos.html",
    "clientes_importados.html",
    "reporte_prestamos.html",
    "reporte_cuotas_vencidas.html"
]

# CSS VIEJO A REEMPLAZAR (patrones comunes)
OLD_CSS_PATTERNS = [
    r"\.dropdown-results \{[\s\S]*?\}",
    r"\.dropdown-results\.show \{[\s\S]*?\}",
    r"\.dropdown-item \{[\s\S]*?\}",
    r"\.dropdown-item:last-child \{[\s\S]*?\}",
    r"\.dropdown-item:hover \{[\s\S]*?\}",
    r"\.dropdown-item strong \{[\s\S]*?\}",
    r"\.dropdown-item small \{[\s\S]*?\}",
    r"\.no-results \{[\s\S]*?\}",
]

# NUEVO SCRIPT A INYECTAR
NEW_SCRIPT = '''<script>
    /**
     * ✅ NUEVA SOLUCIÓN - DROPDOWN ESTÁNDAR
     * Usa DropdownSearch + initClienteDropdown de base.html
     */
    
    document.addEventListener('DOMContentLoaded', function() {
        // 1. INICIALIZAR DROPDOWN CON NUEVA CLASE
        initClienteDropdown('cliente_search', 'cliente_resultados', {
            onAfterSelect: function(cliente) {
                // Al seleccionar un cliente, aplicar filtros
                aplicarFiltros();
            }
        });

        // 2. EVENT LISTENERS ADICIONALES
        const filterSelects = document.querySelectorAll('[onchange="aplicarFiltros()"]');
        filterSelects.forEach(select => {
            select.addEventListener('change', aplicarFiltros);
        });
    });

    // APLICAR FILTROS
    function aplicarFiltros() {
        // Obtener filtros activos
        const filtros = {};
        document.querySelectorAll('select[name]').forEach(select => {
            if (select.value) {
                filtros[select.name] = select.value;
            }
        });
        
        // Obtener cliente seleccionado
        const clienteSeleccionado = getSelectedCliente('cliente_search');
        const clienteNombre = clienteSeleccionado.nombre.toLowerCase();
        
        let filasVisibles = 0;
        const rows = document.querySelectorAll('.cliente-row');

        rows.forEach(row => {
            let mostrar = true;

            // Filtro por cliente
            if (clienteNombre) {
                const nombre = row.dataset.nombre || '';
                const cedula = row.dataset.cedula || '';
                const celular = row.dataset.celular || '';
                
                if (!nombre.includes(clienteNombre) && 
                    !cedula.includes(clienteNombre) && 
                    !celular.includes(clienteNombre)) {
                    mostrar = false;
                }
            }

            // Aplicar otros filtros basados en data-attributes
            for (const [key, value] of Object.entries(filtros)) {
                if (!mostrar) break;
                
                const dataKey = key.replace('filtro_', '');
                const rowValue = row.dataset[dataKey] || '';
                
                // Mapeo de valores si es necesario
                const valueMap = {
                    'PENDIENTE': 'pendiente',
                    'PARCIALMENTE_PAGADO': 'parcial',
                    'PAGADO': 'pagado'
                };
                
                const mappedValue = valueMap[value] || value;
                if (rowValue !== mappedValue && mappedValue !== value) {
                    mostrar = false;
                }
            }

            if (mostrar) {
                row.classList.remove('hidden');
                filasVisibles++;
            } else {
                row.classList.add('hidden');
            }
        });

        // Mostrar mensaje si no hay resultados
        const tbody = document.querySelector('tbody');
        if (!tbody) return;
        
        let noResults = tbody.querySelector('.no-results');
        
        if (filasVisibles === 0 && !noResults) {
            noResults = document.createElement('tr');
            noResults.className = 'no-results';
            noResults.innerHTML = '<td colspan="10" class="text-center text-muted py-4">No se encontraron resultados con los filtros seleccionados</td>';
            tbody.appendChild(noResults);
        } else if (filasVisibles > 0 && noResults) {
            noResults.remove();
        }
    }

    // LIMPIAR FILTROS
    function limpiarFiltros() {
        clearClienteSelection('cliente_search');
        document.querySelectorAll('select[name]').forEach(select => {
            select.value = '';
        });
        document.querySelectorAll('input[type="hidden"]').forEach(input => {
            input.value = '';
        });
        
        document.querySelectorAll('.cliente-row').forEach(row => {
            row.classList.remove('hidden');
        });
        
        const noResults = document.querySelector('.no-results');
        if (noResults) noResults.remove();
    }
</script>'''

def update_template(filepath):
    """Actualizar un template individual"""
    print(f"✏️  Actualizando {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Reemplazar CSS antiguo
    # Buscar y reemplazar estilos deprecated del dropdown
    old_css_full = re.search(r"/\* Dropdown Results \*/([\s\S]*?)\.no-results \{[^}]*\}", content)
    
    if old_css_full:
        new_css = """/* Dropdown Results */
    /* Nota: Los estilos del dropdown ahora vienen de dropdown-search.js */
    /* Que es aplicado dinámicamente en base.html */"""
        
        content = content.replace(old_css_full.group(0), "/* Dropdown Results */\n    /* Nota: Los estilos del dropdown ahora vienen de dropdown-search.js */\n    /* Que es aplicado dinámicamente en base.html */")
    
    # 2. Reemplazar SCRIPT antiguo
    # Buscar patrón: desde "// Cargar clientes" hasta el final del script
    old_script_pattern = r"<script>([\s\S]*?)// Cargar clientes del API([\s\S]*?)<\/script>"
    
    matches = list(re.finditer(old_script_pattern, content))
    
    if matches:
        match = matches[-1]  # Tomar el último match
        start = content.rfind("<script>", 0, match.start())
        end = content.find("</script>", match.end()) + len("</script>")
        
        if start >= 0 and end > start:
            # Extraer la línea de estilos (si la hay)
            style_part = content[match.start():match.start()+100]
            
            new_content = content[:start] + NEW_SCRIPT + content[end:]
            content = new_content
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {os.path.basename(filepath)} actualizado correctamente!")
    return True

# Procesar todos los templates
for template_name in TEMPLATES:
    filepath = os.path.join(BASE_PATH, template_name)
    if os.path.exists(filepath):
        try:
            update_template(filepath)
        except Exception as e:
            print(f"❌ Error en {template_name}: {e}")
    else:
        print(f"⚠️  {template_name} no encontrado en {BASE_PATH}")

print("\n✅ Actualización completada!")

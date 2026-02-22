#!/usr/bin/env python
import re

# Listas de vistas que necesitan protección
vistas_necesitan_proteccion = [
    'buscar_cliente_pago',
    'cuotas_pendientes', 
    'registrar_pago',
    'perfil_cliente',
    'mis_prestamos',
    'detalles_prestamo',
    'detalles_cuota',
    'registrar_pago_mejorado',
    'reporte_clientes',
    'reporte_prestamos',
    'reporte_cuotas_vencidas',
    'reporte_estadisticas',
    'importar_excel',
    'exportar_clientes_excel',
    'exportar_prestamos_excel',
    'exportar_cuotas_excel',
    'crear_prestamo_rapido',
    'detalle_prestamo_rapido',
    'listar_prestamos_rapidos',
    'registrar_pago_rapido',
    'editar_configuracion'
]

with open('mi_app/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Procesar cada línea
modified_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Buscar si esta línea es un def de una vista que necesita protección
    for vista in vistas_necesitan_proteccion:
        if re.match(rf'^def {vista}\(', line.strip()):
            # Verificar si la línea anterior ya tiene @login_required
            if modified_lines and '@login_required' not in modified_lines[-1]:
                # Agregar decorador antes del def
                indent = len(line) - len(line.lstrip())
                modified_lines.append(' ' * indent + "@login_required(login_url='login')\n")
                print(f'✓ Protegido: {vista}')
            break
    
    modified_lines.append(line)
    i += 1

with open('mi_app/views.py', 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)

print('\n✅ Script completado')

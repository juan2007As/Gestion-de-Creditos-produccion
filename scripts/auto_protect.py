import re

vistas = [
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
    content = f.read()

for vista in vistas:
    # Patrón: cualquier cosa seguida de def nombre(
    pattern = rf'^((?:@[^\n]+\n)*)def {vista}\('
    
    # Buscar si ya tiene el decorador
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        prefix = match.group(1)
        if '@login_required' not in prefix:
            # Reemplazar sin el decorador por con el decorador
            old = match.group(0)
            new = f"@login_required(login_url='login')\n{prefix}def {vista}("
            content = content.replace(old, new)
            print(f"✓ {vista}")

with open('mi_app/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Done!")

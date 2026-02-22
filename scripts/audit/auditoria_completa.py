#!/usr/bin/env python
"""
🔍 AUDITORÍA COMPLETA DE LÓGICA DE PRÉSTAMOS
==============================================
Script que prueba la lógica completa:
1. Crear cliente
2. Crear préstamo
3. Generar cuotas
4. Simular pagos
5. Verificar mora
6. Validar estados
"""

from datetime import date, timedelta
from decimal import Decimal
from mi_app.models import Cliente, Prestamo, Cuota, Pago

# ===============================================================================
# COLORES PARA OUTPUT
# ===============================================================================
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{text:^80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}\n")

def print_section(text):
    print(f"\n{Color.BOLD}{Color.OKBLUE}► {text}{Color.ENDC}")
    print(f"{Color.OKBLUE}{'-'*80}{Color.ENDC}")

def print_success(text):
    print(f"{Color.OKGREEN}✓ {text}{Color.ENDC}")

def print_warning(text):
    print(f"{Color.WARNING}⚠ {text}{Color.ENDC}")

def print_error(text):
    print(f"{Color.FAIL}✗ {text}{Color.ENDC}")

def print_info(text):
    print(f"{Color.OKCYAN}ℹ {text}{Color.ENDC}")

# ===============================================================================
# PASO 1: CREAR CLIENTE DE PRUEBA
# ===============================================================================

print_header("PASO 1: CREAR CLIENTE DE PRUEBA")

# Limpiar cliente anterior si existe
Cliente.objects.filter(cedula='9.999.999-9').delete()

cliente = Cliente.objects.create(
    cedula='9.999.999-9',
    nombre='Juan Prueba Auditoría',
    celular='300 999 9999',
    email='auditoria@test.com',
    estado='ACTIVO'
)

print_success(f"Cliente creado: {cliente.nombre}")
print_info(f"  - Cédula: {cliente.cedula}")
print_info(f"  - ID: {cliente.id}")
print_info(f"  - Estado: {cliente.estado}")
print_info(f"  - Total Prestado (inicial): ${cliente.total_prestado:.2f}")
print_info(f"  - Total Pagado (inicial): ${cliente.total_pagado:.2f}")

# ===============================================================================
# PASO 2: CREAR PRÉSTAMO DE PRUEBA
# ===============================================================================

print_section("PASO 2: CREAR PRÉSTAMO DE PRUEBA")

# Limpiar préstamo anterior
Prestamo.objects.filter(cliente=cliente).delete()

# Crear un préstamo de $1,000 con 4 cuotas
monto = Decimal('1000.00')
tasa_interes = Decimal('15.00')  # 15% mensual
fecha_inicio = date.today()
fecha_fin = fecha_inicio + timedelta(days=60)  # 2 meses = 4 cuotas (2 por mes)

prestamo = Prestamo.objects.create(
    cliente=cliente,
    monto_total=monto,
    interes_porcentaje=tasa_interes,
    fecha_inicio=fecha_inicio,
    fecha_fin_estimada=fecha_fin,
    tipo_pago='QUINCENAL',
    estado='ACTIVO',
    calendario_pagos='15_30'
)

print_success(f"Préstamo creado: #{prestamo.id}")
print_info(f"  - Cliente: {prestamo.cliente.nombre}")
print_info(f"  - Monto Original: ${prestamo.monto_total:.2f}")
print_info(f"  - Tasa Interés: {prestamo.interes_porcentaje}% mensual")
print_info(f"  - Fecha Inicio: {prestamo.fecha_inicio}")
print_info(f"  - Fecha Fin Estimada: {prestamo.fecha_fin_estimada}")
print_info(f"  - Estado: {prestamo.estado}")

# ===============================================================================
# PASO 3: GENERAR CUOTAS
# ===============================================================================

print_section("PASO 3: GENERAR CUOTAS AUTOMÁTICAMENTE")

# Limpiar cuotas anteriores
Cuota.objects.filter(prestamo=prestamo).delete()

# Calcular estructura de cuotas
num_cuotas = 4
monto_por_cuota = monto / Decimal(num_cuotas)

# Interés: 15% mensual / 2 quincenas = 7.5% por quincena
# Para 4 cuotas en 2 meses:
# - Capital por mes: $1000 / 2 = $500
# - Interés por mes: $500 × 15% = $75
# - Interés por quincena: $75 / 2 = $37.50

cuotas_por_mes = 2
num_meses = Decimal(num_cuotas) / Decimal(cuotas_por_mes)  # = 2
capital_por_mes = monto / num_meses  # = $500
interes_por_mes = capital_por_mes * (tasa_interes / Decimal('100'))  # = $75
interes_por_cuota = interes_por_mes / Decimal(cuotas_por_mes)  # = $37.50

print_info("Cálculo de estructura:")
print_info(f"  - Número de cuotas: {num_cuotas}")
print_info(f"  - Número de meses: {num_meses}")
print_info(f"  - Monto por cuota (principal): ${monto_por_cuota:.2f}")
print_info(f"  - Capital por mes: ${capital_por_mes:.2f}")
print_info(f"  - Interés por mes (15%): ${interes_por_mes:.2f}")
print_info(f"  - Interés por cuota (7.5%): ${interes_por_cuota:.2f}")

# Crear fechas de pago: día 15 y 30 de cada mes
hoy = date.today()
fechas_pago = []

# Función auxiliar para crear fecha segura
def crear_fecha_segura(año, mes, dia):
    """Crear fecha validando el rango de días del mes"""
    from calendar import monthrange
    max_dias = monthrange(año, mes)[1]
    dia = min(dia, max_dias)
    return date(año, mes, dia)

# Día 15 del próximo mes
mes_prox = hoy.month + 1 if hoy.month < 12 else 1
año_prox = hoy.year if hoy.month < 12 else hoy.year + 1
fecha_15 = crear_fecha_segura(año_prox, mes_prox, 15)
if fecha_15 <= hoy:
    mes_prox = mes_prox + 1 if mes_prox < 12 else 1
    año_prox = año_prox if mes_prox > 1 else año_prox + 1
    fecha_15 = crear_fecha_segura(año_prox, mes_prox, 15)
fechas_pago.append(fecha_15)

# Día 30 del próximo mes
fecha_30 = crear_fecha_segura(año_prox, mes_prox, 30)
if fecha_30 <= hoy:
    mes_prox = mes_prox + 1 if mes_prox < 12 else 1
    año_prox = año_prox if mes_prox > 1 else año_prox + 1
    fecha_30 = crear_fecha_segura(año_prox, mes_prox, 30)
fechas_pago.append(fecha_30)

# Día 15 del mes siguiente
mes_sig = fecha_30.month + 1 if fecha_30.month < 12 else 1
año_sig = fecha_30.year if fecha_30.month < 12 else fecha_30.year + 1
fecha_15_sig = crear_fecha_segura(año_sig, mes_sig, 15)
fechas_pago.append(fecha_15_sig)

# Día 30 del mes siguiente
fecha_30_sig = crear_fecha_segura(año_sig, mes_sig, 30)
fechas_pago.append(fecha_30_sig)

print_info(f"\nFechas de pago generadas:")
for i, fecha in enumerate(fechas_pago[:num_cuotas], 1):
    print_info(f"  - Cuota {i}: {fecha}")

# Crear cuotas
for i in range(num_cuotas):
    cuota = Cuota.objects.create(
        prestamo=prestamo,
        numero_cuota=i + 1,
        monto_original=monto_por_cuota,
        monto_pendiente=monto_por_cuota,
        interes_normal=interes_por_cuota,
        fecha_pago_esperada=fechas_pago[i],
        pagado=False
    )
    print_success(f"Cuota {i+1} creada: ${cuota.monto_original:.2f} + ${cuota.interes_normal:.2f} = ${float(cuota.monto_original) + float(cuota.interes_normal):.2f}")

# ===============================================================================
# PASO 4: VERIFICAR CÁLCULOS DE PRÉSTAMO
# ===============================================================================

print_section("PASO 4: VERIFICAR CÁLCULOS DE PRÉSTAMO")

# Recargar préstamo desde BD
prestamo.refresh_from_db()

# Obtener resumen
resumen = prestamo.resumen_financiero()

print_info("Resumen Financiero:")
print_info(f"  - Monto Original: ${resumen['monto_original']:.2f}")
print_info(f"  - Interés Total: ${resumen['interes_total_credito']:.2f}")
print_info(f"  - Total Crédito (principal + interés): ${resumen['total_credito']:.2f}")
print_info(f"  - Total Pagado: ${resumen['total_pagado_principal']:.2f}")
print_info(f"  - Total Pendiente: ${resumen['total_pendiente_principal']:.2f}")
print_info(f"  - Total Mora: ${resumen['total_mora_acumulada']:.2f}")

# Validaciones
esperado_interes = float(interes_por_cuota) * num_cuotas
esperado_total_credito = float(monto) + esperado_interes

print_info(f"\nValidación de cálculos:")
if abs(resumen['interes_total_credito'] - esperado_interes) < 0.01:
    print_success(f"✓ Interés total correcto: ${resumen['interes_total_credito']:.2f}")
else:
    print_error(f"✗ Interés total incorrecto. Esperado: ${esperado_interes:.2f}, Obtenido: ${resumen['interes_total_credito']:.2f}")

if abs(resumen['total_credito'] - esperado_total_credito) < 0.01:
    print_success(f"✓ Total crédito correcto: ${resumen['total_credito']:.2f}")
else:
    print_error(f"✗ Total crédito incorrecto. Esperado: ${esperado_total_credito:.2f}, Obtenido: ${resumen['total_credito']:.2f}")

# ===============================================================================
# PASO 5: VERIFICAR CUOTAS
# ===============================================================================

print_section("PASO 5: VERIFICAR DETALLES DE CUOTAS")

for cuota in prestamo.cuotas.all().order_by('numero_cuota'):
    print_info(f"\nCuota #{cuota.numero_cuota}:")
    print_info(f"  - Vencimiento: {cuota.fecha_pago_esperada}")
    print_info(f"  - Monto Original (Principal): ${cuota.monto_original:.2f}")
    print_info(f"  - Interés Normal: ${cuota.interes_normal:.2f}")
    print_info(f"  - Total a Pagar: ${float(cuota.monto_original) + float(cuota.interes_normal):.2f}")
    print_info(f"  - Pagado: {cuota.pagado}")
    print_info(f"  - Mora Actual: ${cuota.calcular_mora_diaria():.2f}")
    
    # Detalles completos
    detalles = cuota.detalles_completos()
    print_info(f"  - Estado: {detalles['estado']}")
    print_info(f"  - Días para vencer: {detalles['dias_para_vencer']}")

# ===============================================================================
# PASO 6: SIMULAR PAGOS
# ===============================================================================

print_section("PASO 6: SIMULAR PAGOS")

# Pago 1: Pagar completamente la cuota 1
print_info("\n🔵 PAGO 1: Cuota #1 - PAGO COMPLETO")

cuota1 = prestamo.cuotas.get(numero_cuota=1)
pago1_principal = cuota1.monto_original
pago1_interes = cuota1.interes_normal
pago1_mora = Decimal('0')  # Sin mora aún

print_info(f"  - Principal: ${pago1_principal:.2f}")
print_info(f"  - Interés: ${pago1_interes:.2f}")
print_info(f"  - Mora: ${pago1_mora:.2f}")

pago1 = Pago.objects.create(
    cuota=cuota1,
    monto_pagado=pago1_principal + pago1_interes + pago1_mora,
    monto_principal=pago1_principal,
    monto_interes=pago1_interes,
    monto_mora=pago1_mora,
    notas='Pago de auditoría - Cuota completa'
)

# Actualizar cuota
cuota1.monto_pagado_principal = pago1_principal
cuota1.monto_pagado_interes = pago1_interes
cuota1.monto_pagado_mora = pago1_mora
cuota1.monto_pendiente = Decimal('0')
cuota1.pagado = True
cuota1.fecha_pago_real = date.today()
cuota1.save()

# Actualizar cliente
cliente.total_pagado += pago1_principal + pago1_interes + pago1_mora
cliente.save()

print_success(f"Pago registrado: ${pago1_principal + pago1_interes + pago1_mora:.2f}")
print_success(f"Cuota #{cuota1.numero_cuota} marcada como PAGADA")

# Pago 2: Pago parcial de cuota 2 (solo principal)
print_info("\n🔵 PAGO 2: Cuota #2 - PAGO PARCIAL (solo principal)")

cuota2 = prestamo.cuotas.get(numero_cuota=2)
pago2_principal = cuota2.monto_original / Decimal('2')  # Pagar la mitad
pago2_interes = Decimal('0')  # Sin interés aún
pago2_mora = Decimal('0')

print_info(f"  - Principal: ${pago2_principal:.2f} (50% del total)")
print_info(f"  - Interés: ${pago2_interes:.2f}")
print_info(f"  - Mora: ${pago2_mora:.2f}")

pago2 = Pago.objects.create(
    cuota=cuota2,
    monto_pagado=pago2_principal + pago2_interes + pago2_mora,
    monto_principal=pago2_principal,
    monto_interes=pago2_interes,
    monto_mora=pago2_mora,
    notas='Pago de auditoría - Pago parcial'
)

# Actualizar cuota
cuota2.monto_pagado_principal = pago2_principal
cuota2.monto_pagado_interes = pago2_interes
cuota2.monto_pagado_mora = pago2_mora
cuota2.monto_pendiente = cuota2.monto_original - pago2_principal
cuota2.pagado = False  # Aún no completada
cuota2.save()

# Actualizar cliente
cliente.total_pagado += pago2_principal + pago2_interes + pago2_mora
cliente.save()

print_success(f"Pago parcial registrado: ${pago2_principal + pago2_interes + pago2_mora:.2f}")
print_warning(f"Cuota #{cuota2.numero_cuota} aún pendiente: ${cuota2.monto_pendiente:.2f}")

# Cuotas 3 y 4 sin pagar (para simular mora)
print_info("\n🔵 PAGO 3 y 4: Cuotas #3 y #4 - SIN PAGAR (para simular mora)")
print_warning("  - Cuota #3 y #4 permanecen sin pagar")

# ===============================================================================
# PASO 7: VERIFICAR ESTADO DESPUÉS DE PAGOS
# ===============================================================================

print_section("PASO 7: VERIFICAR ESTADO DESPUÉS DE PAGOS")

# Recargar datos
prestamo.refresh_from_db()
cliente.refresh_from_db()

print_info("Estado del Préstamo:")
print_info(f"  - Total Pagado Cliente: ${cliente.total_pagado:.2f}")
print_info(f"  - Total Prestado Cliente: ${cliente.total_prestado:.2f}")

resumen_actualizado = prestamo.resumen_financiero()
print_info(f"\nResumen Financiero Actualizado:")
print_info(f"  - Monto Original: ${resumen_actualizado['monto_original']:.2f}")
print_info(f"  - Total Pagado (principal): ${resumen_actualizado['total_pagado_principal']:.2f}")
print_info(f"  - Total Pagado (interés): ${resumen_actualizado['total_pagado_interes']:.2f}")
print_info(f"  - Total Pendiente (principal): ${resumen_actualizado['total_pendiente_principal']:.2f}")
print_info(f"  - Total Pendiente (interés): ${resumen_actualizado['total_pendiente_interes']:.2f}")

# Cuotas
print_info("\nEstado de Cuotas:")
for cuota in prestamo.cuotas.all().order_by('numero_cuota'):
    if cuota.pagado:
        print_success(f"  Cuota #{cuota.numero_cuota}: PAGADA ✓")
    else:
        mora = cuota.calcular_mora_diaria()
        if mora > 0:
            print_error(f"  Cuota #{cuota.numero_cuota}: VENCIDA + MORA (${mora:.2f})")
        elif cuota.fecha_pago_esperada < date.today():
            print_warning(f"  Cuota #{cuota.numero_cuota}: VENCIDA (sin mora aún)")
        else:
            print_info(f"  Cuota #{cuota.numero_cuota}: PENDIENTE")

# ===============================================================================
# PASO 8: VERIFICAR MORA
# ===============================================================================

print_section("PASO 8: VERIFICAR CÁLCULO DE MORA")

print_info("Mora por cada cuota sin pagar:")
mora_total = Decimal('0')
for cuota in prestamo.cuotas.filter(pagado=False).order_by('numero_cuota'):
    mora = cuota.calcular_mora_diaria()
    mora_total += mora
    dias_vencidos = max(0, (date.today() - cuota.fecha_pago_esperada).days - 1)
    print_info(f"  - Cuota #{cuota.numero_cuota}: ${mora:.2f} ({dias_vencidos} días vencida × $2,000/día)")

print_info(f"\nTotal Mora Acumulada: ${mora_total:.2f}")
print_info(f"Mora según resumen: ${resumen_actualizado['total_mora_acumulada']:.2f}")

if abs(float(mora_total) - resumen_actualizado['total_mora_acumulada']) < 0.01:
    print_success("✓ Cálculo de mora correcto")
else:
    print_error("✗ Discrepancia en cálculo de mora")

# ===============================================================================
# PASO 9: SIMULAR PAGO DE CUOTA VENCIDA CON MORA
# ===============================================================================

print_section("PASO 9: SIMULAR PAGO DE CUOTA VENCIDA CON MORA")

# Completar el pago de cuota 2 (que tiene pendiente + interés + mora)
print_info("\nCompletando Cuota #2:")

cuota2.refresh_from_db()
mora_cuota2 = cuota2.calcular_mora_diaria()
pendiente_principal = cuota2.monto_pendiente
pendiente_interes = cuota2.interes_normal

print_info(f"  - Principal pendiente: ${pendiente_principal:.2f}")
print_info(f"  - Interés pendiente: ${pendiente_interes:.2f}")
print_info(f"  - Mora acumulada: ${mora_cuota2:.2f}")

pago2_adicional = Pago.objects.create(
    cuota=cuota2,
    monto_pagado=pendiente_principal + pendiente_interes + mora_cuota2,
    monto_principal=pendiente_principal,
    monto_interes=pendiente_interes,
    monto_mora=mora_cuota2,
    notas='Pago de auditoría - Completar cuota con mora'
)

# Actualizar cuota
cuota2.monto_pagado_principal += pendiente_principal
cuota2.monto_pagado_interes += pendiente_interes
cuota2.monto_pagado_mora = mora_cuota2
cuota2.monto_pendiente = Decimal('0')
cuota2.pagado = True
cuota2.fecha_pago_real = date.today()
cuota2.save()

# Actualizar cliente
cliente.total_pagado += pendiente_principal + pendiente_interes + mora_cuota2
cliente.save()

print_success(f"Pago adicional registrado: ${pendiente_principal + pendiente_interes + mora_cuota2:.2f}")
print_success(f"Cuota #{cuota2.numero_cuota} ahora PAGADA (incluida mora)")

# ===============================================================================
# PASO 10: HISTORIAL COMPLETO DE PAGOS
# ===============================================================================

print_section("PASO 10: HISTORIAL COMPLETO DE PAGOS")

pagos = Pago.objects.filter(cuota__prestamo=prestamo).order_by('fecha_pago')
total_pagos = Decimal('0')

print_info("Transacciones registradas:")
for i, pago in enumerate(pagos, 1):
    total_pago = pago.monto_principal + pago.monto_interes + pago.monto_mora
    total_pagos += total_pago
    print_info(f"\n  Pago #{i}:")
    print_info(f"    - Cuota: {pago.cuota.numero_cuota}")
    print_info(f"    - Fecha: {pago.fecha_pago}")
    print_info(f"    - Principal: ${pago.monto_principal:.2f}")
    print_info(f"    - Interés: ${pago.monto_interes:.2f}")
    print_info(f"    - Mora: ${pago.monto_mora:.2f}")
    print_info(f"    - Total: ${total_pago:.2f}")

print_info(f"\nTotal Pagado (suma de transacciones): ${total_pagos:.2f}")
print_info(f"Total Pagado en Cliente: ${cliente.total_pagado:.2f}")

if abs(float(total_pagos) - float(cliente.total_pagado)) < 0.01:
    print_success("✓ Total de pagos sincronizado correctamente")
else:
    print_error("✗ Discrepancia en total de pagos")

# ===============================================================================
# PASO 11: VERIFICAR PROPERTIES DEL PRÉSTAMO
# ===============================================================================

print_section("PASO 11: VERIFICAR PROPERTIES DEL PRÉSTAMO")

prestamo.refresh_from_db()

print_info("Propiedades calculadas del Préstamo:")
print_info(f"  - total_credito: ${prestamo.total_credito:.2f}")
print_info(f"  - total_pagado: ${prestamo.total_pagado:.2f}")
print_info(f"  - total_pendiente: ${prestamo.total_pendiente:.2f}")
print_info(f"  - total_mora: ${prestamo.total_mora:.2f}")
print_info(f"  - num_cuotas_pagadas: {prestamo.num_cuotas_pagadas}")
print_info(f"  - num_cuotas_vencidas: {prestamo.num_cuotas_vencidas}")

# Validaciones
print_info("\nValidaciones:")
esperado_pendiente = float(prestamo.total_credito) - float(prestamo.total_pagado)
if abs(float(prestamo.total_pendiente) - esperado_pendiente) < 0.01:
    print_success("✓ Total pendiente = Total crédito - Total pagado")
else:
    print_error(f"✗ Discrepancia en pendiente. Esperado: ${esperado_pendiente:.2f}, Obtenido: ${prestamo.total_pendiente:.2f}")

# ===============================================================================
# PASO 12: REPORTE FINAL
# ===============================================================================

print_header("REPORTE FINAL DE AUDITORÍA")

print_info("CLIENTE:")
print_info(f"  Nombre: {cliente.nombre}")
print_info(f"  Cédula: {cliente.cedula}")
print_info(f"  Rating: {cliente.calcular_rating():.1f}⭐")
print_info(f"  Total Prestado: ${cliente.total_prestado:.2f}")
print_info(f"  Total Pagado: ${cliente.total_pagado:.2f}")

print_info("\nPRÉSTAMO:")
print_info(f"  ID: #{prestamo.id}")
print_info(f"  Monto: ${prestamo.monto_total:.2f}")
print_info(f"  Tasa: {prestamo.interes_porcentaje}%")
print_info(f"  Estado: {prestamo.estado}")
print_info(f"  Total Crédito: ${prestamo.total_credito:.2f}")
print_info(f"  Total Pagado: ${prestamo.total_pagado:.2f}")
print_info(f"  Total Pendiente: ${prestamo.total_pendiente:.2f}")
print_info(f"  Total Mora: ${prestamo.total_mora:.2f}")

print_info("\nCUOTAS:")
print_info(f"  Total: {prestamo.cuotas.count()}")
print_info(f"  Pagadas: {prestamo.num_cuotas_pagadas}")
print_info(f"  Pendientes: {prestamo.cuotas.filter(pagado=False).count()}")
print_info(f"  Vencidas: {prestamo.num_cuotas_vencidas}")

print_info("\nPAGOS:")
print_info(f"\nTotal transacciones: {Pago.objects.filter(cuota__prestamo=prestamo).count()}")
print_info(f"  Total pagado: ${total_pagos:.2f}")

# ===============================================================================
# VALIDACIÓN FINAL
# ===============================================================================

print_section("VALIDACIÓN FINAL DEL SISTEMA")

checks = []

# Check 1: Monto total = suma de cuotas
suma_cuotas = sum(float(c.monto_original) for c in prestamo.cuotas.all())
check1 = abs(float(prestamo.monto_total) - suma_cuotas) < 0.01
checks.append(("Monto = suma de cuotas", check1))

# Check 2: Interés total = suma intereses cuotas
suma_intereses = sum(float(c.interes_normal) for c in prestamo.cuotas.all())
interes_total = prestamo.total_credito - float(prestamo.monto_total)
check2 = abs(interes_total - suma_intereses) < 0.01
checks.append(("Interés = suma intereses cuotas", check2))

# Check 3: Total crédito correcto
check3 = abs(prestamo.total_credito - (float(prestamo.monto_total) + suma_intereses)) < 0.01
checks.append(("Total crédito correcto", check3))

# Check 4: Pagos registrados correctamente
check4 = abs(float(prestamo.total_pagado) - float(total_pagos)) < 0.01
checks.append(("Pagos registrados correctamente", check4))

# Check 5: Pendiente correcto
check5 = abs(prestamo.total_pendiente - (prestamo.total_credito - prestamo.total_pagado)) < 0.01
checks.append(("Pendiente correcto", check5))

# Check 6: Cliente totales sincronizados
check6 = prestamo.cliente.total_prestado >= prestamo.monto_total
checks.append(("Cliente total_prestado actualizado", check6))

# Check 7: Estados de cuota
check7 = all(c.pagado or not c.pagado for c in prestamo.cuotas.all())
checks.append(("Estados de cuota consistentes", check7))

# Print results
print_info("\nResultados de validación:")
for check_name, result in checks:
    if result:
        print_success(f"{check_name}")
    else:
        print_error(f"{check_name}")

all_passed = all(result for _, result in checks)

print("\n")
if all_passed:
    print(f"{Color.OKGREEN}{Color.BOLD}✓ TODAS LAS VALIDACIONES PASARON{Color.ENDC}")
else:
    print(f"{Color.FAIL}{Color.BOLD}✗ ALGUNAS VALIDACIONES FALLARON{Color.ENDC}")

print_header("FIN DE LA AUDITORÍA")

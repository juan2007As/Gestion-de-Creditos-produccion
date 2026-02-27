import pandas as pd
import os

# Definir los encabezados exactos que el sistema espera leer
# El sistema busca columnas que contengan 'uota', 'interes' y 'echa'
data = {
    'Nombre con responsable': [
        'EJEMPLO: Juan Perez', 
        'EJEMPLO: Maria Lopez (Pendiente)', 
        'EJEMPLO: Carlos Ruiz (Pago Parcial)'
    ],
    'celular': [
        '3001112233', 
        '3104445566', 
        '3207778899'
    ],
    'Monto del préstamo': [
        1000000, 
        500000, 
        800000
    ],
    # Cuota 1
    'Cuota 1': [500000, 250000, 400000],
    'Interes 1': [75000, 37500, 60000],
    'Fecha 1': [
        'enero 15 capital+interes', # PAGADA TOTAL
        'febrero 05',               # PENDIENTE
        'enero 20 capital'          # PAGADO SOLO CAPITAL
    ],
    # Cuota 2
    'Cuota 2': [500000, 250000, 400000],
    'Interes 2': [75000, 37500, 60000],
    'Fecha 2': [
        'febrero 15 capital+interes', 
        '', 
        'febrero 20 interes'        # PAGADO SOLO INTERÉS
    ],
}

# Crear el archivo Excel con dos hojas
nombre_archivo = 'Plantilla_Maestra_Creditos.xlsx'

try:
    with pd.ExcelWriter(nombre_archivo) as writer:
        # Hoja de Préstamos (Principal)
        df_prestamos = pd.DataFrame(data)
        df_prestamos.to_excel(writer, sheet_name='Prestamos', index=False)
        
        # Hoja de Lista Negra (Opcional)
        df_lista_negra = pd.DataFrame({
            'Nombre': ['Ejemplo Usuario Bloqueado'],
            'Celular': ['3110000000']
        })
        df_lista_negra.to_excel(writer, sheet_name='ListaNegra', index=False)
    
    print(f"✅ Archivo '{nombre_archivo}' generado con éxito.")
    print(f"📍 Ubicación: {os.path.abspath(nombre_archivo)}")
    print("\nREGLAS PARA LOS HEADERS:")
    print("1. No cambies 'Nombre con responsable' ni 'celular'.")
    print("2. Las columnas de dinero deben decir 'Cuota' e 'Interes' seguido de un número.")
    print("3. La columna de fecha debe decir 'Fecha' seguido de un número.")
    print("4. Formato de Fecha: 'mes día tipo' (ej: marzo 15 capital+interes).")

except Exception as e:
    print(f"❌ Error al generar la plantilla: {e}")

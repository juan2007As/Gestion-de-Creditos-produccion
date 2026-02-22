import pandas as pd
import os

# Leer el Excel
xlsx_path = r'c:\Users\Juancho\Desktop\Relacion Empresas.xlsx'
csv_path = r'c:\Users\Juancho\Desktop\Relacion Empresas.csv'

try:
    df = pd.read_excel(xlsx_path)
    print("=" * 80)
    print("INFORMACIÓN DEL EXCEL:")
    print("=" * 80)
    print(f"\nTotal de filas: {len(df)}")
    print(f"Total de columnas: {len(df.columns)}")
    print("\nColumnas del Excel:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\n\nPrimeras 2 filas de datos:")
    print("-" * 80)
    for idx, row in df.head(2).iterrows():
        print(f"\nFila {idx + 1}:")
        for col in df.columns:
            print(f"  {col}: {row[col]}")
    
    # Guardar como CSV bien formateado
    df.to_csv(csv_path, index=False, encoding='utf-8-sig', sep=',', quoting=1)
    print("\n" + "=" * 80)
    print(f"✓ CSV guardado correctamente")
    print(f"  Ruta: {csv_path}")
    print(f"  Formato: UTF-8 con BOM")
    print(f"  Delimitador: Coma (,)")
    print(f"  Filas: {len(df)}")
    print(f"  Columnas: {len(df.columns)}")
    print("=" * 80)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

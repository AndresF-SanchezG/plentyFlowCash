import pandas as pd
import os

# Cargar Excel sin encabezados
df = pd.read_excel('Transaction_List_by_Customer.xlsx', header=None)

# Colocar "Customer" en fila 4, columna 0
df.at[4, 0] = "Customer"

# Rellenar los valores NaN en la columna 0 (Customer)
df[0] = df[0].fillna(method='ffill')

# Separar encabezado y contenido
df_part1 = df.iloc[:5]  # Primeras 5 filas (encabezado)
df_part2 = df.iloc[5:]  # Contenido

# Eliminar filas con NaN desde columna 6 en adelante
df_part2 = df_part2.dropna(subset=range(6, df.shape[1]), how='any')

def procesar_filtro(df_base, valores, nombre_hoja):
    df_filtrado = df_base[df_base[6].isin(valores)].copy()
    df_filtrado[7] = pd.to_numeric(df_filtrado[7].astype(str).str.replace(',', '.'), errors='coerce')
    total = df_filtrado[7].sum()

    total_row = pd.Series([None]*df.shape[1])
    total_row[0] = "Total"
    total_row[7] = total

    df_filtrado = pd.concat([df_filtrado, total_row.to_frame().T], ignore_index=True)
    return pd.concat([df_part1, df_filtrado], ignore_index=True), total

# Procesar cada hoja
df_cash_final, total_cash = procesar_filtro(df_part2, ['Cash', 'Cash on hand', 'money order'], "Cash")
df_checking_final, total_checking = procesar_filtro(df_part2, ['CHECK', 'Checking'], "Checking")
df_payments_final, total_payments = procesar_filtro(df_part2, ['Payments to deposit'], "Payments")
df_wire_final, total_wire = procesar_filtro(df_part2, ['WIRE ACCOUNT 3682', 'BUSINESS  3682'], "Wire")
df_zell_final, total_zell = procesar_filtro(df_part2, ['ZELL'], "Zell")

# Ruta de salida
windows_downloads = '/mnt/c/Users/Andres Sanchez/Downloads'
downloads_path = os.path.join(windows_downloads, "Transaction_List_All_Filters.xlsx")

# Guardar todas las hojas en el archivo
with pd.ExcelWriter(downloads_path, engine='openpyxl') as writer:
    df_cash_final.to_excel(writer, index=False, header=False, sheet_name="Cash")
    df_checking_final.to_excel(writer, index=False, header=False, sheet_name="Checking")
    df_payments_final.to_excel(writer, index=False, header=False, sheet_name="Payments")
    df_wire_final.to_excel(writer, index=False, header=False, sheet_name="Wire")
    df_zell_final.to_excel(writer, index=False, header=False, sheet_name="Zell")

print(f"Archivo guardado en: {downloads_path}")

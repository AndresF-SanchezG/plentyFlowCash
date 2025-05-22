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

# Filtrar solo "Cash" y "Cash on hand"
df_part2 = df_part2[df_part2[6].isin(['Cash', 'Cash on hand'])]

# Convertir la columna Amount (columna 7) a número, eliminando comas y tratando errores
df_part2[7] = pd.to_numeric(df_part2[7].astype(str).str.replace(',', '.'), errors='coerce')

# Calcular la suma total de la columna Amount
total_amount = df_part2[7].sum()

# Crear una fila para la suma, con "Total" en la columna 0 y suma en la columna 7
total_row = pd.Series([None]*df.shape[1])
total_row[0] = "Total"
total_row[7] = total_amount

# Añadir la fila al final del dataframe de contenido
df_part2 = pd.concat([df_part2, total_row.to_frame().T], ignore_index=True)

# Unir encabezado + contenido con total
df_filtered = pd.concat([df_part1, df_part2], ignore_index=True)

# Ruta de salida
windows_downloads = '/mnt/c/Users/Andres Sanchez/Downloads'
downloads_path = os.path.join(windows_downloads, "Transaction_List_Cash_Only_with_Total.xlsx")

# Guardar con hoja llamada "Sheet1"
with pd.ExcelWriter(downloads_path, engine='openpyxl') as writer:
    df_filtered.to_excel(writer, index=False, header=False, sheet_name="Sheet1")

print(f"Archivo guardado en: {downloads_path}")

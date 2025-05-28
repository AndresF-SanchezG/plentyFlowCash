import pandas as pd
import os

resumen_totales_customer = {}
resumen_totales_vendor = {}
resumen_totales_vendor_por_proveedor = {}

def procesar_excel(file_path):
    df = pd.read_excel(file_path, header=None)
    df.at[4, 0] = "Customer"
    df[0] = df[0].fillna(method='ffill')
    df_part1 = df.iloc[:5]
    df_part2 = df.iloc[5:]
    df_part2 = df_part2.dropna(subset=range(6, df.shape[1]), how='any')

    

    def procesar_filtro(df_base, valores):
        df_filtrado = df_base[df_base[6].isin(valores)].copy()
        df_filtrado[7] = pd.to_numeric(df_filtrado[7].astype(str).str.replace(',', '.'), errors='coerce')
        total = df_filtrado[7].sum()
        total_row = pd.Series([None]*df.shape[1])
        total_row[0] = "Total"
        total_row[7] = total
        df_filtrado = pd.concat([df_filtrado, total_row.to_frame().T], ignore_index=True)
        return pd.concat([df_part1, df_filtrado], ignore_index=True), total
    

    df_cash_final, total_cash = procesar_filtro(df_part2, ['Cash', 'Cash on hand', 'money order'])
    df_checking_final, total_checking = procesar_filtro(df_part2, ['CHECK', 'Checking'])
    df_payments_final, total_payments = procesar_filtro(df_part2, ['Payments to deposit'])
    df_wire_final, total_wire = procesar_filtro(df_part2, ['WIRE ACCOUNT 3682', 'BUSINESS  3682'])
    df_zell_final, total_zell = procesar_filtro(df_part2, ['ZELL'])

    resumen_totales_customer.clear()
    resumen_totales_customer.update({
            "Cash": total_cash,
            "Check": total_checking,
            "Payments": total_payments,
            "Wire": total_wire,
            "Zell": total_zell
    }) 


    downloads_path = os.path.join('/mnt/c/Users/Andres Sanchez/Downloads', "Transaction_List_All_Filters.xlsx")

    with pd.ExcelWriter(downloads_path, engine='openpyxl') as writer:
        df_cash_final.to_excel(writer, index=False, header=False, sheet_name="Cash")
        df_checking_final.to_excel(writer, index=False, header=False, sheet_name="Checking")
        df_payments_final.to_excel(writer, index=False, header=False, sheet_name="Payments")
        df_wire_final.to_excel(writer, index=False, header=False, sheet_name="Wire")
        df_zell_final.to_excel(writer, index=False, header=False, sheet_name="Zell")

    return downloads_path

def procesar_otro_excel(file_path):
    return f"Se recibió el archivo {os.path.basename(file_path)}, pero no se aplicó el filtro especial."

def procesar_vendors_excel(file_path):
    df = pd.read_excel(file_path, header=None)

    df.at[4, 0] = "Vendor"
    df[0] = df[0].fillna(method='ffill')
    df_part1 = df.iloc[:5]
    df_part2 = df.iloc[5:]

    # Excluir Accounts Payable (A/P)
    df_filtrado = df_part2[df_part2[6] != "Accounts Payable (A/P)"].copy()

    # Eliminar filas con categoría vacía o NaN
    df_filtrado = df_filtrado[df_filtrado[6].notna()]

    # Convertir monto a número y dejarlo negativo si es positivo
    df_filtrado[7] = pd.to_numeric(df_filtrado[7].astype(str).str.replace(',', '.'), errors='coerce')
    df_filtrado[7] = df_filtrado[7].where(df_filtrado[7] < 0, -df_filtrado[7])

    # Crear nueva columna con categoría normalizada
    def normalizar_categoria(valor):
        valor = str(valor).lower().strip()
        if valor in ["cash", "cash on hand", "money order"]:
            return "Cash"
        elif valor in ["check", "checking"]:
            return "Check"
        elif any(w in valor for w in ["wire", "3682", "wiretransfer", "business"]):
            return "Wire"
        elif "credit card" in valor:
            return "Credit Card"
        elif "zell" in valor:
            return "Zell"
        else:
            return valor.title()  # mantiene el resto con formato capitalizado

    df_filtrado['CategoriaNormalizada'] = df_filtrado[6].apply(normalizar_categoria)

    # Agrupar por categoría normalizada
    resumen = df_filtrado.groupby('CategoriaNormalizada')[7].sum().to_dict()

    resumen_totales_vendor.clear()
    resumen_totales_vendor.update(resumen)

    downloads_path = os.path.join('/mnt/c/Users/Andres Sanchez/Downloads', "Transaction_List_by_Vendors_Filtrado.xlsx")

    with pd.ExcelWriter(downloads_path, engine='openpyxl') as writer:
        for tipo, total in resumen.items():
            df_tipo = df_filtrado[df_filtrado['CategoriaNormalizada'] == tipo]
            total_row = pd.Series([None]*df.shape[1])
            total_row[0] = "Total"
            total_row[7] = total
            df_tipo = pd.concat([df_tipo, total_row.to_frame().T], ignore_index=True)
            df_final = pd.concat([df_part1, df_tipo.drop(columns=['CategoriaNormalizada'])], ignore_index=True)
            df_final.to_excel(writer, index=False, header=False, sheet_name=tipo[:31])  # límite de nombre en Excel

    return downloads_path

def procesar_vendors_por_proveedor(file_path):
    df = pd.read_excel(file_path, header=None)

    df.at[4, 0] = "Vendor"
    df[0] = df[0].fillna(method='ffill')
    df_part1 = df.iloc[:5]
    df_part2 = df.iloc[5:]

    # Excluir Accounts Payable (A/P)
    df_filtrado = df_part2[df_part2[6] != "Accounts Payable (A/P)"].copy()
    df_filtrado = df_filtrado[df_filtrado[6].notna()]

    # Convertir montos a negativos
    df_filtrado[7] = pd.to_numeric(df_filtrado[7].astype(str).str.replace(',', '.'), errors='coerce')
    df_filtrado[7] = df_filtrado[7].where(df_filtrado[7] < 0, -df_filtrado[7])

    # Agrupar por proveedor (suma de montos)
    resumen = df_filtrado.groupby(0)[7].sum()

    # Calcular total general (valor absoluto)
    total_general = resumen.abs().sum()

    # Calcular porcentaje por proveedor
    porcentaje = (resumen.abs() / total_general) * 100

    # Crear DataFrame resumen con total y porcentaje
    resumen_df = pd.DataFrame({
    'Proveedor': resumen.index,
    'Total': resumen.values,
    'Porcentaje': porcentaje.values
})
    
    # Convertir Total y Porcentaje a string sin separador de miles
    resumen_df["Total"] = resumen_df["Total"].map(lambda x: f"{x:.2f}".replace(',', ''))
    resumen_df["Porcentaje"] = resumen_df["Porcentaje"].map(lambda x: f"{x:.2f}%")     

    # Ordenar de mayor a menor porcentaje
    resumen_df = resumen_df.sort_values(by='Porcentaje', ascending=False).reset_index(drop=True)

    resumen_totales_vendor_por_proveedor.clear()
    resumen_totales_vendor_por_proveedor.update(resumen.to_dict())

    downloads_path = os.path.join('/mnt/c/Users/Andres Sanchez/Downloads', "Transaction_Vendors_Por_Proveedor_Ordenado.xlsx")

    with pd.ExcelWriter(downloads_path, engine='openpyxl') as writer:
    # Guardar solo el resumen ordenado por proveedor y porcentaje
        resumen_df.to_excel(writer, index=False, sheet_name="Transaction by Vendor Name")

    print(resumen_df.dtypes)

    return downloads_path


    



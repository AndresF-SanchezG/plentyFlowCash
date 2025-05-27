import pandas as pd
import os

resumen_totales = {}

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

    resumen_totales.clear()
    resumen_totales.update({
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



    



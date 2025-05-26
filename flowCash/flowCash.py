from flask import Flask, request, render_template_string
import os
import pandas as pd

app = Flask(__name__)

# HTML para el formulario
html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Plenty APP</title>
</head>
<body>
    <div class="container">
        <h1>PLENTY APP - MODULO ADMINISTRATIVO</h1>
        <h3>Sección: Carga de Reportes</h3>
        <div class="view">
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="excel_file" accept=".xls,.xlsx">
                <input type="submit" value="Subir Excel">
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "excel_file" not in request.files:
        return "No se encontró el archivo", 400

    file = request.files["excel_file"]
    if file.filename == "":
        return "Nombre de archivo vacío", 400

    if file:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        uploaded_path = os.path.join(base_dir, file.filename)
        file.save(uploaded_path)

        try:
            if file.filename == "Transaction_List_by_Customer.xlsx":
                output_path = procesar_excel(uploaded_path)
                return f"Archivo <strong>{file.filename}</strong> procesado exitosamente. Resultado: {output_path}"
            else:
                mensaje = procesar_otro_excel(uploaded_path)
                return f"Archivo <strong>{file.filename}</strong> procesado por otra función. Resultado: {mensaje}"
        except Exception as e:
            return f"Error procesando archivo: {str(e)}", 500

    return "Error al subir el archivo", 500

# Función para Transaction_List_by_Customer.xlsx
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

    df_cash_final, _ = procesar_filtro(df_part2, ['Cash', 'Cash on hand', 'money order'])
    df_checking_final, _ = procesar_filtro(df_part2, ['CHECK', 'Checking'])
    df_payments_final, _ = procesar_filtro(df_part2, ['Payments to deposit'])
    df_wire_final, _ = procesar_filtro(df_part2, ['WIRE ACCOUNT 3682', 'BUSINESS  3682'])
    df_zell_final, _ = procesar_filtro(df_part2, ['ZELL'])

    windows_downloads = '/mnt/c/Users/Andres Sanchez/Downloads'
    downloads_path = os.path.join(windows_downloads, "Transaction_List_All_Filters.xlsx")


    with pd.ExcelWriter(downloads_path, engine='openpyxl') as writer:
        df_cash_final.to_excel(writer, index=False, header=False, sheet_name="Cash")
        df_checking_final.to_excel(writer, index=False, header=False, sheet_name="Checking")
        df_payments_final.to_excel(writer, index=False, header=False, sheet_name="Payments")
        df_wire_final.to_excel(writer, index=False, header=False, sheet_name="Wire")
        df_zell_final.to_excel(writer, index=False, header=False, sheet_name="Zell")


    print(f"Archivo guardado en: {downloads_path}")

# Función alternativa para cualquier otro archivo
def procesar_otro_excel(file_path):
    # Aquí va tu lógica personalizada para otros archivos
    # Por ahora solo devuelve una línea de ejemplo
    return f"Se recibió el archivo {os.path.basename(file_path)}, pero no se aplicó el filtro especial."

if __name__ == "__main__":
    app.run(debug=True)

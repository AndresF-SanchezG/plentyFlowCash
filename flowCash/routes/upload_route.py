from flask import Blueprint, request, render_template
from processors.processor import procesar_excel, procesar_otro_excel, procesar_vendors_excel, resumen_totales_customer, resumen_totales_vendor 


import os

upload_blueprint = Blueprint("upload", __name__)

@upload_blueprint.route("/")
def index():
    return render_template("index.html")

@upload_blueprint.route("/upload", methods=["POST"])
def upload_file():
    if "excel_file" not in request.files:
        return "No se encontró el archivo", 400

    file = request.files["excel_file"]
    if file.filename == "":
        return "Nombre de archivo vacío", 400

    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploaded_path = os.path.join(base_dir, "../../", file.filename)
    file.save(uploaded_path)

    try:
        if file.filename == "Transaction_List_by_Customer.xlsx":
            output_path = procesar_excel(uploaded_path)
            return f"Archivo <strong>{file.filename}</strong> procesado exitosamente. Resultado: {output_path}"
        elif file.filename == "Transaction_List_by_Vendors.xlsx":
            output_path = procesar_vendors_excel(uploaded_path)
            return f"Archivo <strong>{file.filename}</strong> procesado exitosamente. Resultado: {output_path}"
        else:
            mensaje = procesar_otro_excel(uploaded_path)
            return f"Archivo <strong>{file.filename}</strong> procesado por otra función. Resultado: {mensaje}"
    except Exception as e:
        return f"Error procesando archivo: {str(e)}", 500
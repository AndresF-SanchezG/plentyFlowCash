from flask import Flask, request, redirect, url_for, render_template_string
import os

app = Flask(__name__)

# HTML como plantilla (puedes separarlo en un archivo si prefieres)
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

# Ruta principal (formulario)
@app.route("/")
def index():
    return render_template_string(html)

# Ruta que maneja la subida del archivo
@app.route("/upload", methods=["POST"])
def upload_file():
    if "excel_file" not in request.files:
        return "No se encontró el archivo", 400

    file = request.files["excel_file"]

    if file.filename == "":
        return "Nombre de archivo vacío", 400

    if file:
        # Ruta donde se guardará (misma carpeta que chargeReport.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(base_dir, file.filename)
        file.save(save_path)
        return f"Archivo {file.filename} subido exitosamente a {save_path}"

    return "Error al subir el archivo", 500

if __name__ == "__main__":
    app.run(debug=True)
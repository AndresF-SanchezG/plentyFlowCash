import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint
from processors.processor import resumen_totales_customer, resumen_totales_vendor

chart_blueprint = Blueprint("chart", __name__)

def generar_grafico(resumen, titulo):
    if not resumen:
        return "", ""

    categorias = list(resumen.keys())
    valores = list(resumen.values())
    total_general = sum(valores)
    categorias.append("Total")
    valores.append(total_general)

    porcentajes = {
        k: f"{(v / total_general * 100):.2f}%" if total_general != 0 else "0.00%"
        for k, v in resumen.items()
    }

    plt.figure(figsize=(12, 6))
    bars = plt.bar(categorias, valores, color='skyblue')
    plt.title("")  
    plt.xlabel("Categorías")
    plt.ylabel("Total ($)")
    plt.grid(axis='y')

    for bar in bars:
        yval = bar.get_height()
        label = "${:,.2f}".format(yval)
        plt.text(bar.get_x() + bar.get_width() / 2, yval, label, ha='center', va='bottom')

    plt.figtext(0.5, -0.05, titulo, wrap=True, horizontalalignment='center', fontsize=14)
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    porcentaje_html = "<ul>"
    for k, pct in porcentajes.items():
        porcentaje_html += f"<li><strong>{k}</strong>: {pct}</li>"
    porcentaje_html += "</ul>"

    return plot_url, porcentaje_html

@chart_blueprint.route("/graphics")
def mostrar_grafica():
    html_contenido = ""

    if resumen_totales_customer:
        img_url, html_porcentajes = generar_grafico(resumen_totales_customer, "TRANSACTION BY CUSTOMER")
        html_contenido += generar_html_grafico_estilizado(img_url, html_porcentajes, "")

    if resumen_totales_vendor:
        img_url, html_porcentajes = generar_grafico(resumen_totales_vendor, "TRANSACTION BY VENDORS")
        html_contenido += generar_html_grafico_estilizado(img_url, html_porcentajes, "")

    if not html_contenido:
        return "Aún no se ha procesado ningún archivo válido."

    html = f"""
    <html>
    <head>
        <title>Graphics Business</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 30px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            h2 {{
                text-align: center;
                font-size: 28px;
                margin-bottom: 20px;
            }}
            .container {{
                display: flex;
                align-items: flex-start;
                justify-content: center;
                gap: 0px;
                width: 100%;
                max-width: 1300px;
                margin-bottom: 80px;
            }}
            .chart {{
              flex-grow: 1;
              display: flex;
              justify-content: center;
            }}
            .chart img {{
              width: 100%;
              max-width: 1100px;
              height: auto;
            }}
            .porcentajes {{
                background: #ffffff;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                min-width: 200px;
                border: 2px solid #e0e0e0;
                margin-left: 50px;
                margin-top: 50px;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                font-size: 18px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <h1>GRAPHICS BUSINESS</h1>
        {html_contenido}
    </body>
    </html>
    """
    return html

def generar_html_grafico_estilizado(img_url, html_porcentajes, titulo):
    return f"""
    <h2>{titulo}</h2>
    <div class="container">
        <div class="chart">
            <img src="data:image/png;base64,{img_url}" alt="{titulo}">
        </div>
        <div class="porcentajes">
            <h3>Porcentajes</h3>
            {html_porcentajes}
        </div>
    </div>
    """


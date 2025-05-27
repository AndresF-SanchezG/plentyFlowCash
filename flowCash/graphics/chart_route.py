from flask import Blueprint
from processors.processor import resumen_totales
import matplotlib.pyplot as plt
import io
import base64

chart_blueprint = Blueprint("graphics", __name__)

@chart_blueprint.route("/graphics")
def mostrar_grafica():
    if not resumen_totales:
        return "Aún no se ha procesado ningún archivo válido."

    # Datos originales
    categorias = list(resumen_totales.keys())
    valores = list(resumen_totales.values())

    # Agregar categoría "Total"
    total_general = sum(valores)
    categorias.append("Total")
    valores.append(total_general)

    # Calcular porcentajes
    porcentajes = {
        k: f"{(v / total_general * 100):.2f}%" if total_general != 0 else "0.00%"
        for k, v in resumen_totales.items()
    }

    # Generar gráfica
    plt.figure(figsize=(12, 6))
    bars = plt.bar(categorias, valores, color='skyblue')

    # Quitar título superior
    plt.title("")  
    plt.xlabel("Categorías")
    plt.ylabel("Total ($)")
    plt.grid(axis='y')

    # Etiquetas de valores en cada barra
    for bar in bars:
        yval = bar.get_height()
        label = "${:,.2f}".format(yval)
        plt.text(bar.get_x() + bar.get_width() / 2, yval, label, ha='center', va='bottom')

    # Texto al pie de la gráfica
    plt.figtext(0.5, -0.05, "TRANSACTION BY CUSTOMER", wrap=True, horizontalalignment='center', fontsize=14)

    # Convertir la imagen a base64
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # Generar HTML de porcentajes al lado derecho
    porcentaje_html = "<ul>"
    for k, pct in porcentajes.items():
        porcentaje_html += f"<li><strong>{k}</strong>: {pct}</li>"
    porcentaje_html += "</ul>"

    # HTML completo
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
                gap: 0px;  /* no usamos gap para controlar la separación manualmente */
                width: 100%;
                max-width: 1300px;
              
            }}
            .chart {{
              flex-grow: 1;  /* toma todo el espacio disponible */
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
                margin-left: 50px;  /* separamos del gráfico para que no tape nada */
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
        <h2>GRAPHICS BUSINESS</h2>
        <div class="container">
            <div class="chart">
                <img src="data:image/png;base64,{plot_url}" alt="TRANSACTION BY CUSTOMER">
            </div>
            <div class="porcentajes">
                <h3>Porcentajes</h3>
                {porcentaje_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html
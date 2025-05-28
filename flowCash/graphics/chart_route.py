import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from flask import Blueprint
from processors.processor import resumen_totales_customer, resumen_totales_vendor, resumen_totales_vendor_por_proveedor

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

    if resumen_totales_vendor_por_proveedor:
        html_tabla = generar_tabla_html_vendor_por_proveedor(resumen_totales_vendor_por_proveedor)
        html_contenido += f"""
            <h2>TRANSACTION BY VENDOR NAME</h2>
            <div class="container" style="flex-direction: column; align-items: center;">
                <div class="tabla-container">
                    {html_tabla}
                </div>
            </div>
        """
    

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
            .tabla-vendors {{
                border-collapse: collapse;
                 width: 80%;
                margin-top: 30px;
                background: #fff;
                border: 1px solid #ddd;
                font-size: 16px;
            }}

            .tabla-vendors th, .tabla-vendors td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: center;
                
            }}

            .tabla-vendors th {{
                background-color: #f2f2f2;
                font-weight: bold;
                
                
            }}

            .tabla-vendors tr:nth-child(even) {{
                background-color: #f9f9f9;
                
                
                
            }}

             .tabla-vendors tr:hover {{
                background-color: #f1f1f1;
                
                
                
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

def generar_tabla_html_vendor_por_proveedor(resumen_dict):
    if not resumen_dict:
        return ""

    df = pd.DataFrame(list(resumen_dict.items()), columns=["Vendor", "Valor"])
    df["Valor"] = df["Valor"].astype(float).abs()
    total = df["Valor"].sum()
    df["%"] = (df["Valor"] / total) * 100
    df = df.sort_values(by="Valor", ascending=False)
    
    return df.to_html(index=False, float_format='{:,.2f}'.format, classes="tabla-vendors")


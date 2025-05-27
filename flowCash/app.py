from flask import Flask
from routes.upload_route import upload_blueprint
from graphics.chart_route import chart_blueprint

app = Flask(__name__)
app.register_blueprint(upload_blueprint)
app.register_blueprint(chart_blueprint)

if __name__ == "__main__":
    app.run(debug=True)

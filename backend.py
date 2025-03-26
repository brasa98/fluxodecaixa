from flask import Flask, render_template, request
from waitress import serve
import connsql

app = Flask(__name__)

dataSimulada = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', usuario=connsql.config['database'])

@app.route('/armazenar', methods=['GET', 'POST'])
def armazenar():
    return render_template('armazenar.html')

@app.route('/consultar', methods=['GET', 'POST'])
def consultar():
    return render_template('consultar.html')

@app.route('/opcoes', methods=['GET', 'POST'])
def opcoes():
    global dataSimulada

    if request.method == "POST":
        dataSimulada = request.form.get("dataSimulada")  # Pega o valor do campo de texto
        print(f"Configuração salva: {dataSimulada}")

    return render_template('opcoes.html', dataSimulada=dataSimulada)

def iniciar(host="0.0>.0.0", porta="5000", usuario=''):
    if host == "0.0.0.0":
        print(f"\n\nSERVIDOR WEB ONLINE!\n\nAcesse 'http://{host}:{porta}'")
        serve(app, host="0.0.0.0", port=porta)
    else:
        print(f"\n\nSERVIDOR WEB ONLINE!\n\nAcesse 'http://brasa.onthewifi.com'")
        serve(app, host="0.0.0.0", port=porta)


if __name__ == "__main__":
    app.run("0.0.0.0", "5000", debug=True)

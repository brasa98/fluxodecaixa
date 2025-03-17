from flask import Flask, render_template, request
from waitress import serve
#import main, connsql

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/armazenar')
def armazenar():
    return render_template('armazenar.html')

@app.route('/consultar')
def consultar():
    return render_template('consultar.html')

@app.route('/opcoes')
def opcoes():
    return render_template('opcoes.html')

def iniciar(host="0.0.0.0", porta="5000"):
    if host == "0.0.0.0":
        print(f"\n\nSERVIDOR WEB ONLINE!\n\nAcesse 'http://{host}:{porta}'")
        serve(app, host="0.0.0.0", port=porta)
    else:
        print(f"\n\nSERVIDOR WEB ONLINE!\n\nAcesse 'http://brasa.onthewifi.com'")
        serve(app, host="0.0.0.0", port=porta)


if __name__ == "__main__":
    app.run("0.0.0.0", "5000", debug=True)

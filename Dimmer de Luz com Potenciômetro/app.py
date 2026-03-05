from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Estado global simulando o ESP32
estado = {
    "intensidade": 0,
    "rele": False,
    "consumo": 0
}

POTENCIA_MAXIMA = 60  # lâmpada 60W

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/atualizar", methods=["POST"])
def atualizar():
    valor = int(request.json["valor"])

    intensidade = valor
    consumo = (intensidade / 100) * POTENCIA_MAXIMA
    rele = intensidade >= 50

    estado["intensidade"] = intensidade
    estado["rele"] = rele
    estado["consumo"] = round(consumo, 2)

    return jsonify(estado)

if __name__ == "__main__":
    app.run(debug=True)
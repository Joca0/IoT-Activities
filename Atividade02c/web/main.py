from flask import Flask, render_template, request
import random

app = Flask(__name__)

LIMITE_MIN = 30
LIMITE_MAX = 70

def verificar_umidade(valor):
    if valor < LIMITE_MIN:
        return "Solo seco", "vermelho", True
    elif valor <= LIMITE_MAX:
        return "Umidade ideal", "verde", False
    else:
        return "Solo muito úmido", "azul", False

@app.route("/", methods=["GET", "POST"])
def index():
    umidade = 50
    estado = ""
    cor_led = ""
    bomba = False

    if request.method == "POST":
        if "simular" in request.form:
            umidade = random.randint(0, 100)
        else:
            umidade = int(request.form["umidade"])

        estado, cor_led, bomba = verificar_umidade(umidade)

    return render_template("index.html",
                           umidade=umidade,
                           estado=estado,
                           cor_led=cor_led,
                           bomba=bomba)

if __name__ == "__main__":
    app.run(debug=True)
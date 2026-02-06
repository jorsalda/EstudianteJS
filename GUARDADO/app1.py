from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None

    if request.method == "POST":
        # Capturar datos del formulario
        balotas_rojas = int(request.form["balotas_rojas"])
        balotas_azules = int(request.form["balotas_azules"])
        cubos_rojos = int(request.form["cubos_rojos"])
        cubos_azules = int(request.form["cubos_azules"])

        # Cálculo de probabilidades
        total_objetos = balotas_rojas + balotas_azules + cubos_rojos + cubos_azules

        p_balota = (balotas_rojas + balotas_azules) / total_objetos
        p_cubo = (cubos_rojos + cubos_azules) / total_objetos

        p_rojo_dado_balota = balotas_rojas / (balotas_rojas + balotas_azules)
        p_rojo_dado_cubo = cubos_rojos / (cubos_rojos + cubos_azules)

        p_total_rojo = p_balota * p_rojo_dado_balota + p_cubo * p_rojo_dado_cubo
        p_condicional_rojo_dado_cubo = cubos_rojos / (cubos_rojos + cubos_azules)

        resultado = {
            "p_total_rojo": round(p_total_rojo, 4),
            "p_condicional_rojo_dado_cubo": round(p_condicional_rojo_dado_cubo, 4)
        }

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)

app.pyfrom flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    explicacion = None
    formula = None

    if request.method == "POST":
        # Datos del formulario
        n = int(request.form.get("balotas_rojas", 0))
        nm = int(request.form.get("balotas_azules", 0))
        x = int(request.form.get("cubos_rojos", 0))
        y = int(request.form.get("cubos_azules", 0))

        total_balotas = n + nm
        total_cubos = x + y
        total_objetos = total_balotas + total_cubos

        if total_objetos > 0:
            # Probabilidades
            p_balota = total_balotas / total_objetos
            p_cubo = total_cubos / total_objetos
            p_rojo_balota = n / total_balotas if total_balotas > 0 else 0
            p_rojo_cubo = x / total_cubos if total_cubos > 0 else 0
            p_total_rojo = (p_rojo_balota * p_balota) + (p_rojo_cubo * p_cubo)
            p_condicional = p_rojo_cubo

            # Explicación paso a paso
            explicacion = [
                f"1. En total hay {total_objetos} objetos en la urna: "
                f"{total_balotas} balotas y {total_cubos} cubos.",

                f"2. La probabilidad de elegir una balota es "
                f"P(Balota) = {total_balotas}/{total_objetos} = {round(p_balota, 4)}.",

                f"3. La probabilidad de elegir un cubo es "
                f"P(Cubo) = {total_cubos}/{total_objetos} = {round(p_cubo, 4)}.",

                f"4. La probabilidad de que sea rojo dado que elegimos una balota es "
                f"P(Rojo|Balota) = {n}/{total_balotas} = {round(p_rojo_balota, 4)}.",

                f"5. La probabilidad de que sea rojo dado que elegimos un cubo es "
                f"P(Rojo|Cubo) = {x}/{total_cubos} = {round(p_rojo_cubo, 4)}.",

                f"6. Aplicamos la Ley de la Probabilidad Total:",
                f"P(Rojo) = P(Rojo|Balota)·P(Balota) + P(Rojo|Cubo)·P(Cubo)",

                f"P(Rojo) = ({round(p_rojo_balota,4)}×{round(p_balota,4)}) + "
                f"({round(p_rojo_cubo,4)}×{round(p_cubo,4)}) = {round(p_total_rojo,4)}.",

                f"7. Finalmente, la probabilidad condicional de que sea rojo dado que es un cubo es "
                f"P(Rojo|Cubo) = {round(p_condicional, 4)}."
            ]

            # Fórmula en LaTeX
            formula = r"P(Rojo) = P(Rojo|Balota)\cdot P(Balota) + P(Rojo|Cubo)\cdot P(Cubo)"

            # Resultados finales
            resultado = {
                "probabilidad_total_rojo": round(p_total_rojo, 4),
                "probabilidad_condicional_rojo_dado_cubo": round(p_condicional, 4)
            }

    return render_template("index.html", resultado=resultado, explicacion=explicacion, formula=formula)


if __name__ == "__main__":
    app.run(debug=True)

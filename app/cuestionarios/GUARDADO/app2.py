from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "cambiar_por_una_clave_segura"  # necesario para flash

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/calcular", methods=["POST"])
def calcular():
    # Leer y validar datos del formulario
    try:
        n = int(request.form.get("n", 0))    # balotas rojas
        nm = int(request.form.get("nm", 0))  # balotas azules
        x = int(request.form.get("x", 0))    # cubos rojos
        y = int(request.form.get("y", 0))    # cubos azules
    except ValueError:
        flash("Todos los campos deben ser números enteros no negativos.", "danger")
        return redirect(url_for("index"))

    # No aceptar negativos
    if any(v < 0 for v in (n, nm, x, y)):
        flash("Ingrese valores no negativos.", "danger")
        return redirect(url_for("index"))

    # Totales
    total_balotas = n + nm
    total_cubos = x + y
    total_objetos = total_balotas + total_cubos

    if total_objetos == 0:
        flash("La urna no puede estar vacía. Ingrese al menos un objeto.", "danger")
        return redirect(url_for("index"))

    # Probabilidades básicas (comprobando divisiones por cero)
    p_balota = total_balotas / total_objetos if total_objetos > 0 else 0
    p_cubo = total_cubos / total_objetos if total_objetos > 0 else 0

    if total_balotas > 0:
        p_rojo_balota = n / total_balotas
    else:
        p_rojo_balota = None  # indicamos que no aplica

    if total_cubos > 0:
        p_rojo_cubo = x / total_cubos
    else:
        p_rojo_cubo = None

    # Para el cálculo de la probabilidad total, sustituimos 0 cuando una parte no existe
    term_balota = (p_rojo_balota if p_rojo_balota is not None else 0) * p_balota
    term_cubo = (p_rojo_cubo if p_rojo_cubo is not None else 0) * p_cubo
    p_total_rojo = term_balota + term_cubo

    # Probabilidad condicional P(Rojo | Cubo)
    p_condicional_rojo_dado_cubo = p_rojo_cubo if p_rojo_cubo is not None else 0

    # Construir la explicación paso a paso (texto claro y didáctico)
    pasos = []
    pasos.append(
        f"1) Contamos los objetos: Balotas = {total_balotas} (rojas={n}, azules={nm}); "
        f"Cubos = {total_cubos} (rojos={x}, azules={y}). Total = {total_objetos}."
    )

    pasos.append(
        f"2) Probabilidad de elegir una balota: P(Balota) = (balotas) / (total) = "
        f"({total_balotas}) / ({total_objetos}) = {p_balota:.4f}."
    )

    pasos.append(
        f"3) Probabilidad de elegir un cubo: P(Cubo) = (cubos) / (total) = "
        f"({total_cubos}) / ({total_objetos}) = {p_cubo:.4f}."
    )

    if p_rojo_balota is not None:
        pasos.append(
            f"4) Probabilidad de rojo dado que elegimos una balota: P(Rojo | Balota) = "
            f"{n} / {total_balotas} = {p_rojo_balota:.4f}."
        )
    else:
        pasos.append(
            "4) No hay balotas en la urna, por lo tanto P(Rojo | Balota) no aplica (se toma como 0 en el cálculo)."
        )

    if p_rojo_cubo is not None:
        pasos.append(
            f"5) Probabilidad de rojo dado que elegimos un cubo: P(Rojo | Cubo) = "
            f"{x} / {total_cubos} = {p_rojo_cubo:.4f}."
        )
    else:
        pasos.append(
            "5) No hay cubos en la urna, por lo tanto P(Rojo | Cubo) no aplica (se toma como 0 en el cálculo)."
        )

    pasos.append(
        "6) Aplicamos la Ley de la Probabilidad Total:\n"
        "   P(Rojo) = P(Rojo|Balota)*P(Balota) + P(Rojo|Cubo)*P(Cubo)."
    )

    # Mostrar la sustitución numérica y el cálculo de cada término
    pasos.append(
        "7) Sustituimos los valores:\n"
        f"   - Término balota = ({p_rojo_balota:.4f} if aplica) * {p_balota:.4f} = {term_balota:.4f}\n"
        f"   - Término cubo   = ({p_rojo_cubo:.4f} if aplica) * {p_cubo:.4f} = {term_cubo:.4f}\n"
        f"   => P(Rojo) = {term_balota:.4f} + {term_cubo:.4f} = {p_total_rojo:.4f}."
    )

    pasos.append(
        f"8) Probabilidad condicional pedida: P(Rojo | Cubo) = "
        f"{(f'{p_rojo_cubo:.4f}' if p_rojo_cubo is not None else 'No aplica (0)')}."
    )

    # Paquete de valores para la plantilla
    resultado = {
        "p_total_rojo": round(p_total_rojo, 4),
        "p_condicional_rojo_dado_cubo": round(p_condicional_rojo_dado_cubo, 4)
    }

    procesos = {
        "total_balotas": total_balotas,
        "total_cubos": total_cubos,
        "total_objetos": total_objetos,
        "p_balota": round(p_balota, 4),
        "p_cubo": round(p_cubo, 4),
        "p_rojo_balota": (round(p_rojo_balota, 4) if p_rojo_balota is not None else None),
        "p_rojo_cubo": (round(p_rojo_cubo, 4) if p_rojo_cubo is not None else None),
        "term_balota": round(term_balota, 6),
        "term_cubo": round(term_cubo, 6),
        "formula_text": "P(Rojo) = P(Rojo|Balota)*P(Balota) + P(Rojo|Cubo)*P(Cubo)"
    }

    return render_template(
        "resultado.html",
        n=n, nm=nm, x=x, y=y,
        resultado=resultado,
        procesos=procesos,
        pasos=pasos
    )

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambia_esto_por_una_clave_segura'


def compute_probs(n, nm, x, y):
    # calcula y devuelve un dict coherente o None si la urna está vacía
    total_balotas = n + nm
    total_cubos = x + y
    total_objetos = total_balotas + total_cubos

    if total_objetos == 0:
        return None

    p_balota = total_balotas / total_objetos
    p_cubo = total_cubos / total_objetos

    p_rojo_balota = (n / total_balotas) if total_balotas > 0 else None
    p_rojo_cubo = (x / total_cubos) if total_cubos > 0 else None

    term_balota = (p_rojo_balota if p_rojo_balota is not None else 0) * p_balota
    term_cubo = (p_rojo_cubo if p_rojo_cubo is not None else 0) * p_cubo
    p_total_rojo = term_balota + term_cubo

    pasos = []
    pasos.append(
        f"1) Imaginemos la urna: balotas = {total_balotas} (rojas={n}, azules={nm}), "
        f"cubos = {total_cubos} (rojos={x}, azules={y}). Total = {total_objetos}."
    )
    pasos.append(
        f"2) Probabilidad de elegir una balota: P(Balota) = {total_balotas}/{total_objetos} = {p_balota:.4f}."
    )
    pasos.append(
        f"3) Probabilidad de elegir un cubo: P(Cubo) = {total_cubos}/{total_objetos} = {p_cubo:.4f}."
    )
    if p_rojo_balota is not None:
        pasos.append(
            f"4) P(Rojo | Balota) = {n}/{total_balotas} = {p_rojo_balota:.4f}."
        )
    else:
        pasos.append("4) No hay balotas; P(Rojo|Balota) no aplica.")
    if p_rojo_cubo is not None:
        pasos.append(
            f"5) P(Rojo | Cubo) = {x}/{total_cubos} = {p_rojo_cubo:.4f}."
        )
    else:
        pasos.append("5) No hay cubos; P(Rojo|Cubo) no aplica.")

    pasos.append("6) Aplicamos la Ley de la Probabilidad Total:")
    pasos.append(r"\[ P(\mathrm{Rojo}) = P(\mathrm{Rojo}\mid\mathrm{Balota})\cdot P(\mathrm{Balota}) + P(\mathrm{Rojo}\mid\mathrm{Cubo})\cdot P(\mathrm{Cubo}) \]")
    pasos.append(
        f"7) Sustitución numérica: término balota = {term_balota:.6f}, término cubo = {term_cubo:.6f}; "
        f"por tanto P(Rojo) = {p_total_rojo:.6f}."
    )
    pasos.append(f"8) P(Rojo | Cubo) = {(p_rojo_cubo if p_rojo_cubo is not None else 0):.6f}.")

    formula = r"P(\mathrm{Rojo}) = P(\mathrm{Rojo}\mid\mathrm{Balota})\cdot P(\mathrm{Balota}) + P(\mathrm{Rojo}\mid\mathrm{Cubo})\cdot P(\mathrm{Cubo})"

    procesos = {
        "total_balotas": total_balotas,
        "total_cubos": total_cubos,
        "total_objetos": total_objetos,
        "p_balota": round(p_balota, 6),
        "p_cubo": round(p_cubo, 6),
        "p_rojo_balota": (round(p_rojo_balota, 6) if p_rojo_balota is not None else None),
        "p_rojo_cubo": (round(p_rojo_cubo, 6) if p_rojo_cubo is not None else None),
        "term_balota": round(term_balota, 6),
        "term_cubo": round(term_cubo, 6),
    }

    resultado = {
        "p_total_rojo": round(p_total_rojo, 6),
        "p_condicional_rojo_dado_cubo": round((p_rojo_cubo if p_rojo_cubo is not None else 0), 6)
    }

    return {"resultado": resultado, "procesos": procesos, "pasos": pasos, "formula": formula}


@app.route("/", methods=["GET"])
def index():
    # muestra formulario (template index.html)
    return render_template("index.html")


# endpoint para formulario POST clásico -> renderiza la plantilla con resultados
@app.route("/calcular", methods=["POST"])
def calcular():
    try:
        n = int(request.form.get("balotas_rojas", 0))
        nm = int(request.form.get("balotas_azules", 0))
        x = int(request.form.get("cubos_rojos", 0))
        y = int(request.form.get("cubos_azules", 0))
    except ValueError:
        return render_template("index.html", error="Ingrese números enteros no negativos.")

    data = compute_probs(n, nm, x, y)
    if data is None:
        return render_template("index.html", error="La urna no puede estar vacía. Ingrese al menos un objeto.")

    # renderizamos index.html pero con resultados ya calculados (tu template debe detectarlo)
    return render_template("index.html",
                           resultado=data["resultado"],
                           procesos=data["procesos"],
                           pasos=data["pasos"],
                           formula=data["formula"],
                           form_values={"balotas_rojas": n, "balotas_azules": nm, "cubos_rojos": x, "cubos_azules": y})


# endpoint JSON (para AJAX): mantiene compatibilidad con /probabilidades si lo usabas antes
@app.route("/probabilidades", methods=["POST"])
def calcular_probabilidades():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        n = int(payload.get("balotas_rojas", 0))
        nm = int(payload.get("balotas_azules", 0))
        x = int(payload.get("cubos_rojos", 0))
        y = int(payload.get("cubos_azules", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    data = compute_probs(n, nm, x, y)
    if data is None:
        return jsonify({"error": "La urna no puede estar vacía"}), 400

    return jsonify(data)


# alias JSON (opcional)
@app.route("/api/calcular", methods=["POST"])
def api_calcular():
    return calcular_probabilidades()


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)

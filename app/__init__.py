from flask import Flask, render_template, jsonify
import os, json

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    @app.route("/")
    def index():
        return render_template("Estudiante.html")

    @app.route("/cuestionario/<path:nombre_quiz>")
    def cargar_quiz(nombre_quiz):
        ruta_json = os.path.join(base_dir, "cuestionarios", f"{nombre_quiz}.json")
        with open(ruta_json, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))

    return app

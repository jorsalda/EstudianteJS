class CslTIngenios {
    constructor() {
        this.preguntas = [];
        this.preguntaActual = 0;
        this.respuestasCorrectas = 0;
        this.respuestasIncorrectas = 0;
        this.numPreguntasJuego = 1;
        this.respuestaResaltada = false;
        this.countdownInterval = null;
        this.explicacionVisible = false;
        this.modoRevision = false;
        this.password = "jes1";
        this.intentosRestantes = 3;
    }

    cargarPreguntasDesdeArchivo(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                this.preguntas = JSON.parse(e.target.result).preguntas;

                $("#loadedQuestionsCount").html(
                    `<b>El archivo tiene:</b> ${this.preguntas.length}`
                );

                this.shuffleArray(this.preguntas);
                this.mostrarPregunta();

                $("#loadQuestions, #fileInput, #updateQuestions, #numQuestions").hide();
                $("#nextButton").show();
            } catch {
                alert("Error al cargar el archivo JSON.");
            }
        };
        reader.readAsText(file);
    }

    init() {
        $(document).ready(() => {

            $("#submitButton").click(() => {
                if ($("#passwordInput").val() === this.password) {
                    $("#passwordContainer").hide();
                    $("#errorMessage").hide();
                    this.iniciarNuevoJuego();
                } else {
                    this.intentosRestantes--;
                    $("#errorMessage")
                        .text(`Contraseña incorrecta. Intentos restantes: ${this.intentosRestantes}`)
                        .show();
                }
            });

            $("#loadQuestions").click(() => {
                const file = $("#fileInput")[0].files[0];
                if (file) this.cargarPreguntasDesdeArchivo(file);
            });

            $("#updateQuestions").click(() => {
                this.numPreguntasJuego = parseInt($("#numQuestions").val());
            });

            $("#nextButton").click(() => {
                if (!this.respuestaResaltada) {
                    this.detenerContador();
                    this.mostrarResultadoRespuesta();
                } else {
                    this.avanzarAPreguntaSiguiente();
                }
            });

            $("#explanationButton").click(() => {
                this.mostrarExplicacion();
            });

            $(document).on("click", "#playAgain", () => {
                this.preguntaActual = 0;
                this.respuestaResaltada = false;
                this.explicacionVisible = false;
                this.modoRevision = true;
                $("#result").hide();
                $("#nextButton").show();
                this.mostrarPregunta();
            });

            $(document).on("click", "#options label", function () {
                $("#options label").removeClass("selected");
                $(this).addClass("selected");
            });
        });
    }

    iniciarNuevoJuego() {
        this.preguntaActual = 0;
        this.respuestasCorrectas = 0;
        this.respuestasIncorrectas = 0;
        this.respuestaResaltada = false;
        this.explicacionVisible = false;
        this.modoRevision = false;
        clearInterval(this.countdownInterval);

        this.shuffleArray(this.preguntas);
        this.mostrarPregunta();
    }

    mostrarPregunta() {
        if (
            this.preguntaActual < this.numPreguntasJuego &&
            this.preguntaActual < this.preguntas.length
        ) {
            const pregunta = this.preguntas[this.preguntaActual];

            /* ================= CONTEXTO FLEXIBLE ================= */
            let htmlContexto = "<b>Contexto:</b><br>";
            const ctx = pregunta.contexto;

            if (ctx?.tipo === "texto") {
                htmlContexto += `<p>${ctx.contenido}</p>`;
            }

            if (ctx?.tipo === "imagen") {
                htmlContexto += `
                    <img src="static/imagenes/${ctx.contenido}"
                         style="max-width:100%; margin-top:10px;">
                `;
            }

            if (ctx?.tipo === "video") {
                htmlContexto += `
                    <video controls style="max-width:100%; margin-top:10px;">
                        <source src="static/videos/${ctx.contenido}" type="video/mp4">
                    </video>
                `;
            }

            $("#contexto").html(htmlContexto);
            /* ===================================================== */

            $("#question").html(
                `<b>Pregunta ${this.preguntaActual + 1}:</b> ${pregunta.pregunta}`
            );

            $("#options").empty();
            const opciones = this.shuffleArray(pregunta.opciones.slice());
            const letras = ["A)", "B)", "C)", "D)"];

            opciones.forEach((op, i) => {
                $("#options").append(`
                    <label>
                        <input type="radio" name="opcion" value="${op}">
                        ${letras[i]} ${op}
                    </label>
                `);
            });

            $("#explanationButton").hide();

            if (!this.modoRevision) {
                $("#countdown").show();
                this.iniciarContador();
            } else {
                $("#countdown").hide();
            }

        } else {
            this.mostrarResultado();
        }
    }

    mostrarResultadoRespuesta() {
        const pregunta = this.preguntas[this.preguntaActual];

        if (this.modoRevision) {
            $("input[value='" + pregunta.respuesta + "']")
                .parent()
                .addClass("correct-answer");

            this.respuestaResaltada = true;
            $("#explanationButton").show();
            return;
        }

        const seleccion = $("input[name='opcion']:checked").val();
        if (!seleccion) {
            alert("Seleccione una opción.");
            return;
        }

        this.respuestaResaltada = true;
    }

    mostrarExplicacion() {
        const pregunta = this.preguntas[this.preguntaActual];
        $("#explanation-column")
            .html(`<b>Explicación:</b> ${pregunta.explicacion}`)
            .show();
    }

    avanzarAPreguntaSiguiente() {
        $("#explanation-column").empty().hide();
        this.explicacionVisible = false;

        this.preguntaActual++;
        this.respuestaResaltada = false;
        this.mostrarPregunta();
    }

    mostrarResultado() {
        $("#question").empty();
        $("#options").empty();

        $("#result").html(`
            <p>Correctas: ${this.respuestasCorrectas}</p>
            <p>Incorrectas: ${this.respuestasIncorrectas}</p>
            <button id="playAgain">Revisar examen</button>
        `).show();

        $("#nextButton").hide();
        $("#countdown").hide();
    }

    iniciarContador() {
        if (this.modoRevision) return;

        let t = 5;
        $("#countdown").text(`Tiempo restante: ${t}`);

        this.countdownInterval = setInterval(() => {
            t--;
            $("#countdown").text(`Tiempo restante: ${t}`);
            if (t < 0) {
                this.detenerContador();
                this.avanzarAPreguntaSiguiente();
            }
        }, 1000);
    }

    detenerContador() {
        clearInterval(this.countdownInterval);
        this.countdownInterval = null;
    }

    shuffleArray(arr) {
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    }
}

const cslTIngenios = new CslTIngenios();
cslTIngenios.init();
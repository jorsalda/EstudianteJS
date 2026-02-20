class CslTIngenios {
    constructor() {
        this.preguntas = [];
        this.examenFijo = [];        // 🔒 examen congelado
        this.preguntaActual = 0;

        this.respuestasCorrectas = 0;
        this.respuestasIncorrectas = 0;

        this.numPreguntasJuego = 1;
        this.respuestaResaltada = false;
        this.temporizadorDetenido = false;
        this.segundoClic = false;
        this.countdownInterval = null;
        this.explicacionVisible = false;

        this.modoRevision = false;   // 👈 clave

        this.password = "jes1";
        this.intentosRestantes = 3;
    }

    /* =========================
       CARGA DE PREGUNTAS
    ========================= */
    cargarPreguntasDesdeArchivo(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                this.preguntas = JSON.parse(e.target.result).preguntas;

                $("#loadedQuestionsCount").html(
                    `<b>El archivo tiene:</b> ${this.preguntas.length}`
                );

                // 🔒 congelar examen (una sola vez)
                this.examenFijo = this.shuffleArray([...this.preguntas])
                    .slice(0, this.numPreguntasJuego)
                    .map(p => ({
                        ...p,
                        opcionesMezcladas: this.shuffleArray(p.opciones.slice())
                    }));

                this.preguntaActual = 0;
                this.modoRevision = false;

                this.mostrarPregunta();

                $("#loadQuestions, #fileInput, #updateQuestions, #numQuestions").hide();
                $("#nextButton").show();
            } catch {
                alert("Error al cargar el archivo JSON.");
            }
        };
        reader.readAsText(file);
    }

    /* =========================
       INIT
    ========================= */
    init() {
        $(document).ready(() => {

            $("#submitButton").click(() => {
                if ($("#passwordInput").val() === this.password) {
                    $("#passwordContainer").hide();
                    $("#errorMessage").hide();
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
                else alert("Seleccione un archivo JSON");
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
                this.resetGameState();
                this.modoRevision = true;
                this.mostrarPregunta();
            });

            $(document).on("click", "#options label", function () {
                $("#options label").removeClass("selected");
                $(this).addClass("selected");
            });
        });
    }

    /* =========================
       CONTROL DE FLUJO
    ========================= */
    resetGameState() {
        this.preguntaActual = 0;
        this.respuestasCorrectas = 0;
        this.respuestasIncorrectas = 0;
        this.respuestaResaltada = false;
        this.temporizadorDetenido = false;
        this.segundoClic = false;
        this.explicacionVisible = false;
        clearInterval(this.countdownInterval);
    }

    /* =========================
       MOSTRAR PREGUNTA
    ========================= */
    mostrarPregunta() {
        if (this.preguntaActual >= this.examenFijo.length) {
            this.mostrarResultado();
            return;
        }

        const pregunta = this.examenFijo[this.preguntaActual];

        $("#contexto").html(`<b>Contexto:</b> ${pregunta.contexto || ""}`);
        $("#question").html(`<b>Pregunta ${this.preguntaActual + 1}:</b> ${pregunta.pregunta}`);
        $("#options").empty();

        const letras = ["A)", "B)", "C)", "D)"];
        pregunta.opcionesMezcladas.forEach((op, i) => {
            $("#options").append(`
                <label>
                    <input type="radio" name="opcion" value="${op}">
                    ${letras[i]} ${op}
                </label>
            `);
        });

        $("#explanationButton").hide();
        this.iniciarContador();
    }

    /* =========================
       RESPUESTA
    ========================= */
    mostrarResultadoRespuesta() {
        // 🚫 en examen NO califica
        if (!this.modoRevision) {
            this.respuestaResaltada = true;
            return;
        }

        const seleccion = $("input[name='opcion']:checked").val();
        const pregunta = this.examenFijo[this.preguntaActual];

        if (seleccion === pregunta.respuesta) {
            this.respuestasCorrectas++;
        } else {
            this.respuestasIncorrectas++;
        }

        $("input[value='" + pregunta.respuesta + "']")
            .parent()
            .addClass("correct-answer");

        this.respuestaResaltada = true;
        $("#explanationButton").show();
    }

    mostrarExplicacion() {
        const pregunta = this.examenFijo[this.preguntaActual];
        $("#explanation-column")
            .html(`<b>Explicación:</b> ${pregunta.explicacion}`)
            .show();
    }

    avanzarAPreguntaSiguiente() {
        this.preguntaActual++;
        this.respuestaResaltada = false;
        this.mostrarPregunta();
    }

    /* =========================
       RESULTADO FINAL
    ========================= */
    mostrarResultado() {
        $("#result").html(`
            <p>Correctas: ${this.respuestasCorrectas}</p>
            <p>Incorrectas: ${this.respuestasIncorrectas}</p>
            <button id="playAgain">Revisar examen</button>
        `).show();

        $("#nextButton").hide();
        $("#countdown").hide();
    }

    /* =========================
       TIEMPO
    ========================= */
    iniciarContador() {
        let t = 30;
        $("#countdown").text(`Tiempo restante: ${t}`).show();

        this.countdownInterval = setInterval(() => {
            t--;
            $("#countdown").text(`Tiempo restante: ${t}`);
            if (t < 0) {
                clearInterval(this.countdownInterval);
                this.avanzarAPreguntaSiguiente();
            }
        }, 1000);
    }

    detenerContador() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
    }

    /* =========================
       UTIL
    ========================= */
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
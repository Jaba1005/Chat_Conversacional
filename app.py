from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


# Cargar variables del archivo .env
load_dotenv()

# Obtener API Key de Gemini
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )


# Crear cliente de Gemini
client = genai.Client(api_key=API_KEY)


# Configuración del asistente
configuration = types.GenerateContentConfig(
    max_output_tokens=2048,
    system_instruction="""
Eres un asistente virtual especializado en deportes.

Tu función es ayudar a un narrador deportivo.

Responde de manera clara, breve y útil.

Si el usuario pregunta algo que NO está relacionado
con deportes, responde:

"Lo siento, solo puedo responder preguntas relacionadas con deportes."

No inventes información.
"""
)


# ============================================================
# 4. CREAR EL CHAT
# ============================================================

chat = client.chats.create(
    model="gemini-3.6-flash",
    config=configuration
)


# ============================================================
# 5. CREAR APLICACIÓN FLASK
# ============================================================

app = Flask(__name__)

app.secret_key = "clave_secreta_para_simulacion_de_chat_12345"


# ============================================================
# 6. PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def inicio():

    # Si no existe historial, lo creamos
    if "historial" not in session:

        session["historial"] = [
            {
                "remitente": "bot",
                "mensaje": (
                    "¡Hola! Soy tu asistente virtual deportivo. "
                    "¿De qué deporte te gustaría hablar?"
                )
            }
        ]

    return render_template(
        "index.html",
        historial=session["historial"]
    )


# ============================================================
# 7. RECIBIR MENSAJE DEL USUARIO
# ============================================================

@app.route("/enviar", methods=["POST"])
def enviar_mensaje():

    try:

        # Obtener datos enviados desde JavaScript
        datos = request.get_json()

        if not datos:
            return jsonify({
                "error": "No se recibieron datos."
            }), 400

        # Obtener mensaje
        mensaje_usuario = datos.get("mensaje", "").strip()

        if not mensaje_usuario:
            return jsonify({
                "error": "El mensaje no puede estar vacío."
            }), 400


        # ====================================================
        # GUARDAR MENSAJE DEL USUARIO
        # ====================================================

        historial = session.get("historial", [])

        historial.append({
            "remitente": "usuario",
            "mensaje": mensaje_usuario
        })


        # ====================================================
        # ENVIAR MENSAJE A GEMINI
        # ====================================================

        respuesta = chat.send_message(
            mensaje_usuario
        )

        respuesta_bot = respuesta.text


        # ====================================================
        # GUARDAR RESPUESTA DEL BOT
        # ====================================================

        historial.append({
            "remitente": "bot",
            "mensaje": respuesta_bot
        })

        session["historial"] = historial
        session.modified = True


        # ====================================================
        # DEVOLVER RESPUESTA AL FRONTEND
        # ====================================================

        return jsonify({
            "respuesta": respuesta_bot
        })


    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": "Ocurrió un error al comunicarse con Gemini.",
            "detalle": str(e)
        }), 500


# ============================================================
# 8. LIMPIAR CHAT
# ============================================================

@app.route("/limpiar", methods=["POST"])
def limpiar_chat():

    session["historial"] = [
        {
            "remitente": "bot",
            "mensaje": (
                "Historial reiniciado. "
                "¡Hola de nuevo! ¿En qué deporte quieres conversar?"
            )
        }
    ]

    session.modified = True

    return jsonify({
        "status": "success"
    })


# ============================================================
# 9. EJECUTAR SERVIDOR
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True
    )

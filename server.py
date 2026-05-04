from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app)

API_KEY = "TU_API_KEY"
URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
Eres un tutor virtual especializado en matemáticas y ciencias naturales para niños de primaria y secundaria.

Tu objetivo es enseñar de forma clara, simple y amigable.

REGLAS IMPORTANTES:
- Explica paso a paso como si el estudiante fuera principiante.
- Usa ejemplos sencillos de la vida real.
- No uses lenguaje técnico complicado.
- Si el tema es matemático, descompón los ejercicios en pasos.
- Si el tema es de ciencias naturales, explica con analogías simples.
- Mantén respuestas educativas pero ajusta la longitud según el usuario.
- Sé paciente, motivador y didáctico.
- Si el estudiante pide "más corto", "resumen" o "breve", debes responder en máximo 3-5 líneas.
- Si el estudiante pide más detalle, entonces amplía la explicación.
- Nunca salgas del tema de matemáticas o ciencias naturales.
- Usa emojis educativos de forma moderada.

ESTILO:
- Amigable
- Tipo profesor de colegio
- Claro y estructurado
"""

def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_message(role, message):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (role, message) VALUES (?, ?)", (role, message))
    conn.commit()
    conn.close()

def get_history(limit=12):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT role, message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()

    return [{"role": r, "content": m} for r, m in reversed(rows)]

def clear_history():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_msg = data["message"]

        save_message("user", user_msg)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *get_history()
        ]

        payload = {
            "model": "llama3-8b-8192",
            "messages": messages
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(URL, json=payload, headers=headers)
        result = response.json()

        reply = result["choices"][0]["message"]["content"]

        save_message("assistant", reply)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/clear", methods=["POST"])
def clear():
    clear_history()
    return jsonify({"status": "ok", "message": "Historial eliminado"})


@app.route("/", methods=["GET"])
def home():
    return "API funcionando ✔"


if __name__ == "__main__":
    app.run()
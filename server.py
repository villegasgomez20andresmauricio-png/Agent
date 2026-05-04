from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
Eres un tutor virtual especializado en matemáticas y ciencias naturales para niños de primaria y secundaria.

REGLAS:
- Explica claro y paso a paso.
- Usa ejemplos simples.
- Si el usuario pide "más corto", responde breve (3-5 líneas).
- Si pide detalle, amplía explicación.
- Usa emojis educativos moderadamente 😊
- No salgas de matemáticas o ciencias naturales.
"""

MAX_HISTORY = 12

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

def get_history():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        SELECT role, message FROM messages
        ORDER BY id DESC
        LIMIT ?
    """, (MAX_HISTORY,))
    rows = c.fetchall()
    conn.close()

    return [{"role": r, "content": m} for r, m in reversed(rows)]

def clear_history():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def home():
    return "API funcionando ✔"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not API_KEY:
            return jsonify({"error": "Falta GROQ_API_KEY en variables de entorno"}), 500

        data = request.get_json()
        user_msg = data.get("message", "")

        if not user_msg:
            return jsonify({"error": "Mensaje vacío"}), 400

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

        print("GROQ RESPONSE:", result)

        if "choices" not in result:
            return jsonify({
                "error": "Respuesta inválida de Groq",
                "details": result
            }), 500

        reply = result["choices"][0]["message"]["content"]

        save_message("assistant", reply)

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR BACKEND:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/clear", methods=["POST"])
def clear():
    clear_history()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
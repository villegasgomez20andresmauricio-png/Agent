from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GROQ_API_KEY")

URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "Eres un tutor de matemáticas y ciencias naturales para niños. "
    "Explicas de forma simple, clara y con ejemplos fáciles."
)

@app.route("/", methods=["GET"])
def home():
    return "API funcionando ✔"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Falta el campo 'message'"}), 400

        user_msg = data["message"]

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(URL, json=payload, headers=headers)

        try:
            result = response.json()
        except Exception:
            return jsonify({
                "error": "Respuesta no válida de la API",
                "raw": response.text
            }), 500

        print(result)

        if "choices" not in result:
            return jsonify({
                "error": "Respuesta inválida de Groq",
                "details": result
            }), 500

        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
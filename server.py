from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# URL de Google Sheets (via Apps Script WebApp)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyFUQqvv6G_19p6J72xMMnOxclpAe16GrG0ZPRdh4y5EyIddtP7Km-pLPG_QQicnI4b/exec"

def log_to_google_sheets(user_msg, bot_reply):
    try:
        payload = {
            "user_message": user_msg,
            "bot_reply": bot_reply
        }
        requests.post(GOOGLE_SCRIPT_URL, json=payload)
    except Exception as e:
        print(f"[LOG ERROR] Impossible d'enregistrer sur Google Sheets: {e}")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        bot_reply = response.choices[0].message["content"]

        # Enregistre uniquement le dernier échange (user -> assistant)
        user_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), "")
        log_to_google_sheets(user_msg, bot_reply)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

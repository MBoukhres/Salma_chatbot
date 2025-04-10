from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Nouvelle URL Google Apps Script (avec localisation)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwsyw5ZcdtxbqKxlVZJ-MhYmlEMd9x0CDebIYY_lmxWQ4P2E7lZPF-TBvqHfnbZdtKV/exec"

def log_to_google_sheets(user_msg, bot_reply):
    try:
        # Récupération IP
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        # Récupération des données de géolocalisation
        geo_resp = requests.get(f"https://ipinfo.io/{ip}/json")
        geo_data = geo_resp.json()

        city = geo_data.get("city", "Unknown")
        region = geo_data.get("region", "Unknown")
        country = geo_data.get("country", "Unknown")
        loc = geo_data.get("loc", "")  # "latitude,longitude"

        # Payload à envoyer à Google Sheets
        payload = {
            "user_message": user_msg,
            "bot_reply": bot_reply,
            "ip": ip,
            "city": city,
            "region": region,
            "country": country,
            "loc": loc
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

        # Récupération du dernier message utilisateur
        user_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), "")

        # Log dans Google Sheets avec géolocalisation
        log_to_google_sheets(user_msg, bot_reply)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Chatbot API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

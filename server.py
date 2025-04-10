from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import requests

app = Flask(__name__)
CORS(app)

# Clé API OpenAI depuis variable d’environnement
openai.api_key = os.environ.get("OPENAI_API_KEY")

# URL du script Google Apps Script (Web App)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwsyw5ZcdtxbqKxlVZJ-MhYmlEMd9x0CDebIYY_lmxWQ4P2E7lZPF-TBvqHfnbZdtKV/exec"

# Fonction pour enregistrer dans Google Sheets avec géolocalisation
def log_to_google_sheets(user_msg, bot_reply):
    try:
        # Récupération IP réelle depuis header ou fallback
        raw_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        ip = raw_ip.split(',')[0].strip()

        # Appel API ipinfo.io pour obtenir la localisation
        geo_resp = requests.get(f"https://ipinfo.io/{ip}/json")
        geo_data = geo_resp.json()

        city = geo_data.get("city", "Unknown")
        region = geo_data.get("region", "Unknown")
        country = geo_data.get("country", "Unknown")
        loc = geo_data.get("loc", "")  # latitude,longitude

        # Données à envoyer à Google Sheets
        payload = {
            "user_message": user_msg,
            "bot_reply": bot_reply,
            "ip": ip,
            "city": city,
            "region": region,
            "country": country,
            "loc": loc
        }

        # Envoi POST
        requests.post(GOOGLE_SCRIPT_URL, json=payload)

    except Exception as e:
        print(f"[LOG ERROR] {e}")

# Endpoint principal pour le chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # ou "gpt-4"
            messages=messages,
            temperature=0.7
        )

        bot_reply = response.choices[0].message["content"].strip()

        # Dernier message utilisateur
        user_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), "")

        # Log dans Google Sheets
        log_to_google_sheets(user_msg, bot_reply)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint simple pour tester le serveur
@app.route("/", methods=["GET"])
def home():
    return "Chatbot API is running."

# Lancement local (non utilisé sur Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

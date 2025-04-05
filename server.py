from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "أنت سلمى، مساعدة ذكية في موقع CoolMallShop. "
                        "أجب دائمًا باللغة العربية السعودية ما لم يكتب العميل رسالته باللغة الإنجليزية. "
                        "إذا كتب العميل بالإنجليزية، فإما أن ترد بالإنجليزية أو تسأله إن كان يفضل المتابعة بالعربية أو الإنجليزية."
                    )
                },
                {"role": "user", "content": user_msg}
            ],  # ✅ virgule ici
            temperature=0.7
        )
        return jsonify({"reply": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


@app.route("/")
def index():
    return render_template("index.html")


# Correct chat route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message")

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": f"""
You are an AI mental health assistant. 
Analyze the user's message below and return a JSON response ONLY in this format:

{{
  "sentiment": "positive | neutral | negative",
  "emotion": "happy | sad | stressed | anxious | angry | neutral",
  "severity": "low | medium | high",
  "reply": "Your supportive response to user."
}}

User message: "{user_msg}"
"""
                }
            ]
        }
    ]
}

    try:
        response = requests.post(url, json=payload)
        res_json = response.json()
        print("Gemini Response:", res_json)

        # Error from Google
        if "error" in res_json:
            return jsonify({"reply": "AI error: " + res_json["error"].get("message", "")})

        # Extract actual message
        candidates = res_json.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                ai_text = parts[0].get("text", "").strip()
                
                if ai_text.startswith("```"):
                    ai_text = ai_text.replace("```json", "").replace("```", "").strip()

                import json
                try:
                    # Convert AI text into JSON dict
                    ai_json = json.loads(ai_text)
                    return jsonify(ai_json)
                except:
                    # If Gemini returns non-JSON text, fallback
                    return jsonify({"reply": ai_text})

        return jsonify({"reply": "Unexpected AI response"})


    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Server error occurred"})


# Models route 
@app.route("/models")
def models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    response = requests.get(url)
    return response.json()


# Test key route (kept as is)
@app.route("/test_key")
def test_key():
    url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_API_KEY}"
    r = requests.get(url)
    print("MODEL LIST:", r.json())
    return r.json()


if __name__ == "__main__":
    app.run(debug=True)

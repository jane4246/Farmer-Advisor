import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- FRONTEND ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eldoret Orchards AI</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; height: 100vh; background: #eef2f5; margin: 0; }
        .chat-container { width: 100%; max-width: 500px; background: white; display: flex; flex-direction: column; box-shadow: 0 4px 20px rgba(0,0,0,0.1); height: 100%; }
        @media(min-width: 600px) { .chat-container { height: 90vh; margin-top: 5vh; border-radius: 12px; overflow: hidden; } }
        .chat-header { background: #2E7D32; color: white; padding: 20px; text-align: center; font-weight: bold; font-size: 1.2rem; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; background-color: #f9f9f9; }
        .message { padding: 10px 15px; border-radius: 15px; margin-bottom: 10px; max-width: 80%; line-height: 1.4; }
        .bot { background: #e8f5e9; color: #1b5e20; align-self: flex-start; }
        .user { background: #2E7D32; color: white; align-self: flex-end; margin-left: auto; }
        .input-area { display: flex; padding: 15px; background: #fff; border-top: 1px solid #eee; }
        input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none; }
        button { padding: 10px 20px; background: #2E7D32; color: white; border: none; margin-left: 10px; cursor: pointer; border-radius: 25px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🌿 Eldoret Orchards Assistant</div>
        <div class="chat-box" id="chat-box">
            <div class="message bot">Hello! I am your farming assistant. Ask me about avocados, mangoes, or soil health!</div>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Type a message..." onkeypress="handleEnter(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const input = document.getElementById("user-input");
            const text = input.value.trim();
            if (!text) return;
            
            addMessage(text, "user");
            input.value = "";
            
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                addMessage(data.reply || data.error, "bot");
            } catch (e) {
                addMessage("Error connecting to server.", "bot");
            }
        }
        function addMessage(text, sender) {
            const box = document.getElementById("chat-box");
            const div = document.createElement("div");
            div.className = "message " + sender;
            div.innerText = text;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }
        function handleEnter(e) { if (e.key === "Enter") sendMessage(); }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    if not GOOGLE_API_KEY:
        return jsonify({"error": "Configuration Error: API Key missing."}), 500
        
    user_input = request.json.get("message")
    
    # --- FIX: SWITCHED TO 'gemini-pro' (The Standard Model) ---
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"You are a helpful farming expert for Eldoret Orchards. User asks: {user_input}"
            }]
        }]
    }

    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            try:
                bot_reply = result['candidates'][0]['content']['parts'][0]['text']
                return jsonify({"reply": bot_reply})
            except (KeyError, IndexError):
                 return jsonify({"reply": "I understood the question but couldn't think of an answer. Please try again."})
        else:
            return jsonify({"error": f"Google Error ({response.status_code}): {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

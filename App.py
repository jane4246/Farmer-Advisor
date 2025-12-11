import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- SECURE CONFIGURATION ---
# This looks for the key in Render's settings. 
# It will be None if the setting is missing.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("⚠️ WARNING: API Key not found. Chat will not work.")

# --- FRONTEND ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eldoret Orchards AI</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; height: 100vh; background: #eef2f5; margin: 0; }
        .chat-container { width: 100%; max-width: 500px; background: white; display: flex; flex-direction: column; box-shadow: 0 4px 20px rgba(0,0,0,0.1); height: 100%; }
        .chat-header { background: #2E7D32; color: white; padding: 20px; text-align: center; font-weight: bold; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; background-color: #f9f9f9; }
        .message { padding: 10px 15px; border-radius: 15px; margin-bottom: 10px; max-width: 80%; }
        .bot { background: #e8f5e9; color: #1b5e20; align-self: flex-start; }
        .user { background: #2E7D32; color: white; margin-left: auto; }
        .input-area { display: flex; padding: 15px; background: #fff; border-top: 1px solid #eee; }
        input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #2E7D32; color: white; border: none; margin-left: 10px; cursor: pointer; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🌿 Eldoret Orchards Assistant</div>
        <div class="chat-box" id="chat-box">
            <div class="message bot">Hello! Ask me about fruit farming.</div>
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
            
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            addMessage(data.reply || data.error, "bot");
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
        return jsonify({"error": "System Error: API Key missing in Settings."}), 500
        
    user_input = request.json.get("message")
    try:
        response = model.generate_content(f"You are a farming expert. User asks: {user_input}")
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

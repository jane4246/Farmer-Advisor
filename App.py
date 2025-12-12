import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CONFIGURATION ---
# We are now using Groq (Free & Fast)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- FRONTEND (Same Beautiful Interface) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eldoret Orchards AI</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; height: 100vh; background: #eef2f5; margin: 0; }
        .chat-container { width: 100%; max-width: 500px; background: white; display: flex; flex-direction: column; box-shadow: 0 4px 20px rgba(0,0,0,0.1); height: 100%; }
        @media(min-width: 600px) { .chat-container { height: 90vh; margin-top: 5vh; border-radius: 12px; overflow: hidden; } }
        
        .chat-header { background: #2E7D32; color: white; padding: 20px; text-align: center; font-size: 1.2rem; font-weight: bold; }
        
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; background-color: #f9f9f9; display: flex; flex-direction: column; gap: 10px; }
        
        .message { padding: 10px 15px; border-radius: 15px; max-width: 80%; line-height: 1.4; font-size: 0.95rem; }
        .bot { background: #e8f5e9; color: #1b5e20; align-self: flex-start; border-bottom-left-radius: 2px; }
        .user { background: #2E7D32; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .error { background: #ffebee; color: #c62828; align-self: center; font-size: 0.8rem; }

        .input-area { display: flex; padding: 15px; background: #fff; border-top: 1px solid #eee; }
        input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none; transition: border 0.3s; }
        input:focus { border-color: #2E7D32; }
        button { padding: 10px 20px; background: #2E7D32; color: white; border: none; margin-left: 10px; cursor: pointer; border-radius: 25px; font-weight: bold; transition: background 0.2s; }
        button:hover { background: #1b5e20; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🌿 Eldoret Orchards Assistant</div>
        <div class="chat-box" id="chat-box">
            <div class="message bot">Hello! I am your AI assistant for fruit farming. Ask me about avocados, mangoes, or pests!</div>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Ask a question..." onkeypress="handleEnter(event)">
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
                
                if (data.reply) {
                    addMessage(data.reply, "bot");
                } else {
                    addMessage("Error: " + (data.error || "Unknown error"), "error");
                }
            } catch (err) {
                addMessage("Failed to connect to server.", "error");
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

# --- ROUTES ---

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    # 1. Check for Groq API Key
    if not GROQ_API_KEY:
        return jsonify({"error": "Server Error: GROQ_API_KEY missing."}), 500
        
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Empty message"}), 400
    
    # 2. Connect to Groq API
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # System prompt to make it an expert
    system_prompt = "You are a helpful agricultural expert for Eldoret Orchards in Kenya. Provide concise advice on growing avocados, mangoes, and passion fruit."

    payload = {
        "model": "llama3-8b-8192", # Free, fast, and smart model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            bot_reply = result['choices'][0]['message']['content']
            return jsonify({"reply": bot_reply})
        else:
            return jsonify({"error": f"Groq Error ({response.status_code}): {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

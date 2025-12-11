import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CONFIGURATION ---
# Get this key from https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Using 'gemini-1.5-flash' which is fast and free-tier eligible
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- CUSTOMIZE YOUR AI HERE ---
SYSTEM_PROMPT = """
You are a helpful and expert agricultural assistant for 'Eldoret Orchards Ltd'.
You specialize in growing avocados, passion fruits, and mangoes in Kenya.
Keep your answers concise, friendly, and practical for farmers.
If asked about prices, say: 'Please contact our sales team at sales@eldoretorchards.com for current prices.'
"""

# --- THE FRONTEND (HTML/CSS/JS) ---
# This is your own chat interface. No external branding!
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eldoret Orchards AI</title>
    <style>
        /* General Style */
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; height: 100vh; background: #eef2f5; margin: 0; }
        
        /* Chat Container */
        .chat-container { width: 100%; max-width: 500px; background: white; display: flex; flex-direction: column; box-shadow: 0 4px 20px rgba(0,0,0,0.1); height: 100%; }
        @media(min-width: 600px) { .chat-container { height: 90vh; margin-top: 5vh; border-radius: 12px; overflow: hidden; } }

        /* Header */
        .chat-header { background: #2E7D32; color: white; padding: 20px; text-align: center; font-size: 1.2rem; font-weight: bold; }
        
        /* Chat Messages Area */
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; background-color: #f9f9f9; display: flex; flex-direction: column; gap: 10px; }
        
        /* Message Bubbles */
        .message { padding: 10px 15px; border-radius: 15px; max-width: 80%; line-height: 1.4; font-size: 0.95rem; }
        .bot { background: #e8f5e9; color: #1b5e20; align-self: flex-start; border-bottom-left-radius: 2px; }
        .user { background: #2E7D32; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .error { background: #ffebee; color: #c62828; align-self: center; font-size: 0.8rem; }

        /* Input Area */
        .input-area { display: flex; padding: 15px; background: #fff; border-top: 1px solid #eee; }
        input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none; transition: border 0.3s; }
        input:focus { border-color: #2E7D32; }
        button { padding: 10px 20px; background: #2E7D32; color: white; border: none; margin-left: 10px; cursor: pointer; border-radius: 25px; font-weight: bold; transition: background 0.2s; }
        button:hover { background: #1b5e20; }
        button:disabled { background: #ccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🌿 Eldoret Orchards Assistant</div>
        <div class="chat-box" id="chat-box">
            <div class="message bot">Hello! I am your fruit farming assistant. How can I help you grow today?</div>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Ask about avocados, mangoes..." onkeypress="handleEnter(event)">
            <button id="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById("user-input");
            const btn = document.getElementById("send-btn");
            const box = document.getElementById("chat-box");
            
            const text = input.value.trim();
            if (!text) return;

            // 1. Add User Message
            addMessage(text, "user");
            input.value = "";
            input.disabled = true;
            btn.disabled = true;

            try {
                // 2. Send to Backend
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                
                // 3. Add Bot Response
                if (data.reply) {
                    addMessage(data.reply, "bot");
                } else {
                    addMessage("Error: " + (data.error || "Unknown error"), "error");
                }
            } catch (err) {
                addMessage("Failed to connect to server.", "error");
            }

            input.disabled = false;
            btn.disabled = false;
            input.focus();
        }

        function addMessage(text, sender) {
            const box = document.getElementById("chat-box");
            const div = document.createElement("div");
            div.className = "message " + sender;
            div.innerText = text;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }

        function handleEnter(e) {
            if (e.key === "Enter") sendMessage();
        }
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
    # 1. Check for API Key
    if not GOOGLE_API_KEY:
        return jsonify({"error": "Server Error: GOOGLE_API_KEY not set."}), 500

    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        # 2. Construct the full prompt (System instruction + User Question)
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {user_message}"
        
        # 3. Generate response
        response = model.generate_content(full_prompt)
        
        # 4. Return text
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Gemini Error: {e}")
        return jsonify({"error": "I'm having trouble connecting to the AI brain right now."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

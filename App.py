import os
import sys
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CONFIGURATION & DEBUGGING ---
# Fetch the key
GOOGLE_API_KEY = os.getenv("AIzaSyBEfvCU-bj-OvsW4LK4FUKw2qHBy5MPVdw")

# PRINT STATUS TO LOGS (Check your Render Logs tab!)
if not GOOGLE_API_KEY:
    print("❌ ERROR: The app started, but GOOGLE_API_KEY is None.", file=sys.stderr)
    print("   Please check spelling in Render Dashboard -> Environment.", file=sys.stderr)
else:
    print(f"✅ SUCCESS: API Key found! (Length: {len(GOOGLE_API_KEY)})", file=sys.stderr)
    # Only configure if key exists
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"⚠️ Warning: Key found but Gemini failed to load: {e}", file=sys.stderr)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are a helpful and expert agricultural assistant for 'Eldoret Orchards Ltd'.
You specialize in growing avocados, passion fruits, and mangoes in Kenya.
Keep your answers concise, friendly, and practical for farmers.
"""

# --- HTML FRONTEND ---
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
        .chat-header { background: #2E7D32; color: white; padding: 20px; text-align: center; font-size: 1.2rem; font-weight: bold; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; background-color: #f9f9f9; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 10px 15px; border-radius: 15px; max-width: 80%; line-height: 1.4; font-size: 0.95rem; }
        .bot { background: #e8f5e9; color: #1b5e20; align-self: flex-start; }
        .user { background: #2E7D32; color: white; align-self: flex-end; }
        .error { background: #ffebee; color: #c62828; align-self: center; font-size: 0.8rem; }
        .input-area { display: flex; padding: 15px; background: #fff; border-top: 1px solid #eee; }
        input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none; }
        button { padding: 10px 20px; background: #2E7D32; color: white; border: none; margin-left: 10px; cursor: pointer; border-radius: 25px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🌿 Eldoret Orchards Assistant</div>
        <div class="chat-box" id="chat-box">
            <div class="message bot">Hello! I am your fruit farming assistant. How can I help you grow today?</div>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Ask a question..." onkeypress="handleEnter(event)">
            <button id="send-btn" onclick="sendMessage()">Send</button>
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
                if (data.reply) addMessage(data.reply, "bot");
                else addMessage("Error: " + data.error, "error");
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
    # RELOAD KEY (Just in case it wasn't ready at startup)
    current_key = os.getenv("GOOGLE_API_KEY")
    
    if not current_key:
        print("❌ Request failed: GOOGLE_API_KEY missing.", file=sys.stderr)
        return jsonify({"error": "Server Error: GOOGLE_API_KEY not set. Check Render Logs."}), 500

    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        # Re-configure if needed (failsafe)
        genai.configure(api_key=current_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {user_message}"
        response = model.generate_content(full_prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"❌ Gemini API Error: {e}", file=sys.stderr)
        return jsonify({"error": f"AI Brain Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

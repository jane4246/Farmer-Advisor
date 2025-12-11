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
        .chat-header { background: #d32f2f; color: white; padding: 20px; text-align: center; font-weight: bold; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; background-color: #f9f9f9; }
        .message { padding: 10px 15px; border-radius: 15px; margin-bottom: 10px; max-width: 80%; }
        .bot { background: #e8f5e9; color: #1b5e20; align-self: flex-start; }
        .user { background: #2E7D32; color: white; align-self: flex-end; margin-left: auto; }
        .input-area { display: flex; padding: 15px; background: #fff; border-top: 1px solid #eee; }
        input { flex: 1; padding: 10px; border: 1px solid #ddd; }
        button { padding: 10px 20px; background: #d32f2f; color: white; border: none; margin-left: 10px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🛠️ Diagnostic Mode</div>
        <div class="chat-box" id="chat-box">
            <div class="message bot">I am in Diagnostic Mode. Type anything to test the connection.</div>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Type 'test'..." onkeypress="handleEnter(event)">
            <button onclick="sendMessage()">Test</button>
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
            
            // If we get a debug list, format it nicely
            if (data.debug_info) {
                 addMessage("⚠️ CONNECTION FAILED. Google says you have access to these models:", "bot");
                 addMessage(data.debug_info, "bot");
            } else {
                 addMessage(data.reply || data.error, "bot");
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
        return jsonify({"error": "API Key missing."}), 500
        
    user_input = request.json.get("message")

    # 1. Try to generate content using 'gemini-1.5-flash'
    target_model = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={GOOGLE_API_KEY}"
    
    payload = { "contents": [{ "parts": [{ "text": user_input }] }] }

    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            # IT WORKED!
            return jsonify({"reply": response.json()['candidates'][0]['content']['parts'][0]['text']})
        
        else:
            # 2. IF IT FAILED (404), ASK GOOGLE FOR THE LIST OF AVAILABLE MODELS
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GOOGLE_API_KEY}"
            list_response = requests.get(list_url)
            
            if list_response.status_code == 200:
                # We got the list! Let's show it to the user.
                models = list_response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                debug_msg = " | ".join(model_names)
                return jsonify({
                    "error": f"Model {target_model} failed.",
                    "debug_info": f"AVAILABLE MODELS: {debug_msg}"
                })
            else:
                # Even listing failed. The key is broken.
                return jsonify({"error": f"CRITICAL: Key rejected. Google said: {list_response.text}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

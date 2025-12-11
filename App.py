import os
from flask import Flask, request, jsonify
from relevanceai import RelevanceAI

app = Flask(__name__)

# SECURITY FIX: Load credentials from Environment Variables
# (We will set these up in the Render dashboard in the next step)
RELEVANCE_API_KEY = os.getenv("sk-NmZjMWExODMtODAwYy00YTlhLWFjZjAtYzU0ZWE3OGNiZmQ4")
RELEVANCE_PROJECT = "FruitAid"

# Initialize RelevanceAI client only if key exists (prevents crash on startup if key is missing)
client = None
if RELEVANCE_API_KEY:
    client = RelevanceAI(
        api_key=RELEVANCE_API_KEY,
        project=RELEVANCE_PROJECT,
        region="us-west"
    )

# 1. THE MISSING ROUTE (Fixes the 404 error)
@app.route("/", methods=["GET"])
def home():
    return "✅ Eldoret Orchards AI Service is Running! Use the /chat endpoint for requests."

# 2. YOUR CHAT ENDPOINT
@app.route("/chat", methods=["POST"])
def chat():
    # Safety check: Ensure client is ready
    if not client:
        return jsonify({"error": "Server misconfiguration: API Key missing"}), 500

    data = request.json
    # Safety check: Ensure JSON was actually sent
    if not data:
         return jsonify({"error": "Invalid JSON format"}), 400
         
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Create embedding for the user input
        response = client.embeddings.create(
            dataset="fruits_dataset", 
            records=[{"text": user_input}]
        )
        output_embedding = response["records"][0]["embedding"]
        return jsonify({"reply": f"Embedding generated with length {len(output_embedding)}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

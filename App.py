from flask import Flask, request, jsonify, send_from_directory
from relevanceai import RelevanceAIClient
import os

app = Flask(__name__, static_folder=".")

# Load API key from environment
RELEVANCE_KEY = os.environ.get("sk-NmZjMWExODMtODAwYy00YTlhLWFjZjAtYzU0ZWE3OGNiZmQ4")
client = RelevanceAIClient(api_key=RELEVANCE_KEY)

# Load your agent
AGENT_PATH = "agent.rai"
agent = client.agents.load(AGENT_PATH)

# Endpoint your frontend calls
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = agent.run(user_message)
    return jsonify({"reply": response})

# Serve frontend
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

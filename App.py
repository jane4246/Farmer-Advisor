from flask import Flask, request, jsonify
from relevanceai import RelevanceAIClient
import os

app = Flask(__name__)
client = RelevanceAIClient(api_key=os.environ.get("sk-ODU0ZTVlMWUtZjQ4My00NWIxLWIxMTYtMDJiYWJlMzM5YjUx    API key"))
agent_id = "9cf49e03-37cc-4752-9fc1-0c65a8dd5750"


@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_query = data.get("query")
    response = client.agent.run(user_query, agent_id=agent_id)
    return jsonify({"reply": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

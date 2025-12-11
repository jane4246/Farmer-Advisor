from flask import Flask, request, jsonify
from relevanceai import RelevanceAI

app = Flask(__name__)

# RelevanceAI credentials
RELEVANCE_API_KEY = "sk-NmZjMWExODMtODAwYy00YTlhLWFjZjAtYzU0ZWE3OGNiZmQ4"
RELEVANCE_PROJECT = "FruitAid"  # Your actual project name

# Initialize RelevanceAI client
client = RelevanceAI(
    api_key=RELEVANCE_API_KEY,
    project=RELEVANCE_PROJECT,
    region="us-west"  # Oregon region
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Create embedding for the user input
        response = client.embeddings.create(
            dataset="fruits_dataset",  # your dataset inside FruitAid
            records=[{"text": user_input}]
        )
        # Extract embedding (or you can generate a textual response from a model)
        output_embedding = response["records"][0]["embedding"]
        return jsonify({"reply": f"Embedding generated with length {len(output_embedding)}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

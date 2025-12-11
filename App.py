import os
from flask import Flask, request, jsonify
from relevanceai import RelevanceAI

app = Flask(__name__)

# --- CONFIGURATION ---
# We use os.getenv to read the key from Render's Environment Variables.
# DO NOT paste the actual 'sk-...' key here. 
# Paste it in the Render Dashboard under "Environment".
RELEVANCE_API_KEY = os.getenv("sk-NmZjMWExODMtODAwYy00YTlhLWFjZjAtYzU0ZWE3OGNiZmQ4")
RELEVANCE_PROJECT = "FruitAid"

# Initialize RelevanceAI client only if the key was found in the environment
client = None
if RELEVANCE_API_KEY:
    try:
        client = RelevanceAI(
            api_key=RELEVANCE_API_KEY,
            project=RELEVANCE_PROJECT,
            region="us-west"
        )
    except Exception as e:
        print(f"Warning: Failed to initialize RelevanceAI client: {e}")

# --- ROUTES ---

# 1. HOMEPAGE: Displays the Chat Interface
@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Eldoret Orchards AI Support</title>
      <style>
        body, html {
          margin: 0;
          padding: 0;
          height: 100%;
          font-family: Arial, sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          background-color: #f0f0f0;
        }
        iframe {
          width: 100%;
          max-width: 600px;
          height: 700px;
          border: none;
          border-radius: 10px;
          box-shadow: 0 4px 10px rgba(0,0,0,0.1);
          background-color: #ffffff;
        }
        /* Mobile Responsiveness: Full screen on small devices */
        @media (max-width: 600px) {
            iframe {
                max-width: 100%;
                height: 100%;
                border-radius: 0;
            }
        }
      </style>
    </head>
    <body>
      <iframe 
        src="https://app.relevanceai.com/agents/d7b62b/9cf49e03-37cc-4752-9fc1-0c65a8dd5750/57685344-a115-406c-89cf-30fdd36a5916/embed-chat?hide_tool_steps=false&hide_file_uploads=false&hide_conversation_list=false&bubble_style=agent&primary_color=%23685FFF&bubble_icon=pd%2Fchat&input_placeholder_text=Type+your+message...&hide_logo=true&hide_description=false"
        allow="microphone; autoplay">
      </iframe>
    </body>
    </html>
    """

# 2. CHAT ENDPOINT: Handles backend requests if needed
@app.route("/chat", methods=["POST"])
def chat():
    # Safety check: Ensure client is ready
    if not client:
        return jsonify({"error": "Server misconfiguration: API Key missing in Environment Variables"}), 500

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
        # Extract embedding
        if "records" in response and len(response["records"]) > 0:
            output_embedding = response["records"][0]["embedding"]
            return jsonify({"reply": f"Embedding generated with length {len(output_embedding)}"})
        else:
            return jsonify({"error": "Failed to generate embedding"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

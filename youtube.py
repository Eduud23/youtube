from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import requests
import os

app = Flask(__name__)

# Enable CORS for the entire app
CORS(app)

# Set API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY2")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

def get_search_query(user_query):
    """Generate a simplified search query using Gemini AI."""
    prompt = f"Convert this into a simple educational YouTube search query: {user_query}"
    
    response = model.generate_content(prompt)
    search_query = response.text.strip()
    
    # If Gemini outputs something too complex, return None
    if len(search_query.split()) > 10:  # Arbitrary complexity check
        return None
    return search_query

def search_youtube(query):
    """Search YouTube for educational videos based on the query."""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&maxResults=10&type=video&key={YOUTUBE_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if "items" in data:
        return [
            f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            for item in data["items"]
        ]
    return []

@app.route("/search", methods=["GET"])
def search():
    user_query = request.args.get("query", "")

    # If no query is provided, return an error message
    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    print(f"User query received: {user_query}")  # Log for debugging

    search_query = get_search_query(user_query)
    if search_query:
        videos = search_youtube(search_query)
        return jsonify({"search_query": search_query, "videos": videos})
    else:
        return jsonify({"message": "This topic is too complex. No video suggestions."})

if __name__ == "__main__":
    app.run(debug=True)

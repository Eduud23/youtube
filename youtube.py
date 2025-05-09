from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import requests
import os
import re

app = Flask(__name__)
CORS(app)

# Set API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY2")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def get_search_query(user_query):
    """Generate a simplified search query using Gemini AI and extract the first suggestion."""
    prompt = f"Convert this into a short and simple YouTube search query for an educational video: {user_query}"

    try:
        response = model.generate_content(prompt)
        full_text = response.text.strip()

        # Extract the first quoted string (e.g., "how to change a tire")
        match = re.search(r'"([^"]+)"', full_text)
        if match:
            return match.group(1)
        else:
            # If no quotes found, fallback to first line or the entire response
            return full_text.splitlines()[0]
    except Exception as e:
        print(f"Gemini error: {e}")
        return user_query  # Fallback to original query

def search_youtube(query):
    """Search YouTube for educational videos based on the query."""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&maxResults=10&type=video&key={YOUTUBE_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if "items" in data:
        video_details = []
        for item in data["items"]:
            thumbnail_url = item["snippet"]["thumbnails"].get("default", {}).get("url", "")
            
            video_details.append({
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "description": item["snippet"].get("description", "No description available."),
                "channelTitle": item["snippet"]["channelTitle"],
                "thumbnail": thumbnail_url
            })
        return video_details
    return []

@app.route("/search", methods=["GET"])
def search():
    user_query = request.args.get("query", "")

    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    print(f"User query received: {user_query}")  # Debugging

    search_query = get_search_query(user_query)
    if search_query:
        videos = search_youtube(search_query)
        return jsonify({"search_query": search_query, "videos": videos})
    else:
        return jsonify({"message": "This topic is too complex. No video suggestions."})

if __name__ == "__main__":
    app.run(debug=True)

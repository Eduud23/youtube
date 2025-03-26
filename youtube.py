from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import requests
import os

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY2")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

def get_vehicle_related_query(user_query):
    """Ensure the query is related to vehicles."""
    prompt = f"Convert this into a vehicle-related YouTube search query: {user_query}"
    
    response = model.generate_content(prompt)
    search_query = response.text.strip()
    
    if len(search_query.split()) > 10:
        return None
    return search_query

def search_youtube(query):
    """Search YouTube for vehicle-related videos."""
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
    
    print(f"User query received: {user_query}")
    
    search_query = get_vehicle_related_query(user_query)
    if search_query:
        videos = search_youtube(search_query)
        return jsonify({"search_query": search_query, "videos": videos})
    else:
        return jsonify({"message": "This topic is not vehicle-related. No video suggestions."})

if __name__ == "__main__":
    app.run(debug=True)

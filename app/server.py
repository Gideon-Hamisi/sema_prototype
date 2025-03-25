# app/server.py
from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Load mock data
data_path = os.path.join(os.path.dirname(__file__), '../data/mock_data.json')
with open(data_path, 'r') as f:
    mock_data = json.load(f)

@app.route('/process', methods=['POST'])
def process_command():
    command = request.json.get('command', '').lower()
    response = ""

    # Weather Updates
    if "weather" in command and "nairobi" in command:
        weather = mock_data["weather"]["Nairobi"]
        response = f"Sema, bro! Nairobi’s at {weather}, but clouds might roll in later."
    
    # News Headlines
    elif "news" in command:
        news_list = ", ".join(mock_data["news"])
        response = f"Sema! Top headlines: {news_list}. Want more?"
    
    # M-Pesa Balance Check
    elif "m-pesa balance" in command:
        balance = mock_data["mpesa_balance"]
        response = f"Sema, let’s see… Your balance is {balance} bob."
    
    # Music Playback
    elif "play" in command and "music" in command:
        song = mock_data["music_playlist"][0]  # Pick the first song
        response = f"Sema, time to vibe! Playing ‘{song}’."
    
    # Default response
    else:
        response = "Sema, I’m not sure what you mean. Try again?"

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
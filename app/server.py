# app/server.py
from flask import Flask, request, jsonify, send_from_directory
import requests
import spacy
import sqlite3
import os

app = Flask(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# API Keys
OPENWEATHERMAP_API_KEY = "233102f5def6465624c7283bf7af03b3"
NEWSAPI_KEY = "2b4df1604d5e47529c8ab4f26315eed2"

# SQLite setup
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, mpesa_balance INTEGER)")
    conn.commit()
    conn.close()

@app.route('/process', methods=['POST'])
def process_command():
    command = request.json.get('command', '').lower()
    user_id = request.json.get('user_id', 'default_user')
    doc = nlp(command)
    response = ""

    intent = None
    city = None
    for token in doc:
        if token.lemma_ == "stop":
            intent = "stop_music"
            break
        elif token.lemma_ == "pause":
            intent = "pause_music"
            break
        elif token.lemma_ == "resume":
            intent = "resume_music"
            break
        elif token.lemma_ in ["weather", "forecast"]:
            intent = "weather"
        elif token.lemma_ in ["news", "headlines"]:
            intent = "news"
        elif token.lemma_ in ["balance", "mpesa"]:
            intent = "mpesa"
        elif token.lemma_ in ["play", "music", "sing"]:
            intent = "music"
        elif token.ent_type_ == "GPE":
            city = token.text

    if intent == "weather":
        cities = ["nairobi", "mombasa", "kisumu", "eldoret"]
        if city and city.lower() in cities:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city},ke&appid={OPENWEATHERMAP_API_KEY}&units=metric"
            weather_data = requests.get(url).json()
            if weather_data.get("cod") == 200:
                temp = weather_data["main"]["temp"]
                desc = weather_data["weather"][0]["description"]
                response = f"Sema, bro! {city.capitalize()}’s at {temp}°C, {desc}."
            else:
                response = f"Sema! Couldn’t fetch weather for {city}."
        else:
            response = "Sema! Which city’s weather? Nairobi, Mombasa, Kisumu, or Eldoret?"
    elif intent == "news":
        url = f"https://newsapi.org/v2/top-headlines?country=ke&apiKey={NEWSAPI_KEY}"
        news_data = requests.get(url).json()
        if news_data.get("status") == "ok":
            headlines = [article["title"] for article in news_data["articles"][:5]]
            response = f"Sema! Top headlines: {', '.join(headlines)}."
        else:
            response = "Sema! Couldn’t fetch the news right now."
    elif intent == "mpesa":
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, mpesa_balance) VALUES (?, ?)", (user_id, 1200))
        c.execute("SELECT mpesa_balance FROM users WHERE user_id = ?", (user_id,))
        balance = c.fetchone()[0]
        response = f"Sema, let’s see… Your balance is {balance} bob."
        conn.commit()
        conn.close()
    elif intent == "music":
        response = "Sema, time to vibe! Playing a tune for you."
    elif intent == "stop_music":
        response = "Sema! Stopping the music, bro."
    elif intent == "pause_music":
        response = "Sema! Pausing the music, bro."
    elif intent == "resume_music":
        response = "Sema! Resuming the music, bro."
    else:
        response = "Sema, I’m not sure what you mean. Try again?"

    return jsonify({"response": response, "intent": intent})

@app.route('/music/<filename>')
def serve_music(filename):
    return send_from_directory("app", filename)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sema Prototype</title>
    </head>
    <body>
        <h1>Sema Prototype</h1>
        <p>Speak a command: "Weather in Nairobi," "Play some music," "Pause the music," etc.</p>
        <audio id="player" controls>
            <source src="/music/sample_song.mp3" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <p id="response">Listening...</p>
        <script>
            const player = document.getElementById('player');
            const responseP = document.getElementById('response');
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = function(event) {
                const command = event.results[event.results.length - 1][0].transcript.toLowerCase();
                console.log("You said: " + command);
                fetch('/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: command, user_id: 'user123'})
                })
                .then(response => response.json())
                .then(data => {
                    responseP.textContent = data.response;
                    if (data.intent === 'music') player.play();
                    if (data.intent === 'stop_music') {
                        player.pause();
                        player.currentTime = 0;
                    }
                    if (data.intent === 'pause_music') player.pause();
                    if (data.intent === 'resume_music') player.play();
                    const utterance = new SpeechSynthesisUtterance(data.response);
                    window.speechSynthesis.speak(utterance);
                })
                .catch(error => console.error('Error:', error));
            };

            recognition.onerror = function(event) {
                responseP.textContent = "Error: " + event.error;
            };

            recognition.onend = function() {
                recognition.start(); // Restart listening
            };

            recognition.start();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Heroku sets PORT
    app.run(debug=False, host='0.0.0.0', port=port)
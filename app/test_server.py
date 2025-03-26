# app/test_server.py
import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_weather_command(client):
    response = client.post('/process', json={"command": "weather in nairobi"})
    assert response.status_code == 200
    assert "Sema, bro! Nairobi’s at" in response.json["response"]

def test_news_command(client):
    response = client.post('/process', json={"command": "tell me the news"})
    assert response.status_code == 200
    assert "Sema! Top headlines:" in response.json["response"]

def test_mpesa_command(client):
    response = client.post('/process', json={"command": "check my mpesa balance", "user_id": "test_user"})
    assert response.status_code == 200
    assert "Sema, let’s see… Your balance is" in response.json["response"]

def test_unknown_command(client):
    response = client.post('/process', json={"command": "do something random"})
    assert response.status_code == 200
    assert "Sema, I’m not sure what you mean" in response.json["response"]

def test_music_command(client):
    response = client.post('/process', json={"command": "play some music"})
    assert response.status_code == 200
    assert "Sema, time to vibe! Playing a tune for you." in response.json["response"]
    assert response.json["intent"] == "music"

def test_stop_music_command(client):
    response = client.post('/process', json={"command": "stop the music"})
    assert response.status_code == 200
    assert "Sema! Stopping the music, bro." in response.json["response"]
    assert response.json["intent"] == "stop_music"

def test_pause_music_command(client):
    response = client.post('/process', json={"command": "pause the music"})
    assert response.status_code == 200
    assert "Sema! Pausing the music, bro." in response.json["response"]
    assert response.json["intent"] == "pause_music"

def test_resume_music_command(client):
    response = client.post('/process', json={"command": "resume the music"})
    assert response.status_code == 200
    assert "Sema! Resuming the music, bro." in response.json["response"]
    assert response.json["intent"] == "resume_music"
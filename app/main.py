# app/main.py
import speech_recognition as sr
import pyttsx3
import requests
import pygame.mixer
import os

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Initialize pygame mixer
pygame.mixer.init()

def speak(text):
    print(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Recognition failed: Didn’t catch that.")
            return "Sorry, didn’t catch that."
        except sr.RequestError:
            print("Recognition failed: Network error.")
            return "Network error, can’t connect."

def send_to_server(command):
    url = "http://localhost:5000/process"
    payload = {"command": command, "user_id": "user123"}
    try:
        response = requests.post(url, json=payload)
        print(f"Server response: {response.json()}")
        return response.json()["response"], response.json().get("intent")
    except requests.RequestException as e:
        print(f"Server error: {e}")
        return "Sema! Server’s down, bro.", None

def handle_command(command):
    if "sorry" not in command.lower() and "network" not in command.lower():
        response, intent = send_to_server(command)
        speak(response)
        music_path = os.path.join(os.path.dirname(__file__), "app", "sample_song.mp3")
        if intent == "music":
            try:
                print("Attempting to play music...")
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play()
                print("Music started.")
            except Exception as e:
                speak("Sema! Couldn’t play the tune, bro.")
                print(f"Music playback error: {e}")
        elif intent == "stop_music":
            try:
                print("Attempting to stop music...")
                pygame.mixer.music.stop()
                print("Music stopped.")
            except Exception as e:
                speak("Sema! Couldn’t stop the tune, bro.")
                print(f"Music stop error: {e}")
        elif intent == "pause_music":
            try:
                print("Attempting to pause music...")
                pygame.mixer.music.pause()
                print("Music paused.")
            except Exception as e:
                speak("Sema! Couldn’t pause the tune, bro.")
                print(f"Music pause error: {e}")
        elif intent == "resume_music":
            try:
                print("Attempting to resume music...")
                pygame.mixer.music.unpause()
                print("Music resumed.")
            except Exception as e:
                speak("Sema! Couldn’t resume the tune, bro.")
                print(f"Music resume error: {e}")
    else:
        speak(command)

def start_sema():
    speak("Sema! I’m ready—what’s up?")
    while True:
        command = listen()
        handle_command(command)

if __name__ == "__main__":
    try:
        start_sema()
    except KeyboardInterrupt:
        print("Shutting down...")
        pygame.mixer.music.stop()
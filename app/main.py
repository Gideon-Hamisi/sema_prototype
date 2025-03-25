# app/main.py
import speech_recognition as sr
import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speed for a natural feel
engine.setProperty('volume', 0.9)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Calibrate for noise
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            return "Sorry, didn’t catch that."
        except sr.RequestError:
            return "Network error, can’t connect."

def start_sema():
    speak("Sema! I’m ready—what’s up?")
    command = listen()
    speak(f"Sema! You said: {command}")

if __name__ == "__main__":
    start_sema()
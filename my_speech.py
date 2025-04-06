import speech_recognition as sr

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "❌ Could not understand audio"
    except sr.RequestError:
        return "❌ Could not request results; check your internet"

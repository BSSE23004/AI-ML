import speech_recognition as sr
import webbrowser
import pyttsx3

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        # using getattr to call recognize_google so static analyzers that lack stubs won't flag it
        command = getattr(recognizer, "recognize_google")(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return ""
    except sr.RequestError:
        print("Could not request results; check your network connection.")
        return ""
 
def start():
    while True:
        while True:
            command = listen()
            if "jarvis" in command:
                speak("Yes, how can I help you?")
                command = listen()
                break
        if "open youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        elif "open google" in command:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")
        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            break
        else:
            speak("Sorry, I can't help with that yet.")



if __name__ == "__main__":
    speak("Hello, I am Jarvis. How can I assist you today?")
    print("Jarvis is online.")
    #listen for wake word jarvis
    start()
    
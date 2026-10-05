import speech_recognition as sr
import pyttsx3
import datetime
import warnings
import wikipedia
from bs4 import GuessedAtParserWarning
import webbrowser
import os
import pyjokes
import re
from urllib.parse import quote_plus

def speak(text):
    print(f"Assistant: {text}")
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except:
        print("Speech output not supported in CLI")
def greet_user():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I'm your voice assistant. How can I help you this fine day?")
def command():
    return input("You (your query): ")
def run_assistant():
    greet_user()
    while True:
        query_orig = command()
        query = query_orig.lower()
        url_match = re.search(r'https?://[^\s<>"]+|www\.[^\s<>"]+', query)
        #print(query)
        if 'exit' in query or 'bye' in query:
            speak("Goodbye! Have a nice day.")
            break
        elif url_match:  
            if url_match is not None:
                url = url_match.group(0)
                speak(f"Opening {url}")
                webbrowser.open(url)
        elif 'joke' in query:
            joke = pyjokes.get_joke()
            speak(joke)
        elif 'wikipedia' in query:
            speak("Wikipedia part still needs to be fixed dot dot dot but anyways dot dot dot")
            speak("Searching Wikipedia...")
            query = query_orig.replace("wikipedia", "")
            #print(query)
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", GuessedAtParserWarning)
                    result = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia:")
                speak(result)
            except:
                speak("Sorry I couldn't find anything on the subject")
        else:
            qued = quote_plus(query)
            speak(f"Redirecting you to the web about {query}")
            webbrowser.open(f'https://www.google.com/search?q={qued}')

    print("Assistant session ended.")

run_assistant()

        
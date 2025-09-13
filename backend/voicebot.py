## Run these commands before executing:
## Terminal 1: rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml
## Terminal 2: rasa run actions

import requests
import speech_recognition as sr
from gtts import gTTS
from translate import Translator
from pydub import AudioSegment
from pydub.playback import play

bot_message = ""
message = ""

translator_hi = Translator(to_lang='hi')

def speak(text):
    #Convert text to Hindi TTS and play
    tts = gTTS(text=translator_hi.translate(text), lang='hi')
    tts.save("welcome.mp3")
    song = AudioSegment.from_mp3("welcome.mp3")
    play(song)

# Initial greeting
r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": "Hello"})
print("Bot says: ", end='')
for i in r.json():
    if 'text' in i:
        bot_message = i['text']
        print(bot_message)
    else:
        print("Bot response:", i)
print("Bot says: ", end='')
bot_message = ""
for i in r.json():
    if 'text' in i:
        bot_message = i['text']
        print(bot_message)
    else:
        print("Bot response:", i)  # debug print for non-text messages

# Only speak if there is something to say
if bot_message:
    speak(bot_message)

# Chat loop
while bot_message.lower() not in ["bye", "thanks"]:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak Anything :")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            message = recognizer.recognize_google(audio)
            translator_en = Translator(to_lang='en')
            print("You said:", translator_en.translate(message))
            message_en = translator_en.translate(message)
        except:
            print("Sorry could not recognize your voice")
            continue

    print("Sending message now...")
    r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message_en})

    print("Bot says: ", end='')
    for i in r.json():
        bot_message = i['text']
        print(bot_message)
    speak(bot_message)

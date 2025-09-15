# from fastapi import FastAPI
# from pydantic import BaseModel
# import requests
# from googletrans import Translator
# from langdetect import detect
# from db import save_message, get_chat_history  # Import MongoDB helpers
# from twilio.twiml.messaging_response import MessagingResponse

# app = FastAPI()
# translator = Translator()
# RASA_URL = "http://localhost:5005/webhooks/rest/webhook"  # your Rasa endpoint

# class ChatRequest(BaseModel):
#     message: str
#     # user_id: str = "default"

# @app.post("/chat")
# async def chat(request: ChatRequest):
#     user_msg = request.message  
#     # user_msg=user_msg.lower().strip()
#     user_id = request.user_id

#     # 1️ Detect user language using Google Translate detection
#     detected = translator.detect(user_msg)
#     lang = detected.lang if detected.lang else "en"

#     # 2️ Translate user message → English
#     if lang != "en":
#         translated_in = translator.translate(user_msg, src=lang, dest="en")
#         rasa_input = translated_in.text
#     else:
#         rasa_input = user_msg

#     # 3 Retrieve previous chat history
#     # history = await get_chat_history(user_id)
#     # context = {}

#     # 4 Send message to Rasa
#     payload = {"sender": user_id, "message": rasa_input}
#     rasa_response = requests.post(RASA_URL, json=payload).json()

#     # 5 Translate Rasa response → user language and save chat
#     replies = []
#     for resp in rasa_response:
#         text_en = resp.get("text", "")
#         if text_en:
#             if lang != "en":
#                 text_out = translator.translate(text_en, src="en", dest=lang).text
#             else:
#                 text_out = text_en

#             replies.append(text_out)

#             # Save chat to DB
#             # await save_message(user_id, user_msg, text_out, context)

#     return {"replies": replies, "language": lang}
from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
import requests
from googletrans import Translator
from langdetect import detect
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()
translator = Translator()
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"  # your Rasa endpoint

@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    user_id = From  # WhatsApp number
    user_msg = Body.strip()

    # 1️ Detect language
    try:
        lang = detect(user_msg)
    except:
        lang = "en"

    # 2️ Translate to English if not already
    rasa_input = translator.translate(user_msg, src=lang, dest="en").text if lang != "en" else user_msg

    # 3️ Send to Rasa
    payload = {"sender": user_id, "message": rasa_input}
    rasa_response = requests.post(RASA_URL, json=payload).json()

    # 4️ Pick first Rasa reply (or fallback)
    reply_text = "Sorry, I didn’t understand."
    for resp in rasa_response:
        if resp.get("text"):
            reply_text = resp["text"]
            break

    # 5️ Translate back to user’s language if needed
    if lang != "en":
        reply_text = translator.translate(reply_text, src="en", dest=lang).text

    # 6️ Return TwiML so Twilio sends WhatsApp reply
    twiml = MessagingResponse()
    twiml.message(reply_text)
    return str(twiml)

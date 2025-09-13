from fastapi import FastAPI
from pydantic import BaseModel
import requests
from googletrans import Translator
from langdetect import detect

app = FastAPI()
translator = Translator()
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# Define request model for Swagger
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"   # optional, default "default"

@app.post("/chat")
async def chat(request: ChatRequest):
    user_msg = request.message
    user_id = request.user_id

    # 1. Detect language of user
    lang = detect(user_msg)

    # 2. Translate user message → English
    translated_in = translator.translate(user_msg, src=lang, dest="en")

    # 3. Send to Rasa bot
    rasa_payload = {"sender": user_id, "message": translated_in.text}
    rasa_response = requests.post(RASA_URL, json=rasa_payload).json()

    # 4. Translate Rasa response → user’s language
    replies = []
    for resp in rasa_response:
        text_en = resp.get("text", "")
        if text_en:
            text_out = translator.translate(text_en, src="en", dest=lang).text
            replies.append(text_out)

    return {"replies": replies, "language": lang}

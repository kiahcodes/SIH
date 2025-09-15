from motor.motor_asyncio import AsyncIOMotorClient

# 1️⃣ MongoDB server connection
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)

# 2️⃣ Database and collection
database = client.SIH  # your database
chat_collection = database.get_collection("chat_context")  # collection for chat history

# 3️⃣ Helper function to save messages
async def save_message(user_id: str, message: str, reply: str, context: dict = None):
    doc = {
        "user_id": user_id,
        "message": message,
        "reply": reply,
        "context": context or {}
    }
    result = await chat_collection.insert_one(doc)
    return result.inserted_id

# 4️⃣ Helper function to get chat history
async def get_chat_history(user_id: str):
    cursor = chat_collection.find({"user_id": user_id})
    history = []
    async for doc in cursor:
        history.append(doc)
    return history

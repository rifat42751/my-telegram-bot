import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai

# পরিবেশ ভ্যারিয়েবল থেকে তথ্য গ্রহণ
API_ID = int(os.environ.get("API_ID", "36475164"))
API_HASH = os.environ.get("API_HASH", "b98551705c8ccd85509aabdc5e6c0548")
STRING_SESSION = os.environ.get("STRING_SESSION")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini AI কনফিগারেশন
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Telethon ক্লায়েন্ট চালু
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    # শুধু প্রাইভেট মেসেজে উত্তর দেবে
    if event.is_private:
        user_prompt = event.text
        
        # মেসেজ পেলে Gemini AI উত্তর জেনারেট করবে
        try:
            response = model.generate_content(
                f"You are a helpful assistant. Provide clear responses or summaries in Bengali if the user asks in Bengali:\n\n{user_prompt}"
            )
            await event.reply(response.text)
        except Exception as e:
            await event.reply("দুঃখিত, উত্তর তৈরি করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

print("Bot is running 24/7...")
client.start()
client.run_until_disconnected()

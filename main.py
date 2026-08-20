import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai

# Render Port Binding bypass
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# Environment variables
API_ID = int(os.environ.get("API_ID", "36475164"))
API_HASH = os.environ.get("API_HASH", "b98551705c8ccd85509aabdc5e6c0548")
STRING_SESSION = os.environ.get("STRING_SESSION")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# আপডেটেড মডেল নেম ব্যবহার
model = genai.GenerativeModel("gemini-2.5-flash")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    # নিজের মেসেজ বা বট মেসেজে যাতে লুপ না হয়
    if event.is_private and not event.out:
        user_prompt = event.text
        if not user_prompt:
            return
            
        try:
            response = model.generate_content(
                f"You are a helpful Telegram AI assistant. Provide concise and natural responses. Answer in Bengali if the message is in Banglish or Bengali:\n\n{user_prompt}"
            )
            if response.text:
                await event.reply(response.text)
        except Exception as e:
            # সমস্যা চিহ্নিত করার জন্য ব্যাকআপ মডেল দিয়ে চেষ্টা
            try:
                fallback_model = genai.GenerativeModel("gemini-1.5-pro")
                res = fallback_model.generate_content(user_prompt)
                await event.reply(res.text)
            except Exception as err:
                print(f"Error: {err}")

print("Bot is running successfully...")
client.start()
client.run_until_disconnected()

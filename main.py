import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai

# Render Port Binding bypass করার জন্য Dummy Server
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

# ব্যাকগ্রাউন্ডে ডামি পোর্টে সার্ভার চালু
threading.Thread(target=run_dummy_server, daemon=True).start()

# Environment variables থেকে ডাটা গ্রহণ
API_ID = int(os.environ.get("API_ID", "36475164"))
API_HASH = os.environ.get("API_HASH", "b98551705c8ccd85509aabdc5e6c0548")
STRING_SESSION = os.environ.get("STRING_SESSION")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    if event.is_private:
        user_prompt = event.text
        try:
            response = model.generate_content(
                f"You are a helpful Telegram AI assistant. Answer clearly or summarize as requested. Respond in Bengali if the query is in Bengali:\n\n{user_prompt}"
            )
            await event.reply(response.text)
        except Exception as e:
            await event.reply("দুঃখিত, উত্তর তৈরি করতে সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।")

print("Bot is running successfully...")
client.start()
client.run_until_disconnected()

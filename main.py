import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai

# Port Binding Bypass
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# Configs
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
        text = event.text
        if not text:
            return
            
        try:
            response = model.generate_content(text)
            if response and response.text:
                await event.reply(response.text)
        except Exception as e:
            # আসল আসল টেকনিক্যাল এরর সরাসরি টেলিগ্রাম চ্যাটে পাঠিয়ে দেবে
            await event.reply(f"❌ Error Code: {type(e).__name__}\nDetails: {str(e)}")

print("Bot is running...")
client.start()
client.run_until_disconnected()

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
model = genai.GenerativeModel("gemini-1.5-flash")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage)
async def handle_message(event):
    # বট যেন নিজের তৈরি করা উত্তরে পুনরায় উত্তর না দেয় (লুপ বন্ধ রাখা)
    me = await client.get_me()
    
    if event.is_private:
        # মেসেজ খালি হলে বা নিজের বটের রিপ্লাই মেসেজ হলে স্কিপ করবে
        if not event.text or (event.out and event.text.startswith("🤖 AI:")):
            return

        user_prompt = event.text
        
        try:
            response = model.generate_content(
                f"You are a helpful Telegram AI assistant. Provide concise and clear answers. Respond in Bengali if the text is in Bengali or Banglish:\n\n{user_prompt}"
            )
            if response.text:
                await event.reply(f"🤖 AI:\n{response.text}")
        except Exception as e:
            print(f"Gemini API Error: {e}")

print("Bot is running successfully...")
client.start()
client.run_until_disconnected()

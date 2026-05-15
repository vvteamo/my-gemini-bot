import os
import telebot
from google import genai
from google.genai import types

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """
You are Gemini, an experienced business assistant and developer.
You are helping Vova and Artem with their projects.
CRITICAL: Always reply in Russian language.
Keep your answers clear, concise, and professional.
"""

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)
chat_sessions = {}

def get_or_create_chat(chat_id):
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7
            )
        )
    return chat_sessions[chat_id]

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text.startswith('/'):
        return

    chat_id = message.chat.id
    user_name = message.from_user.first_name or "User"
    formatted_prompt = f"[{user_name}]: {message.text}"
    
    try:
        chat = get_or_create_chat(chat_id)
        response = chat.send_message(formatted_prompt)
        bot.reply_to(message, response.text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Error processing request.")

if __name__ == "__main__":
    print("Bot started successfully on Railway...")
    bot.infinity_polling()

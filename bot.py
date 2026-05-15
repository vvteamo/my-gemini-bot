import os
import telebot
from groq import Groq

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GEMINI_API_KEY")  # Специально оставляем старое имя, чтобы не переделывать настройки в Railway

SYSTEM_INSTRUCTION = """
You are a helpful business assistant.
You are helping Vova and Artem with their projects.
CRITICAL: Always reply in Russian language.
Keep your answers clear, concise, and professional.
"""

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text.startswith('/'):
        return

    chat_id = message.chat.id
    user_name = message.from_user.first_name or "User"
    
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
        
    chat_histories[chat_id].append({"role": "user", "content": f"[{user_name}]: {message.text}"})
    
    try:
        # Используем мощную и бесплатную модель Llama 3 70B
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_histories[chat_id],
            temperature=0.7,
        )
        response_text = completion.choices[0].message.content
        chat_histories[chat_id].append({"role": "assistant", "content": response_text})
        
        try:
            bot.reply_to(message, response_text, parse_mode="Markdown")
        except Exception:
            bot.reply_to(message, response_text)
            
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Error processing request.")

if __name__ == "__main__":
    print("Bot started successfully on Railway via Groq...")
    bot.infinity_polling()

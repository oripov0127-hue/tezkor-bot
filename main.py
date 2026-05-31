import os
import telebot
import time
from yt_dlp import YoutubeDL
from flask import Flask
import threading

# Bot Token va Kanal sozlamalari
BOT_TOKEN = '8754283301:AAFNGXEDaOOKegOP4-T12S1ALJFNJAPzR30'
KANAL_ID = '@oripov27'  # Sizning kanalingiz
KANAL_LINK = 'https://t.me/oripov27'

bot = telebot.TeleBot(BOT_TOKEN)

# Render serveri o'chib qolmasligi uchun Flask veb-server yaratamiz
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Kanalga a'zolikni tekshirish funksiyasi
def check_membership(user_id):
    try:
        member = bot.get_chat_member(KANAL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        # Agar bot kanalda admin bo'lmasa yoki xato yuz bersa, bot to'xtab qolmasligi uchun True qaytaradi
        return True

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        bot.reply_to(message, "Salom! Men Tezkor Yuklovchi botman. 🚀\nMenga Instagram Reels, TikTok yoki YouTube Shorts havolasini yuboring!")
    else:
        # Agar a'zo bo'lmasa, ogohlantirish va kanal linkini yuborish
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Kanalga a'zo bo'lish ➕", url=KANAL_LINK)
        markup.add(btn)
        bot.send_message(message.chat.id, f"⚠️ Botdan foydalanish uchun avval kanalimizga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    # Har bir xabarda a'zolikni tekshiramiz
    if not check_membership(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Kanalga a'zo bo'lish ➕", url=KANAL_LINK)
        markup.add(btn)
        bot.send_message(message.chat.id, f"⚠️ Botdan foydalanish uchun avval kanalimizga a'zo bo'ling!", reply_markup=markup)
        return

    url = message.text
    if "instagram.com" in url or "tiktok.com" in url or "youtube.com" in url or "youtu.be" in url:
        msg = bot.reply_to(message, "Video yuklab olinmoqda... ⏳")
        
        ydl_opts = {
            'outtmpl': 'tezkor_video.mp4',
            'format': 'mp4/best',
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('tezkor_video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, caption="Mana siz so'ragan video! 🚀\n\n@Tezkor_yuklovchi_bot_bot")
            
            os.remove('tezkor_video.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"Yuklashda xatolik bo'ldi ❌\nQayta urinib ko'ring.", message.chat.id, msg.message_id)
            if os.path.exists('tezkor_video.mp4'):
                os.remove('tezkor_video.mp4')
    else:
        bot.reply_to(message, "Iltimos, faqat to'g'ri video havolasini yuboring! ⚠️")

# Botni alohida oqimda (thread) yurgizish
def run_bot():
    print("Tezkor Yuklovchi Bot muvaffaqiyatli ishga tushdi...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    # Flask va Telegram Botni bir vaqtda ishga tushiramiz
    t = threading.Thread(target=run_bot)
    t.start()
    run_flask()
          

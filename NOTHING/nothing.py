import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date

# Token va admin ID
TOKEN = "7806083873:AAHwWEeJeM1jI9WyRm4BdY6c9wB0PCRuOPU"
ADMIN_ID = 907402803
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchini bazaga saqlash
def save_user(user_id, username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Jadval yaratish (agar hali yo'q bo‘lsa)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        joined_date TEXT)''')

    # Agar foydalanuvchi yo‘q bo‘lsa, qo‘shamiz
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, username, joined_date) VALUES (?, ?, ?)",
                       (user_id, username, date.today().isoformat()))

    conn.commit()
    conn.close()

# Foydalanuvchilarning ID'larini olish
def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    conn.close()
    return [user[0] for user in users]

# Statistikani olish
def get_stats():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE joined_date=?", (date.today().isoformat(),))
    today_users = cursor.fetchone()[0]

    conn.close()
    return total_users, today_users

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.from_user.id, message.from_user.username)

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🔍 Explore", url="t.me/probabliy_nothingbot"),
        InlineKeyboardButton("🐝 Earn", url="t.me/probabliy_nothingbot"),
        InlineKeyboardButton("👥 Community", url="https://t.me/probably_nothing_communitiy")
    )

    # Notcoin gif linki
    gif_url = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWpocGd3NWM0bXdkZXJuczR0dnR4bXhiaHAweXY2ZDRtbGZhNnh2ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YXPhGdkZSWfr1fFpc8/giphy.gif"

    bot.send_animation(
        chat_id=message.chat.id,
        animation=gif_url,
        caption="*Probably Nothing. TAPPP...*\n\nMaybe nothing, maybe everything.",
        parse_mode="Markdown",
        reply_markup=markup
    )

# /stats komandasi (faqat admin uchun)
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        total, today = get_stats()
        bot.send_message(message.chat.id, f"👥 Jami foydalanuvchilar: {total}\n\n📅 Bugun qo‘shilganlar: {today}")
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat admin uchun!")

# /broadcast komandasi (faqat admin uchun)
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        # Xabarni olish
        msg = message.text[11:]  # Xabarni /broadcast dan keyin olish
        
        if msg:
            users = get_all_users()
            for user_id in users:
                try:
                    bot.send_message(user_id, msg)
                except Exception as e:
                    print(f"Xatolik: {e}")
            bot.send_message(message.chat.id, "📢 Barcha foydalanuvchilarga xabar yuborildi!")
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, xabarni kiriting.")
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat admin uchun!")

# Botni ishga tushurish
bot.polling()

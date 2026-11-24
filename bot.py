from flask import Flask
import threading
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.environ.get("9288341808:AAGxhUEAmSvGyJcUi6pwtCcOqCA1ZgAIzT0")
ADMIN_ID = 621360017
bot = telebot.TeleBot(TOKEN)

FILE = "video.txt"
POINTS_FILE = "points.txt"
WATCHED_FILE = "watched.txt"
OPENED_FILE = "opened.txt"

waiting_for_video = set()

def get_video():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return f.read().strip()
    return "لسا ما نزل فيديو اليوم"

def save_video(link):
    with open(FILE, "w") as f:
        f.write(link)
    for x in [WATCHED_FILE, OPENED_FILE]:
        if os.path.exists(x):
            os.remove(x)

def get_points(user_id):
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r") as f:
            for line in f:
                if line.startswith(str(user_id) + ":"):
                    return int(line.split(":")[1])
    return 0

def add_points(user_id, amount):
    points = {}
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    uid, p = line.strip().split(":")
                    points[uid] = int(p)
    points[str(user_id)] = points.get(str(user_id), 0) + amount
    with open(POINTS_FILE, "w") as f:
        for uid, p in points.items():
            f.write(f"{uid}:{p}\n")

def has_in(file, user_id):
    if os.path.exists(file):
        with open(file, "r") as f:
            return str(user_id) in f.read().split()
    return False

def add_to(file, user_id):
    with open(file, "a") as f:
        f.write(f"{user_id} ")

def main_menu(user_id=None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("فيديو اليوم 🎬"), KeyboardButton("رصيدي 💰"))
    markup.add(KeyboardButton("ما هي عملة بون؟ 💎"))
    if user_id == ADMIN_ID:
        markup.add(KeyboardButton("➕ إضافة فيديو اليوم"))
    return markup

def back_menu(user_id=None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("رجوع 🔙"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "اهلا بك في بون ☕️\n\nشاهد، اجمع، واكسب 💰", reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_video)
def receive_new_video(message):
    link = message.text.strip()
    save_video(link)
    waiting_for_video.remove(message.from_user.id)
    bot.send_message(message.chat.id, f"تم ✅ تغير فيديو اليوم بنجاح\n{link}", reply_markup=main_menu(message.from_user.id))

@bot.message_handler(commands=['setvideo'])
def set_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        link = message.text.split(" ", 1)[1]
        save_video(link)
        bot.reply_to(message, "تم ✅ تغير فيديو اليوم بنجاح")
    except:
        bot.reply_to(message, "ارسل كذا: /setvideo + رابط الفيديو")

@bot.message_handler(func=lambda m: m.text == "فيديو اليوم 🎬")
def video_today(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("شاهد الفيديو على يوتيوب ▶️", url=get_video() if get_video().startswith("http") else "https://youtube.com"))
    bot.send_message(message.chat.id, "فيديو اليوم 🎬\n\nاضغط الزر وشاهد الفيديو كامل، بعدها بيطلع لك زر شاهدت", reply_markup=markup)
    # نرسل زر شاهدت كزر ثابت
    m2 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m2.add(KeyboardButton("شاهدت الفيديو ✅"), KeyboardButton("رجوع 🔙"))
    bot.send_message(message.chat.id, "بعد ما تخلص المشاهدة، اضغط شاهدت الفيديو 👇", reply_markup=m2)

@bot.message_handler(func=lambda m: m.text == "شاهدت الفيديو ✅")
def watched_btn(message):
    user_id = message.from_user.id
    if has_in(WATCHED_FILE, user_id):
        bot.send_message(message.chat.id, "خلاص قد اخذت نقاط اليوم ✅", reply_markup=main_menu(user_id))
    else:
        add_points(user_id, 100)
        add_to(WATCHED_FILE, user_id)
        bot.send_message(message.chat.id, "حصلت على 100 نقطة 🎉", reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda m: m.text == "رصيدي 💰")
def balance_btn(message):
    p = get_points(message.from_user.id)
    bot.send_message(message.chat.id, f"رصيدك 💰\n\n{p} نقطة من عملة بون 💎", reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "ما هي عملة بون؟ 💎")
def about_btn(message):
    text = """ما هي عملة بون؟ 💎☕️

بون BUN هي عملة رقمية مجتمعية، تابعة لشركة بون.

بدل ما تشاهد المحتوى بدون مقابل، أنت تكافأ على وقتك وتفاعلك داخل المنظومة.

💰 كيف تحصل على عملة بون؟
كل يوم تشاهد فيديو اليوم بشكل كامل، وتحصل على 100 بون.

🌍 ما هو مستقبل بون؟
تعمل شركة بون حالياً على تطوير منظومة متكاملة للعملة، تشمل المحفظة، والمتجر، وخدمات داخل المجتمع.

بون ليست مشروعاً مؤقتاً، بون منظومة تُبنى خطوة بخطوة، بثبات واحترافية.

أهلاً بك في بون. 🚀"""
    bot.send_message(message.chat.id, text, reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "رجوع 🔙")
def back_btn(message):
    bot.send_message(message.chat.id, "اهلا بك في بون ☕️", reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "➕ إضافة فيديو اليوم")
def admin_add(message):
    if message.from_user.id != ADMIN_ID:
        return
    waiting_for_video.add(message.from_user.id)
    bot.send_message(message.chat.id, "ارسل الآن رابط فيديو اليوم 👇", reply_markup=back_menu())

print("البوت شغال...")
bot.polling()

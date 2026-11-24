from flask import Flask
import threading
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = "9288341808:AAGxhUEAmSvGyJcUi6pwtCcOqCA1ZgAIzT0"
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
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("فيديو اليوم 🎬", callback_data="video"))
    markup.add(InlineKeyboardButton("رصيدي 💰", callback_data="balance"))
    markup.add(InlineKeyboardButton("ما هي عملة بون؟ 💎", callback_data="about"))
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("➕ إضافة فيديو اليوم", callback_data="admin_add_video"))
    return markup

def back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("رجوع 🔙", callback_data="back"))
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

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.data == "video":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("شاهد الفيديو على يوتيوب ▶️", callback_data="open_video"))
        markup.add(InlineKeyboardButton("رجوع 🔙", callback_data="back"))
        bot.send_message(call.message.chat.id, "فيديو اليوم 🎬\n\nاضغط الزر وشاهد الفيديو كامل، بعدها بيطلع لك زر شاهدت", reply_markup=markup)

    elif call.data == "open_video":
        add_to(OPENED_FILE, call.from_user.id)
        video = get_video()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("شاهدت الفيديو ✅", callback_data="watched"))
        markup.add(InlineKeyboardButton("رجوع 🔙", callback_data="back"))
        bot.send_message(call.message.chat.id, f"هذا هو الفيديو 👇\n{video}\n\nشاهده للآخر، بعد ما تخلص ارجع هنا واضغط شاهدت الفيديو", reply_markup=markup)

    elif call.data == "watched":
        if has_in(WATCHED_FILE, call.from_user.id):
            bot.send_message(call.message.chat.id, "خلاص قد اخذت نقاط اليوم ✅", reply_markup=back_button())
        elif not has_in(OPENED_FILE, call.from_user.id):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("شاهد الفيديو على يوتيوب ▶️", callback_data="open_video"))
            bot.send_message(call.message.chat.id, "اولاً لازم تضغط شاهد على يوتيوب وتدخل الفيديو ⚠️", reply_markup=markup)
        else:
            add_points(call.from_user.id, 100)
            add_to(WATCHED_FILE, call.from_user.id)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("رصيدي 💰", callback_data="balance"))
            markup.add(InlineKeyboardButton("رجوع 🔙", callback_data="back"))
            bot.send_message(call.message.chat.id, "حصلت على 100 نقطة 🎉", reply_markup=markup)

    elif call.data == "balance":
        p = get_points(call.from_user.id)
        bot.send_message(call.message.chat.id, f"رصيدك 💰\n\n{p} نقطة من عملة بون 💎", reply_markup=back_button())

    elif call.data == "about":
        text = """ما هي عملة بون؟ 💎☕️

بون BUN هي عملة رقمية مجتمعية، تابعة لشركة بون.

عملة تم إطلاقها بهدف بناء مجتمع رقمي حقيقي، يكون فيه المستخدم شريكاً في النمو، وليس مجرد متابع.

فكرة بون بسيطة وقوية في نفس الوقت:
بدل ما تشاهد المحتوى بدون مقابل، أنت تكافأ على وقتك وتفاعلك داخل المنظومة.

💰 كيف تحصل على عملة بون؟
كل يوم تشاهد فيديو اليوم بشكل كامل، وتحصل على 100 بون.
رصيدك يتراكم يوماً بعد يوم داخل حسابك، وكل نقطة مسجلة باسمك وبشكل شفاف.

🌍 ما هو مستقبل بون؟
تعمل شركة بون حالياً على تطوير منظومة متكاملة للعملة، تشمل المحفظة، والمتجر، وخدمات داخل المجتمع.

وإن شاء الله، في المرحلة القادمة، سيتم إدراج عملة بون في المنصات العالمية، لتصبح عملة قابلة للتداول، وليست مجرد نقاط داخل بوت.

بون ليست مشروعاً مؤقتاً، بون منظومة تُبنى خطوة بخطوة، بثبات واحترافية.

أهلاً بك في بون.
أهلاً بك في مستقبل العملات المجتمعية. 🚀"""
        bot.send_message(call.message.chat.id, text, reply_markup=back_button())

    elif call.data == "back":
        bot.send_message(call.message.chat.id, "اهلا بك في بون ☕️", reply_markup=main_menu(call.from_user.id))

    elif call.data == "admin_add_video":
        if call.from_user.id != ADMIN_ID:
            return
        waiting_for_video.add(call.from_user.id)
        bot.send_message(call.message.chat.id, "ارسل الآن رابط فيديو اليوم 👇")

print("البوت شغال...")
bot.polling()

import json
import requests
import telebot
import time
from decouple import config


bot = telebot.TeleBot(config("TOKEN"))
BASE_URL = config("BASE_URL")


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
    button = telebot.types.KeyboardButton('/register')
    button2 = telebot.types.KeyboardButton('/login')
    button3 = telebot.types.KeyboardButton('/activate')
    markup.add(button, button2, button3)
    text = '*✨Добро пожаловать в TikTak\n\n👤Если у вас уже есть аккаунт то бот ни чем вам не поможет, можете перейти на сайт: \nhttp://127.0.0.1:8000\n\n🔐Если же у вас еще нет аккаунта, вы можете его создать введя команду /register*'
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['register'])
def register(message: telebot.types.Message):
    resp = bot.send_message(message.chat.id, "📝Для начала регистрации ведите email")
    bot.register_next_step_handler(resp, register_step_2, {})

def register_step_2(message: telebot.types.Message, other_data: dict):
    other_data["email"] = message.text
    resp = bot.send_message(message.chat.id, "🔑Придумайте password")
    bot.register_next_step_handler(resp, register_step_3, other_data)

def register_step_3(message: telebot.types.Message, other_data: dict):
    other_data["password"] = message.text
    other_data["password_confirm"] = message.text
    resp = bot.send_message(message.chat.id, "👤Придумайте username")
    bot.register_next_step_handler(resp, finish_register, other_data)

def finish_register(message: telebot.types.Message, other_data: dict):
    other_data["name"] = message.text
    resp = requests.post(BASE_URL + "/account/register/", other_data)
    if resp.status_code == 400:
        text = ""
        for k, v in resp.json().items():
            text += f"[{k}] {' '.join(v)}\n"
        bot.send_message(message.chat.id, text)
        bot.send_message(message.chat.id, "❌Пройдите регистрацию заново /register")
    else:
        bot.send_message(message.chat.id, "✅Вы успешно зарегались, вам на почту был отправлен код активации.\n\nДля его использования введите команду /activate")

@bot.message_handler(commands=['activate'])
def activate(message: telebot.types.Message):
    bot.send_message(message.chat.id, "🪪Введите email и код через пробел")
    bot.register_next_step_handler(message, send_activation_code)

def send_activation_code(message: telebot.types.Message):
    try:
        email, code = message.text.strip().split()
    except ValueError:
        bot.send_message(message.chat.id, "🪪Введите через один пробел email, затем код подтверждения")
        return activate(message)
    resp = requests.post(BASE_URL + "/account/activate/", {"email": email, "code": code})
    if resp.status_code == 201:
        bot.send_message(message.chat.id, "✅Вы успешно активировали аккаунт, остался последний шаг.\n\nВведите команду /login чтобы залогиниться")
    else:
        bot.send_message(message.chat.id, "❌Email или код не верные")


@bot.message_handler(commands=['login'])
def login(message: telebot.types.Message):
    bot.send_message(message.chat.id, "🪪Введите email и password через пробел")
    bot.register_next_step_handler(message, finish_login)

def finish_login(message: telebot.types.Message):
    try:
        email, password = message.text.strip().split()
    except ValueError:
        bot.send_message(message.chat.id, "🪪Введите через один пробел email, затем password")
        return login(message)
    resp = requests.post(BASE_URL + "/account/login/", {"email": email, "password": password})
    if resp.status_code == 200:
        bot.send_message(message.chat.id, "✅Вы успешно залогинелись, перейти на сайт:")
        bot.send_message(message.chat.id, "http://127.0.0.1:8000")
    else:
        bot.send_message(message.chat.id, "❌Не верные данные")


@bot.message_handler(commands=[config("ADMIN_KEY")])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    button_a = telebot.types.KeyboardButton(config("BUTTON_A/"))
    button_d = telebot.types.KeyboardButton(config("BUTTON_D/"))
    button_e = telebot.types.KeyboardButton(config("BUTTON_E/"))
    markup.add(button_a, button_d, button_e)
    text = '*👤Добро пожаловать в админ панель TikTak🔓*'
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)
    time.sleep(1)
    bot.send_message(message.chat.id, "❗❗❗Внимание❗❗❗\n\nАдминская панель напримую связана с сайтом!\nБудьте вниметельны при её использовании!\nТак как действия производимые в ней на прямую влияют на сайт TikTak.")


@bot.message_handler(commands=[config("BUTTON_E")])
def start(message):
    bot.send_message(message.chat.id, "🔒Панель закрыта")
    time.sleep(2)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
    button = telebot.types.KeyboardButton('/register')
    button2 = telebot.types.KeyboardButton('/login')
    button3 = telebot.types.KeyboardButton('/activate')
    markup.add(button, button2, button3)
    text = '*✨Добро пожаловать в TikTak\n\n👤Если у вас уже есть аккаунт то бот ни чем вам не поможет, можете перейти на сайт: \nhttp://127.0.0.1:8000\n\n🔐Если же у вас еще нет аккаунта, вы можете его создать введя команду /register*'
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)


bot.polling()


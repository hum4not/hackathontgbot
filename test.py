import telebot
import telebot.types
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import os
import json
import subprocess
from telegram import Sticker, StickerSet, Bot, InputFile

bot = telebot.TeleBot('6477693722:AAFSgjOhL9hLKxU6BCFG9fAiwCgLJ0nW3Ds')

active = {} #ожидание загрузки темпейлта
sending_face = {} #ожидание загрузки лица для создания пака 
database = {}
try:
  with open('users.json') as f:
    database = json.load(f)
except FileNotFoundError:
  print("Could not load users.json, database will be not loaded or saved")
  database = {}

@bot.message_handler(commands=['start'])
def start_message(message: Message):
    bot.reply_to(message, "Привет! вот список команд:\n/create_template (name) - создание шаблона(можно загрузить несколько фотографий)\n/choose_template - позволяет выбрать нужный шаблон\n/gen - создание стикерпака")

@bot.message_handler(commands=['choose_template'])
def choose_template(message: Message):
    markup = ReplyKeyboardMarkup()
    templates = os.listdir(str(message.from_user.id))
    markup.one_time_keyboard = True
    for i in templates:
            markup.add(KeyboardButton(i))

    bot.send_message(message.chat.id, "Выберите шаблон:", reply_markup=markup)

@bot.message_handler(commands=['gen'])
def generate_stickers(message: Message):
    bot.reply_to(message, f"Отлично, теперь отправьте фотографию c лицом, которое будет применено для создания стикерпака используя шаблон: {database[str(message.from_user.id)]}")
    sending_face[message.from_user.id] = True

@bot.message_handler(commands=['subscribe'])
def subscribe_channel(message: Message):
    bot.reply_to(message, "Вы подписались на наш канал!")

@bot.message_handler(commands=['support'])
def support_chat(message: Message):
    bot.reply_to(message, "Для поддержки и обратной связи напишите сообщение администратору.")

# Функция для обработки команды /create_template
@bot.message_handler(commands=['create_template'])
def create_template(message: Message):
    print(f"DEBUG: {message.text}")
    try:
        name = message.text.split()[1]
        active[message.from_user.id] = f"{message.from_user.id}\\{name}"
        direc = f"{message.from_user.id}\\{name}"
        os.makedirs(direc)
        print(f"created {direc}")
        bot.reply_to(message, f"Шаблон будет сохранен под именем '{name}'. Пожалуйста, отправьте изображения.")
    except:
        bot.reply_to(message, f"В аргументе команды укажите имя шаблона.")

import random
@bot.message_handler(content_types=['text'])
def funcc(message):
    templates = os.listdir(str(message.from_user.id))
    if message.text in templates :
        database[str(message.from_user.id)] = message.text
        bot.reply_to(message, f"Выбран шаблон {message.text}")
        _save()
@bot.message_handler(content_types=['photo'])
def handle_images(message):
    if message.from_user.id in active:
        direc = active[message.from_user.id]

        photo = message.photo[-1]

        file_info = bot.get_file(photo.file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        file_extension = '.' + file_info.file_path.split('.')[-1]

        rand = random.randint(1,100)
        file_name = f"pic-{rand}{file_extension}"

        file_path = os.path.join(direc, file_name)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            print(f"saved file: {file_path}")

    if message.chat.id in sending_face and sending_face[message.chat.id]:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(f"{message.from_user.id}\\face.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        
        bot.reply_to(message, "Спасибо. Фотография успешно сохранена, приступаем к обработке!")
        sending_face[message.chat.id] = False

        arguments = [f"{message.from_user.id}", f"{database[str(message.from_user.id)]}", f"{message.from_user.id}\\face.jpg"]
        process = subprocess.Popen(["FaceReplace.exe"] + arguments)
        process.wait()

        jpg_files = [f for f in os.listdir(f"{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack") if os.path.isfile(os.path.join(f"{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack", f)) and f.endswith('.jpg')]

        for file_name in jpg_files:
            print("ASD " + file_name)
            bot.send_chat_action(message.chat.id, 'upload_photo')
            img = open(f"{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack\\" + file_name, 'rb')
            bot.send_photo(message.chat.id, img)
            img.close()


#        stickers = []
#        for file_name in jpg_files:
#            sticker = Sticker(file_id=file_name, file_unique_id=file_name, width=512, height=512, is_animated=False, is_video=False, emojis='😊')
#            stickers.append(sticker)

        #sticker_set = StickerSet(database[str(message.from_user.id)], title=database[str(message.from_user.id)], stickers=stickers, is_animated=False, is_video=False, contains_masks=False)

       # bot.reply_to(message, sticker_set)

        #bot.create_new_sticker_set(user_id=str(message.from_user.id), name=database[str(message.from_user.id)], title=database[str(message.from_user.id)], png_sticker=f"{message.from_user.id}\\face.jpg", emojis="😊", contains_masks=True, mask_position=None)

def _save():
    with open('users.json', 'w+') as f:
        json.dump(database, f)

# Запуск бота
bot.polling(skip_pending=True)
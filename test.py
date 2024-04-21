import telebot
from telebot import types
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import os
import json
import subprocess
from PIL import Image

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

    markup_inline = types.InlineKeyboardMarkup()
    item_1 = types.InlineKeyboardButton(text='Создать шаблон', callback_data='create_template')
    item_2 = types.InlineKeyboardButton(text='Выбрать шаблон', callback_data='choose_template')
    item_3 = types.InlineKeyboardButton(text='Сгенерировать стикерпак', callback_data='generate_template')
    markup_inline.add(item_1, item_2, item_3)
    bot.reply_to(message, "Привет! вот список команд:\n/create_template (name) - создание шаблона(можно загрузить несколько фотографий)\n/choose_template - позволяет выбрать нужный шаблон\n/gen - создание стикерпака", reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if (call.data) == 'create_template':
        bot.send_message(call.message.chat.id, "Что бы создать шаблон используйте команду: /create_template (имя шаблона)")
    if call.data == 'choose_template':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        templates = os.listdir("templates\\" + str(call.message.chat.id))
        markup.one_time_keyboard = True
        if templates.count == 0:
            for i in templates:
                    if(not "." in i):
                        markup.add(KeyboardButton(i))

            bot.send_message(call.message.chat.id, "Выберите шаблон:", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Для начала нужно создать хотя бы один шаблон")
    if call.data == 'generate_template':
        try:
            bot.reply_to(call.message, f"Отлично, теперь отправьте фотографию c лицом, которое будет применено для создания стикерпака используя шаблон: {database[str(call.message.chat.id)]}")
            sending_face[call.message.chat.id] = True
        except:
            bot.reply_to(call.message, "Для начала нужно выбрать/создать хотя бы один шаблон.")
@bot.message_handler(commands=['choose_template'])
def choose_template(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    templates = os.listdir("templates\\" + str(message.chat.id))
    markup.one_time_keyboard = True
    for i in templates:
            if(not "." in i):
                markup.add(KeyboardButton(i))

    bot.send_message(message.chat.id, "Выберите шаблон:", reply_markup=markup)

@bot.message_handler(commands=['gen'])
def generate_stickers(message: Message):
    try:
        bot.reply_to(message, f"Отлично, теперь отправьте фотографию c лицом, которое будет применено для создания стикерпака используя шаблон: {database[str(message.from_user.id)]}")
        sending_face[message.from_user.id] = True
    except:
        bot.reply_to(message, "Для начала нужно создать хотя бы один шаблон (/create_template)")

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
        direc = f"templates\\{message.from_user.id}\\{name}"
        os.makedirs(direc)
        print(f"created {direc}")
        bot.reply_to(message, f"Шаблон будет сохранен под именем '{name}'. Пожалуйста, отправьте изображения.")
    except:
        bot.reply_to(message, f"В аргументе команды укажите имя шаблона.")

import random
@bot.message_handler(content_types=['text'])
def funcc(message):
    templates = os.listdir("templates\\" + str(message.from_user.id))
    if message.text in templates :
        database[str(message.from_user.id)] = message.text
        bot.reply_to(message, f"Выбран шаблон {message.text}")
        _save()

@bot.message_handler(content_types=['photo'])
def handle_images(message):
    if message.from_user.id in active:
        direc = "templates\\" + active[message.from_user.id]

        photo = message.photo[-1]

        file_info = bot.get_file(photo.file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        rand = random.randint(1,100)
        file_name = f"pic-{rand}.png"

        file_path = os.path.join(direc, file_name)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            print(f"saved file: {file_path}")

    if message.chat.id in sending_face and sending_face[message.chat.id]:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(f"templates\\{message.from_user.id}\\face.png", 'wb') as new_file:
            new_file.write(downloaded_file)
        
        bot.reply_to(message, "Спасибо. Фотография успешно сохранена, приступаем к обработке!")
        sending_face[message.chat.id] = False

        arguments = [f"templates\\{message.from_user.id}", f"{database[str(message.from_user.id)]}", f"templates\\{message.from_user.id}\\face.png"]
        process = subprocess.Popen(["FaceReplace.exe"] + arguments)
        process.wait()

        jpg_files = [f for f in os.listdir(f"templates\\{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack") if os.path.isfile(os.path.join(f"templates\\{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack", f)) and f.endswith('.png')]
        
        sticker_pack_name =  str(database[str(message.from_user.id)]).upper() + str(message.from_user.id) + f"_by_FS2024HKTN_bot"

        for file_name in jpg_files:
            img = Image.open(f"templates\\{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack\\" + file_name)
            img_resized = img.resize((512, 512))
            img_resized.save(f"templates\\{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack\\" + file_name)
        try:
            path = f"templates\\{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack\\" + jpg_files[0]
            pack_path = f"templates\\{message.from_user.id}\\{database[str(message.from_user.id)]}\\pack\\"

            stickers = [pack_path + file_id for file_id in jpg_files]

            #sticker_set = StickerSet(sticker_pack_name, title="Sticker Pack Title", stickers=stickers, is_animated=False, contains_masks=False, is_video=False)

            try:
                with open(path, "rb") as cover_image:
                    bot.create_new_sticker_set(user_id=message.from_user.id, name=sticker_pack_name, title=database[str(message.from_user.id)] ,png_sticker=cover_image, emojis=['😊'],contains_masks=False, mask_position=None)
            except telebot.apihelper.ApiException as e:
                # Handle the exception if the sticker set name is already occupied
                if e.result_json["description"] == "Bad Request: sticker set name is already occupied":
                    pass

            for sticker_path in stickers:
                bot.add_sticker_to_set(user_id=message.from_user.id, name=sticker_pack_name,
                                        png_sticker=open(sticker_path, 'rb'), emojis=['😊'])

            bot.send_message(message.from_user.id, f"https://t.me/addstickers/{sticker_pack_name}")
        except Exception as err:
            bot.send_message(message.from_user.id, f"Вознилка ошибка: {err}")


def _save():
    with open('users.json', 'w+') as f:
        json.dump(database, f)

bot.polling(skip_pending=True)

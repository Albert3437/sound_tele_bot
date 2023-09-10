import io
import time
import telebot
import requests

import pandas as pd
from telebot import types

from modules.silero_tts import TextToSpeech
from modules.config import TELE_API


bot = telebot.TeleBot(TELE_API) 



def core(df):
    text = df['Text']
    title = df['Filename']
    voice = df['Voice']
    lang = df['Language']
    
    tts = TextToSpeech(lang, voice)
    audio = tts.core(text)
    audio_bytes = tts.audio_bytes(audio)
    return audio_bytes, title



# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user
    markup = generate_markup()
    bot.send_message(user.id, "Добрый день, господин!", reply_markup=markup)

# Создание клавиатуры с кнопками
def generate_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    button1 = types.KeyboardButton("Шаблон")
    button2 = types.KeyboardButton("Инфо")

    markup.add(button1, button2)

    return markup


# Обработка нажатий на кнопки
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "Шаблон":
        with open('example/example.xlsx', 'rb') as file:
            bot.send_document(message.chat.id, file)
    if message.text == "Инфо":
        msg = 'Добрый день,\n\nОписание ячеек:\nFilename - Имя будущего файла\nText - Текст для озвучки\nVoice - Необходимый голос\nLanguage - Язык озвучки\n\nДоступные языки: ru/en\n\nДоступные русские голоса: aidar, baya, kseniya, xenia, eugene, random\n\nДоступные английские голоса: en_0 - en_117, random'
        bot.send_message(message.chat.id, msg)



@bot.message_handler(content_types=['document'])
def handle_document(message):
    user = message.from_user
    file_info = bot.get_file(message.document.file_id)
    file_path = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

    try:
        with io.BytesIO() as file_stream:
            file_stream.write(requests.get(file_path).content)
            file_stream.seek(0)
            df = pd.read_excel(file_stream, engine='openpyxl')
            bot.send_message(user.id, "Файл успешно прочитан")
            for i in range(len(df)):
                audio_bytes, title = core(df.iloc[i])
                bot.send_audio(user.id, audio_bytes, title=title)
            bot.send_message(user.id, "Успешно выполнено")
    except Exception as e:
        bot.send_message(user.id, f"Произошла ошибка при чтении файла: {str(e)}")



# Запуск бота
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            time.sleep(1)

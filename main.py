import sqlite3

from config import API_TOKEN
from bot.database import DATABASE_NAME
from telegram.ext import Updater, CommandHandler


def start(update, context):
    update.message.reply_text('Привет! Я библиотечный бот и мазафакер. Введите /help для списка команд.')

def help(update, context):
    update.message.reply_text('/borrow - взять книгу\n/return - вернуть книгу\n/queue - занять очередь на книгу\n/addbook - добавить книгу\n/workinghours - узнать рабочие часы офлайн библиотки')

def working_hours(update, context):
    update.message.reply_text('Библиотека работает для поситителей с 15:00 до 15:30 ежедневно.')

def add_book(update, context):
    user_input = update.message.text.split(', ')
    # Проверка количества введенных аргументов
    if len(user_input) < 3:
        update.message.reply_text('Ошибка ввода. Используйте формат: /addbook название, автор')
        return

    title, author = user_input[1], user_input[2]
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            conn.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
            conn.commit()  # Важно сохранить изменения в БД
            update.message.reply_text(f'Книга "{title}" добавлена в каталог.')
    except sqlite3.Error as e:
        update.message.reply_text(f'Ошибка при добавлении книги: {e}')

# В main.py




updater = Updater(API_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("workinghours", working_hours))
dp.add_handler(CommandHandler("addbook", add_book))


updater.start_polling()
updater.idle()

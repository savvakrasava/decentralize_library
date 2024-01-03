import sqlite3

from config import API_TOKEN, YOUR_GROUP_CHAT_ID
from bot.database import DATABASE_NAME
from telegram.ext import Updater, CommandHandler,  MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from bot.database import SessionLocal, engine, init_db
from bot.models import Base

from bot.models.users import User
from bot.models.books import Book

from sqlalchemy.orm import sessionmaker


AUTHOR, TITLE, DESCRIPTION, CONFIRMATION = range(4)
BORROW = 1


init_db()


def start(update, context):
    update.message.reply_text('Привет! Я библиотечный бот и мазафакер. Введите /help для списка команд.')

def help(update, context):
    update.message.reply_text('/borrow - взять книгу\n/return - вернуть книгу\n/queue - занять очередь на книгу\n/addbook - добавить книгу\n/workinghours - узнать рабочие часы офлайн библиотки\n/showcatalog - показать книжный каталог')

def working_hours(update, context):
    update.message.reply_text('Библиотека работает для поситителей с 15:00 до 15:30 ежедневно.')

def add_book(update, context):
    if update.message is None:
        print("Ошибка: update.message is None")
        return
    update.message.reply_text('Введите автора книги:')
    return AUTHOR

def author(update, context):
    print("Функция author вызвана.")
    context.user_data['author'] = update.message.text
    update.message.reply_text('Введите название книги:')
    return TITLE

def title(update, context):
    print("Функция title вызвана.")
    context.user_data['title'] = update.message.text
    update.message.reply_text('Введите описание книги (или нажмите /skip, чтобы пропустить):')
    return DESCRIPTION

def skip_description(update, context):
    print("Функция skip_description вызвана.")
    context.user_data['description'] = None
    return confirmation(update, context)

def description(update, context):
    print("Функция description вызвана.")    
    context.user_data['description'] = update.message.text
    return confirmation(update, context)

def confirmation(update, context):
    user_data = context.user_data
    update.message.reply_text(f"Автор: {user_data['author']}\n"
                              f"Название: {user_data['title']}\n"
                              f"Описание: {user_data.get('description', 'Не указано')}\n"
                              f"Добавить книгу в каталог? (да/нет)")
    return CONFIRMATION

def save_book(update, context):
    user_data = context.user_data
    user_key = update.message.from_user.id  # Telegram ID пользователя
    username = update.message.from_user.username  # Имя пользователя в Telegram

    if update.message.text.lower() == 'да':
        db = SessionLocal()
        try:
            # Проверяем, есть ли пользователь в базе данных
            user = db.query(User).filter(User.user_key == user_key).first()
            if not user:
                # Если пользователя нет, создаём нового
                user = User(user_key=user_key, username=username)
                db.add(user)
                db.commit()

            # Создание новой книги с текущим пользователем в качестве владельца
            new_book = Book(
                title=user_data['title'],
                author=user_data['author'],
                user_key=user.user_key , # ID пользователя из базы данных
                #location = 'DANANG' 
            )
            db.add(new_book)
            db.commit()
            update.message.reply_text('Книга добавлена в каталог.')
        except Exception as e:
            db.rollback()
            update.message.reply_text(f'Ошибка при добавлении книги: {e}')
        finally:
            db.close()
    else:
        update.message.reply_text('Добавление книги отменено.')
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text('Добавление книги отменено.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END



def show_catalog(update, context):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, user_key, book_key FROM books")
        books = cursor.fetchall()

        if not books:
            update.message.reply_text("Каталог книг пуст.")
            return

        catalog_message = ""
        for title, author, user_key, book_key in books:
            if user_key:
                cursor.execute("SELECT username FROM users WHERE user_key = ?", (user_key,))
                owner_result = cursor.fetchone()
                owner_name =  "@" + owner_result[0] if owner_result else "Неизвестен"
            else:
                owner_name = "@" + owner_result[0] if owner_result else "Неизвестен"
            catalog_message += f"Название: {title}, Автор: {author}, Владелец: {owner_name}, ID: {book_key}\n"

        update.message.reply_text(catalog_message)

def borrow_book(update, context):
    print("Функция borrow_book вызвана.")      
    update.message.reply_text("Введите ID книги, которую хотите взять:")
    return BORROW

def confirm_borrow(update, context):
    print("Функция confirm_borrow вызвана.")     
    book_id = update.message.text
    db = SessionLocal()
    book = db.query(Book).filter(Book.book_key == book_id, Book.is_available == True).first()
    if book:
        book.is_available = False
        db.commit()
        owner = db.query(User).filter(User.user_key == book.user_key).first()
        group_chat_id = YOUR_GROUP_CHAT_ID  # ID группового чата
        update.message.reply_text(f"Вы выбрали книгу '{book.title}' автора {book.author}.")
        context.bot.send_message(chat_id=group_chat_id, text=f"Пользователь @{update.message.from_user.username} хочет взять книгу '{book.title}' автора {book.author}, принадлежащую @{owner.username}.")
    else:
        update.message.reply_text("Книга недоступна или не существует.")
    db.close()
    return ConversationHandler.END
conv_handler_addbook = ConversationHandler(
    entry_points=[CommandHandler('addbook', add_book)],
    states={
        AUTHOR: [MessageHandler(Filters.text & ~Filters.command, author)],
        TITLE: [MessageHandler(Filters.text & ~Filters.command, title)],
        DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description),
                      CommandHandler('skip', skip_description)],
        CONFIRMATION: [MessageHandler(Filters.regex('^(да|нет)$'), save_book)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)




conv_handler_borrow = ConversationHandler(
    entry_points=[CommandHandler('borrow', borrow_book)],
    states={
        BORROW: [MessageHandler(Filters.text & ~Filters.command, confirm_borrow)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

conv_handler_addbook = ConversationHandler(
    entry_points=[CommandHandler('addbook', add_book)],
    states={
        AUTHOR: [MessageHandler(Filters.text & ~Filters.command, author)],
        TITLE: [MessageHandler(Filters.text & ~Filters.command, title)],
        DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description),
                      CommandHandler('skip', skip_description)],
        CONFIRMATION: [MessageHandler(Filters.regex('^(да|нет)$'), save_book)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


updater = Updater(API_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("workinghours", working_hours))
dp.add_handler(conv_handler_borrow)
dp.add_handler(conv_handler_addbook)
dp.add_handler(CommandHandler("showcatalog", show_catalog))

updater.start_polling()
updater.idle()

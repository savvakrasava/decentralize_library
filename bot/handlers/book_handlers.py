import sqlite3
from datetime import datetime, timedelta
from config import API_TOKEN, YOUR_GROUP_CHAT_ID
from bot.database import DATABASE_NAME
from telegram.ext import Updater, CommandHandler,  MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from bot.database import SessionLocal, engine, init_db
from bot.models import Base
from bot.models.users import User
from bot.models.bookings import Bookings
from bot.models.books import Book
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from telegram.ext import Updater, CommandHandler, ConversationHandler
from bot.utils.helpers import cancel



AUTHOR, TITLE, DESCRIPTION, CONFIRMATION = range(4)
READ_DESCRIPTION = range(5)

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
                description=user_data['description'],
                user_key=user.user_key ,
                is_available=True,
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




def read_description(update, context):
    update.message.reply_text("Введите ID книги для просмотра описания:")
    return READ_DESCRIPTION

def provide_description(update, context):
    book_id = update.message.text
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.book_key == book_id).first()
        if book:
            update.message.reply_text(f"Название: {book.title}\nАвтор: {book.author}\nОписание: {book.description or 'Описание отсутствует.'}")
        else:
            update.message.reply_text("Книга с таким ID не найдена.")
    except Exception as e:
        update.message.reply_text(f"Произошла ошибка: {e}")
    finally:
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

conv_handler_description = ConversationHandler(
    entry_points=[CommandHandler('read_description', read_description)],
    states={READ_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, provide_description)]},
    fallbacks=[CommandHandler('cancel', cancel)]
)

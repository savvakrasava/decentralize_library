
# bot/utils.py
from telegram import ReplyKeyboardRemove
from sqlalchemy.orm import sessionmaker
from bot.database import engine
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

def hide_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()



def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()

def get_or_create_user(db, user_id, username):
    user = db.query(User).filter(User.telegram_key == user_id).first()
    if not user:
        user = User(telegram_key=user_id, username=username)
        db.add(user)
        db.commit()
    return user

def get_book_by_id(db, book_id):
    return db.query(Book).filter(Book.book_key == book_id).first()

def create_booking(db, book_id, from_user_id, to_user_id):
    new_booking = Bookings(book_key=book_id, from_user_key=from_user_id, to_user_key=to_user_id, status="draft")
    db.add(new_booking)
    db.commit()

def format_book_info(book):
    return f"Название: {book.title}, Автор: {book.author}, ID: {book.book_key}"

def cancel(update, context):
    update.message.reply_text('Добавление книги отменено.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
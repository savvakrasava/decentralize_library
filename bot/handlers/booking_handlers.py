
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



BORROW, CONFIRM_BORROW = range(2)


def borrow_book(update, context):
    update.message.reply_text("Введите ID книги, которую хотите взять:")
    return BORROW

def confirm_borrow(update, context):
    book_id = update.message.text
    from_user_id = update.message.from_user.id
    db = SessionLocal()

    # Проверка доступности книги
    book = db.query(Book).filter(Book.book_key == book_id, Book.is_available == True).first()
    try:

        if book:
            new_booking = Bookings(
                book_key=book.book_key,
                from_user_key=from_user_id,
                to_user_key=book.user_key,
                status="draft"
            )
            db.add(new_booking)
            db.commit()
            update.message.reply_text(f"Запрос на бронирование книги '{book.title}' отправлен. Свяжитесь с владельцем книги для подтверждения.")
        else:
            update.message.reply_text("Книга недоступна или не существует.")
    except Exception as e:
        db.rollback()
        update.message.reply_text(f"Произошла ошибка: {e}")
    finally:
        db.close()
    return ConversationHandler.END

def start_confirm_borrow(update, context):
    update.message.reply_text("Введите ID книги, которую вы подтверждаете:")
    return CONFIRM_BORROW

def confirm_book(update, context):
    book_id = update.message.text
    db = SessionLocal()

    # Получение информации о бронировании
    booking = db.query(Bookings).filter(Bookings.book_key == book_id, Bookings.status == "draft").first()
    if booking:
        booking.status = "confirmed"
        booking.return_ts = datetime.now() + timedelta(weeks=3)
        booking.last_updated_ts = datetime.now()
        db.commit()
        update.message.reply_text(f"Бронирование книги подтверждено.")
    else:
        update.message.reply_text("Бронирование не найдено или уже подтверждено.")

    db.close()
    return ConversationHandler.END


def show_my_bookings(update, context):
    user_id = update.message.from_user.id
    db = SessionLocal()

    try:
        # Получаем бронирования, где пользователь является инициатором и получателем
        my_bookings = db.query(Bookings, Book, User)\
            .join(Book, Bookings.book_key == Book.book_key)\
            .outerjoin(User, Bookings.to_user_key == User.user_key)\
            .filter((Bookings.from_user_key == user_id) | (Bookings.to_user_key == user_id))\
            .all()

        if my_bookings:
            booking_info = []
            for booking, book, user in my_bookings:
                role = "взял" if booking.from_user_key == user_id else "отдал"
                user_role = "от" if role == "взял" else "к"
                owner_username = user.username if user else "Неизвестен"
                booking_info.append(
                    f"Книга: {book.title}, Автор: {book.author}, "
                    f"Забронирована: {booking.borrow_ts}, "
                    f"Возврат: {'не определен' if not booking.return_ts else booking.return_ts}, "
                    f"{user_role} пользователя: @{owner_username}, "
                    f"Статус: {booking.status}, "
                    f"Роль в бронировании: {role}"
                )

            update.message.reply_text("\n".join(booking_info))
        else:
            update.message.reply_text("У вас нет активных бронирований.")

    except Exception as e:
        update.message.reply_text(f"Ошибка при получении данных о бронированиях: {e}")
    finally:
        db.close()





conv_handler_borrow = ConversationHandler(
    entry_points=[CommandHandler('borrow', borrow_book)],
    states={BORROW: [MessageHandler(Filters.text & ~Filters.command, confirm_borrow)]},
    fallbacks=[CommandHandler('cancel', cancel)]
)

confirm_borrow_handler = ConversationHandler(
    entry_points=[CommandHandler('confirm_borrow', start_confirm_borrow)],
    states={CONFIRM_BORROW: [MessageHandler(Filters.text & ~Filters.command, confirm_book)]},
    fallbacks=[CommandHandler('cancel', cancel)]
)

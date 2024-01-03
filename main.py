from telegram.ext import Updater, CommandHandler, ConversationHandler
from config import API_TOKEN
from bot.database import init_db
from bot.handlers.book_handlers import add_book, show_catalog, read_description, conv_handler_addbook, conv_handler_description
from bot.handlers.user_handlers import start, help, working_hours
from bot.handlers.booking_handlers import borrow_book, confirm_borrow, show_my_bookings, start_confirm_borrow,conv_handler_borrow,confirm_borrow_handler




def main():
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Добавление обработчиков
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("workinghours", working_hours))
    # Добавление ConversationHandler'ов
    dp.add_handler(conv_handler_addbook)
    dp.add_handler(conv_handler_borrow)
    dp.add_handler(confirm_borrow_handler)
    dp.add_handler(conv_handler_description)
    dp.add_handler(CommandHandler("showcatalog", show_catalog))
    dp.add_handler(CommandHandler("showmybookings", show_my_bookings))

    # Инициализация базы данных
    init_db()

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
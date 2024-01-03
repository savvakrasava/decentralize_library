from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Импорт Base из моделей
from bot.models import Base

# Путь к файлу базы данных SQLite
DATABASE_URL = "sqlite:///library.db"
DATABASE_NAME = 'library.db'

# Создание движка базы данных
engine = create_engine(DATABASE_URL, echo=True)

# Фабрика сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Импорт моделей
    from bot.models.users import User
    from bot.models.books import Book
    from bot.models.bookings import Bookings

    # Создание таблиц в базе данных
    Base.metadata.create_all(bind=engine)

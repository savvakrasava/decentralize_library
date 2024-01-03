from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.models import Base  #User, Book  # Убедитесь, что этот импорт соответствует расположению вашего файла models.py

DATABASE_URL = "sqlite:///library.db"  # Используйте путь к вашей базе данных
DATABASE_NAME = 'library.db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)


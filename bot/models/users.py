from sqlalchemy import create_engine, Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from . import Base

#Base = declarative_base()



class User(Base):
    __tablename__ = 'users'

    user_key = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    created_ts = Column(TIMESTAMP, nullable=False, default=func.now())
    last_updated_ts = Column(TIMESTAMP, nullable=False, default=func.now())
    telegram_key = Column(Integer, unique=True)  
    location_lat = Column(Float)  
    location_lon = Column(Float)  # Новый столбец для долготы
    city =  Column(String, nullable=True)


# Подключение к базе данных (для создания таблиц)
#engine = create_engine('sqlite:///library.db')
#Base.metadata.create_all(engine)

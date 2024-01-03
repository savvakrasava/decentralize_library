from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

#Base = declarative_base()

from . import Base

class Book(Base):
    __tablename__ = 'books'

    book_key = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_key = Column(Integer,  ForeignKey('users.user_key'), nullable=True)
    created_ts = Column(TIMESTAMP, nullable=False, default=func.now())
    last_updated_ts = Column(TIMESTAMP, nullable=False, default=func.now())
    is_available = Column(Boolean, default=True)


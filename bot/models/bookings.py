from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
####from sqlalchemy.ext.declarative import declarative_base

from . import Base
##Base = declarative_base()

class Bookings(Base):
    __tablename__ = 'bookings'

    booking_key = Column(Integer, primary_key=True)
    book_key = Column(Integer, ForeignKey('books.book_key'))
    from_user_key = Column(Integer, ForeignKey('users.user_key'))
    to_user_key = Column(Integer, ForeignKey('users.user_key'))
    borrow_ts = Column(DateTime, default=func.now())
    return_ts = Column(DateTime)
    status = Column(String, default="draft")
    created_ts = Column(TIMESTAMP, nullable=False, default=func.now())
    last_updated_ts = Column(TIMESTAMP, nullable=False, default=func.now())
    

    book = relationship("Book")
    borrower = relationship("User")

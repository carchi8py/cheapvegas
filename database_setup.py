
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Hotel(Base):
    """
    Hotel store all the information on Vegas Hotels
    """
    __tablename__ = 'hotel'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class Price(Base):
    """
    Price store the price for each day of a hotel
    """
    __tablename__ = 'price'
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotel.id'))
    hotel = relationship(Hotel)
    date = Column(Date, nullable=False)
    price = Column(Integer)


engine = create_engine('sqlite:///db.db')
Base.metadata.create_all(engine)
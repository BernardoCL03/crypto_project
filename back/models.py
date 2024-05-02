
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Migrant(Base):
    __tablename__ = 'migrants'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    country = Column(String)
    arrival_date = Column(Date)
    status = Column(String)
    gender = Column(String)
    phone = Column(String)


from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQL engine, SQLite is used here for simplicity
DATABASE_URL = "sqlite:///./migrants.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a Base class
Base = declarative_base()

# Define a Migrant table
class Migrant(Base):
    __tablename__ = 'migrants'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    age = Column(Integer)
    country = Column(String)
    arrival_date = Column(Date)
    status = Column(String)
    gender = Column(String)
    phone = Column(String)

# Create the table in the database
Base.metadata.create_all(engine)

# Create a Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

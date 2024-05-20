
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

# Define the SQL engine, SQLite is used here for simplicity
DATABASE_URL = "sqlite:///./migrants.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a Base class
Base = declarative_base()

# Base de datos de información general del migrante
class Migrant(Base):
    __tablename__ = 'migrants'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    age = Column(Integer)
    country = Column(String)
    arrival_date = Column(Date)
    status = Column(String)
    gender = Column(String)
    phone = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    user_type = Column(Enum('User','Admin', name = 'user_types'), default='user', nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

# Crear todas las tablas en la base de datos
Base.metadata.create_all(engine)

# Create a Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

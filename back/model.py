import os
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, Engine, Column, Integer, String, Date, Enum
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import bcrypt

# para loggear
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

# Load the environment variables from the specified path
load_dotenv(dotenv_path=dotenv_path)

# Define the SQL engine, SQLite is used here for simplicity
CONN_STRING = os.getenv('DATABASE_URL')
print(CONN_STRING)

ENGINE_URL = URL.create(
    drivername="mssql+pyodbc",
    query={
        "odbc_connect":CONN_STRING,
    },
)

try:
    engine = create_engine(ENGINE_URL)

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
        username = Column(String(50), unique=True, nullable=False)
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

except SQLAlchemyError as e:
    logger.error("Database error occurred", exc_info=True)

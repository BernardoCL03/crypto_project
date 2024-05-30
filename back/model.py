import os
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import bcrypt # pswd hashing
import pytz # zonas horarias

# para loggear
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

# Load the environment variables from the specified path
load_dotenv(dotenv_path=dotenv_path)

# Define the SQL engine, SQLite is used here for simplicity
CONN_STRING = os.getenv('DATABASE_URL')
#print(CONN_STRING)

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
    # class Migrant(Base):
    #     __tablename__ = 'migrants'
    #     id = Column(Integer, primary_key=True, autoincrement=True)
    #     name = Column(String)
    #     age = Column(Integer)
    #     country = Column(String)
    #     arrival_date = Column(Date)
    #     status = Column(String)
    #     gender = Column(String)
    #     phone = Column(String, nullable=False)

    class General(Base):
        __tablename__ = 'general'
        id = Column(Integer, primary_key=True, autoincrement=True)
        arrival_date = Column(String(1024), nullable=False)
        type = Column(String(1024), nullable=True)
        name = Column(String(1024), nullable=True)
        last_name = Column(String(1024), nullable=True)
        gender = Column(String(1024), nullable=True)
        birth_date = Column(String(1024), nullable=False)
        age = Column(String(1024), nullable=False)
        country_of_origin = Column(String(1024), nullable=True)
        civil_status = Column(String(1024), nullable=True)
        has_children = Column(String(1024), nullable=True)
        children_traveling = Column(String(1024), nullable=False)
        can_return_to_country = Column(String(1024), nullable=True)
        reason_cannot_return = Column(String(1024), nullable=True)
        access_to_casa_monarca = Column(String(1024), nullable=True)
        reason_for_denial = Column(String(1024), nullable=True)
        services_provided = Column(String(1024), nullable=True)
        assigned_dormitory = Column(String(1024), nullable=True)
        distinctive_signs = Column(String(1024), nullable=True)
        emergency_contact = Column(String(1024), nullable=True)
        emergency_contact_location = Column(String(1024), nullable=True)
        final_observations = Column(String(1024), nullable=True)
        front_photo = Column(String, nullable=True)
        right_profile_photo = Column(String, nullable=True)
        left_profile_photo = Column(String, nullable=True)
        current_member = Column(String, nullable=True)
        reason_departure = Column(String, nullable=True)
        date_departure = Column(String, nullable=True)

    class Transit(Base):
        __tablename__ = 'transit'
        id = Column(Integer, ForeignKey('general.id'), primary_key=True)
        date_left_origin = Column(String, nullable=False)
        traveling_alone_accompanied = Column(String, nullable=True)
        who_accompanied = Column(String, nullable=True)
        which_relative = Column(String, nullable=True)
        how_traveled = Column(String, nullable=True)
        reason_for_leaving = Column(String, nullable=True)
        abuse_during_travel = Column(String, nullable=True)
        type_of_abuse = Column(String, nullable=True)
        abuse_in_mexico = Column(String, nullable=True)
        type_of_abuse_mexico = Column(String, nullable=True)
        abuser = Column(String, nullable=True)
        paid_guide = Column(String, nullable=True)
        amount_paid = Column(String, nullable=True)
        date_entered_mexico = Column(String, nullable=False)
        entry_point_mexico = Column(String, nullable=True)
        final_destination = Column(String, nullable=True)
        destination_monterrey = Column(String, nullable=True)
        reason_stay_monterrey = Column(String, nullable=True)
        support_network_monterrey = Column(String, nullable=True)
        time_knowing_support = Column(String, nullable=True)
        tried_enter_us = Column(String, nullable=True)
        support_network_us = Column(String, nullable=True)
        description_support_us = Column(String, nullable=True)
        been_in_migration_station = Column(String, nullable=True)
        suffered_aggression = Column(String, nullable=True)
        migration_station_location = Column(String, nullable=True)
        description_of_facts = Column(String, nullable=True)
        filed_complaint = Column(String, nullable=True)
        reason_no_complaint = Column(String, nullable=True)
        solution_offered = Column(String, nullable=True)
        stayed_in_shelter = Column(String, nullable=True)
        last_shelter = Column(String, nullable=True)

    class Health(Base):
        __tablename__ = 'health'
        id = Column(Integer, ForeignKey('general.id'), primary_key=True)
        has_illness = Column(String, nullable=True)
        illness_details = Column(String, nullable=True)
        on_medical_treatment = Column(String, nullable=True)
        medical_treatment_description = Column(String, nullable=True)
        has_allergy = Column(String, nullable=True)
        allergy_details = Column(String, nullable=True)
        is_pregnant = Column(String, nullable=True)
        months_pregnant = Column(String, nullable=True)
        has_prenatal_care = Column(String, nullable=True)

    class Education(Base):
        __tablename__ = 'education'
        id = Column(Integer, ForeignKey('general.id'), primary_key=True)
        can_read_write = Column(String, nullable=True)
        last_grade_study = Column(String, nullable=True)
        languages_spoken = Column(String, nullable=True)
        other_language = Column(String, nullable=True)

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True, autoincrement=True)
        username = Column(String(50), unique=True, nullable=False)
        password_hash = Column(String, nullable=False)
        user_type = Column(Enum('User', 'Colaborador', 'Admin', name = 'user_types'), default='User', nullable=False)

        def set_password(self, password):
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        def check_password(self, password):
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
        
    class Logs(Base):
        __tablename__ = 'logs'
        id = Column(Integer, primary_key=True, autoincrement=True)
        timestamp = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/Monterrey')), nullable=False)
        action = Column(String(50), nullable=False)
        user_name = Column(String(50), ForeignKey('users.username'), nullable=False)
        user_type = Column(Enum('User', 'Colaborador', 'Admin', name = 'user_types'), default='User', nullable=False)
        description = Column(String(100), nullable=True)

    # Crear todas las tablas en la base de datos
    Base.metadata.create_all(engine)

    # Create a Session class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except SQLAlchemyError as e:
    logger.error("Database error occurred", exc_info=True)

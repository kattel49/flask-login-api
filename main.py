from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv

from flask import Flask
from flask_restful import Api, Resource
import os
import bcrypt
"""
    Load all environment variables
"""
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

"""
    Database Implementation
"""
Base = declarative_base()
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")
# establish a database session with the database engine
session = (sessionmaker())()
session.bind(engine)



"""
    Rest Api Implementation
"""
app = Flask(__name__)
api = Api(app)

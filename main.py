from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv

from flask import Flask, request
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
SALT = os.getenv("SALT").encode("utf8")

"""
    Database Implementation
"""
Base = declarative_base()
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")
# establish a database session with the database engine
Session = sessionmaker(bind=engine)
session = Session()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True)
    password_hash = Column(String(128))

    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.hash_password(password)

    def hash_password(self, password):
        # database will encode the password hash as utf8
        return bcrypt.hashpw(password.encode("utf8"), SALT).decode("utf8")
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf8"), self.password_hash)



"""
    Rest Api Implementation
"""
app = Flask(__name__)
api = Api(app)

class Register(Resource):
    def post(self):
        data = request.json

        if data["username"] is None or data["password"] is None:
            return {"error": "Username/Password Missing"}, 400
        try:
            # check to see if the username already exists
            check_user = session.query(Users).filter(Users.username == data["username"]).first()
            if check_user is not None:
                return {"error": "Username already exists"}, 400

            # create the new user
            new_user = Users(data["username"], data["password"])
            session.add(new_user)
            session.commit()
            id = new_user.id
            username = new_user.username
            session.close()
            return {"data": {"username": username, "id": id}}, 201
        
        except Exception as e:
            return {"error" : {"Internal Error"}}, 500

api.add_resource(Register, "/register")        

if __name__ == "__main__":
    app.run(debug=True)
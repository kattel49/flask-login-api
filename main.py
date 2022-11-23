from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os
import bcrypt

import jwt
import datetime
from functools import wraps
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
SECRET_KEY = os.getenv("SECRET_KEY")

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
        return bcrypt.checkpw(password.encode("utf8"), self.password_hash.encode("utf8"))



"""
    Rest Api Implementation
"""
app = Flask(__name__)
api = Api(app)
# Register users
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
            # store data in temp vars
            id = new_user.id
            username = new_user.username
            # close the database session
            session.close()

            return {"data": {"username": username, "id": id}}, 201
        
        except Exception as e:
            return {"error" : {"Internal Error"}}, 500

# login users
class Login(Resource):
    def post(self):
        data = request.json
        # missing fields
        if data["username"] is None or data["password"] is None:
            return {"error": "Username/Password missing"}, 400

        try:
            # query database for username
            user = session.query(Users).filter(Users.username == data["username"]).first()
            
            if user is None:
                return {"error" : "username does not exist"}, 400

            # check if the password is valid
            if user.check_password(data["password"]):
                id = user.id
                username = user.username
                session.close()
                token = jwt.encode({"username": username, "id": id, "exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=30)}, SECRET_KEY)

                return {"data": {"token": token}}, 200

            return {"error": "Invalid password"}
        except Exception as e:
            return {"error" : {"Internal Error"}}, 500

        
# get all usernames
class Usernames(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        if token == None:
            return {"error": "Missing Token"}
        
        try:
            
            data = jwt.decode(token.split(" ")[1], SECRET_KEY, "HS256")
        except Exception as e:
            return {"error": "Invalid Token"}
        #can add username access logs to the database
        users = session.query(Users)
        usernames = []
        for user in users:
            usernames.append(user.username)
        
        return {"data": {"usernames": usernames}}



# Api urls
api.add_resource(Register, "/register")
api.add_resource(Login, "/login")
api.add_resource(Usernames, "/users")

if __name__ == "__main__":
    app.run(debug=True)
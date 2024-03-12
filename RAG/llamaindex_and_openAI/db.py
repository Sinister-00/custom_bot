from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
import bcrypt
from pymongo.server_api import ServerApi

load_dotenv()
uri = os.getenv('MONGO_URI')
# print(uri)

# client = MongoClient(uri, server_api=ServerApi('1'))
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)



uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
db = client["VinAi"]

users_collection = db["users"]
def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)  
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def insert_user(email, password):
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return "User with this email already exists"
    else:
        hashed_password = hash_password(password)
        user_data = {"email": email, "password": hashed_password}
        result = users_collection.insert_one(user_data)
        return result.inserted_id

insert_user("swapnil@vinculumgroup.com", "demo@123")
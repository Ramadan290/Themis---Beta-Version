import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI from environment variable
MONGO_URI = os.getenv("MONGO_URI")

# Check if the URI is loaded properly
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

# Connect to MongoDB
client = MongoClient(MONGO_URI)


db = client["APOLLO"] 

# define collections :
users_collection = db["users"]
payroll_collection = db["payroll"]
attendance_collection = db["attendance"]
news_collection = db["news"]
status_collection = db["status"]
skills_collection = db["skills"]
departments_collection = db["skills"]



print("Successfully connected to the database.")


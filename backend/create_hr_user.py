"""
Script to check the HR manager user account in the database.
"""

import sys
import os
from datetime import datetime
import pymongo

# Get the absolute path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path so we can import app modules
sys.path.insert(0, parent_dir)

# Import our application modules
from app.core.config import settings

# Connect to MongoDB
client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
users_collection = db["users"]

# Check if HR user exists
existing_user = users_collection.find_one({"username": "HR"})

if existing_user:
    print("Found HR user in database:")
    print(f"Username: {existing_user.get('username')}")
    print(f"User ID: {existing_user.get('user_id')}")
    print(f"Role: {existing_user.get('role')}")
    print(f"Active: {existing_user.get('active')}")
    
    # Check if role is manager
    if existing_user.get('role') != "manager":
        print("Warning: User does not have manager role!")
    
    # Check if user is active
    if not existing_user.get('active', True):
        print("Warning: User account is marked as inactive!")
else:
    print("HR user not found in database!")
    print("You need to create the user with these properties:")
    print("- username: HR")
    print("- password: admin123")
    print("- role: manager")
    print("- active: true")

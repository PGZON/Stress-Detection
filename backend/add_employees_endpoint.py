"""
Add a new endpoint to the manager.py file to get all employees.
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "stress_sense_db")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
employees_collection = db["employees"]

# Add the new endpoint to manager.py
manager_file_path = os.path.join("app", "api", "endpoints", "manager.py")

# Read the existing content
with open(manager_file_path, "r") as file:
    content = file.read()

# Define the new endpoint
new_endpoint = '''
@router.get("/employees", response_model=List[dict])
async def get_all_employees_endpoint(
    current_user: User = Depends(get_current_manager)
) -> Any:
    '''
    Get a list of all active employees (manager only)
    '''
    employees = get_all_employees()
    
    # Clean MongoDB _id from results
    for employee in employees:
        if "_id" in employee:
            employee.pop("_id")
    
    return employees
'''

# Find a good insertion point after the existing endpoints
# Look for the last endpoint definition
last_endpoint = content.rfind("@router.get")
if last_endpoint != -1:
    # Find the end of the function (next blank line after the endpoint)
    function_end = content.find("\n\n", last_endpoint)
    if function_end == -1:
        function_end = len(content)  # If no blank line found, append to end
    
    # Insert the new endpoint
    new_content = content[:function_end] + "\n\n" + new_endpoint + content[function_end:]
    
    # Fix the triple quotes in the docstring
    new_content = new_content.replace('"""', '\"\"\"', 2)
    
    # Write the updated content back to the file
    with open(manager_file_path, "w") as file:
        file.write(new_content)
    
    print(f"Successfully added get_all_employees_endpoint to {manager_file_path}")
else:
    print(f"Could not find insertion point in {manager_file_path}")
    sys.exit(1)

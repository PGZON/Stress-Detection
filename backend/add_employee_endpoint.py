"""
Add a new endpoint to the manager.py file to get employee details.
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
new_endpoint = """
@router.get("/employee/{employee_id}", response_model=dict)
async def get_employee_details(
    employee_id: str,
    current_user: User = Depends(get_current_manager)
) -> Any:
    '''
    Get detailed information about a specific employee (manager only)
    '''
    # Get employee details
    employee = get_employee(employee_id)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Clean MongoDB _id
    if "_id" in employee:
        employee.pop("_id")
        
    return employee
"""

# Find a good insertion point after the imports and before the first endpoint
insertion_point = content.find("router = APIRouter()")
if insertion_point != -1:
    # Find the end of that line
    insertion_point = content.find("\n", insertion_point) + 1
    
    # Insert the new endpoint
    new_content = content[:insertion_point] + new_endpoint + content[insertion_point:]
    
    # Write the updated content back to the file
    with open(manager_file_path, "w") as file:
        file.write(new_content)
    
    print(f"Successfully added get_employee_details endpoint to {manager_file_path}")
else:
    print(f"Could not find insertion point in {manager_file_path}")
    sys.exit(1)

"""
Create a minimal stress/aggregate endpoint that returns dummy data.
This helps with testing the frontend analytics page.
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

# Add the new endpoint to manager.py
manager_file_path = os.path.join("app", "api", "endpoints", "manager.py")

# Read the existing content
with open(manager_file_path, "r") as file:
    content = file.read()

# Create a temporary endpoint that returns dummy data
dummy_endpoint = """
# Temporary endpoint for testing analytics
@router.get("/stress/aggregate_test", response_model=dict)
async def get_stress_aggregates_test(
    current_user: User = Depends(get_current_manager)
) -> Any:
    '''
    Test endpoint that returns dummy stress aggregates for frontend testing
    '''
    # Return dummy data for frontend testing
    return {
        "summary": {
            "uniqueEmployees": 5,
            "totalReadings": 50,
            "avgStressLevel": 45.5
        },
        "distribution": {
            "Low": 20,
            "Medium": 20,
            "High": 10
        },
        "timeline": [
            {"date": "2025-08-15", "Low": 4, "Medium": 3, "High": 2},
            {"date": "2025-08-16", "Low": 5, "Medium": 2, "High": 1},
            {"date": "2025-08-17", "Low": 3, "Medium": 4, "High": 2},
            {"date": "2025-08-18", "Low": 2, "Medium": 5, "High": 3},
            {"date": "2025-08-19", "Low": 6, "Medium": 2, "High": 1}
        ],
        "departments": [
            {"name": "Engineering", "avgStress": 35.2},
            {"name": "Marketing", "avgStress": 48.7},
            {"name": "Sales", "avgStress": 52.3}
        ]
    }
"""

# Fix triple quotes in the docstring
dummy_endpoint = dummy_endpoint.replace('"""', '\"\"\"', 2)

# Find a good insertion point - after the last endpoint
last_endpoint = content.rfind("@router.get")
if last_endpoint != -1:
    # Find the end of the function
    function_end = content.find("\n\n", last_endpoint)
    if function_end == -1:
        function_end = len(content)  # If no blank line found, append to end
    
    # Insert the new endpoint
    new_content = content[:function_end] + "\n\n" + dummy_endpoint + content[function_end:]
    
    # Write the updated content back to the file
    with open(manager_file_path, "w") as file:
        file.write(new_content)
    
    print(f"Successfully added test analytics endpoint to {manager_file_path}")
else:
    print(f"Could not find insertion point in {manager_file_path}")
    sys.exit(1)

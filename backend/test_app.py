"""
Test script to check if the FastAPI application starts properly.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI

try:
    # Import the app
    from main import app
    
    print("✅ Successfully imported the FastAPI application!")
    print("Routes configured:")
    
    for route in app.routes:
        print(f"  - {route.path}")
    
    print("\nApplication is ready to run!")
    print("To start the server, run: uvicorn main:app --reload")
    
except Exception as e:
    print(f"❌ Error importing the application: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

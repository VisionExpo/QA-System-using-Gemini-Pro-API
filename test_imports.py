#!/usr/bin/env python
"""
Test script to verify that imports work correctly
"""

import sys
import os

print("Python version:", sys.version)
print("Python path:", sys.path)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir("."))

try:
    from app.core.app_factory import create_app
    print("Successfully imported create_app from app.core.app_factory")
    
    app = create_app()
    print("Successfully created app instance")
    
    from wsgi import application
    print("Successfully imported application from wsgi")
    
    print("All imports successful!")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

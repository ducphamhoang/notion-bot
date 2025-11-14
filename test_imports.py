#!/usr/bin/env python3
"""Test script to check if all modules can be imported correctly."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

print("Testing imports...")

try:
    from src.config.settings import get_settings
    print("✓ Successfully imported: src.config.settings")
    
    from src.core.database.connection import DatabaseConnection
    print("✓ Successfully imported: src.core.database.connection")
    
    from src.features.tasks.routes import router as tasks_router
    print("✓ Successfully imported: src.features.tasks.routes")
    
    from src.features.workspaces.routes import router as workspaces_router
    print("✓ Successfully imported: src.features.workspaces.routes")
    
    from src.features.users.routes import router as users_router
    print("✓ Successfully imported: src.features.users.routes")
    
    print("\nAll imports successful!")
    
    # Test settings
    settings = get_settings()
    print(f"\nCurrent settings:")
    print(f"- API Host: {settings.api_host}")
    print(f"- API Port: {settings.api_port}")
    print(f"- Debug: {settings.debug}")
    print(f"- MongoDB URI (first 20 chars): {settings.mongodb_uri[:20]}...")
    
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
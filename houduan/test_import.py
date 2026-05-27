#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
import traceback

def test_imports():
    try:
        print("Testing imports...")
        
        # Test basic imports
        print("1. Importing config...")
        from config import settings
        print("   OK")
        
        print("2. Importing database...")
        from database import async_engine, Base, get_db
        print("   OK")
        
        print("3. Importing models...")
        from models import User, UserRole, UserStatus
        print("   OK")
        
        print("4. Importing schemas...")
        from schemas import UserCreate, UserLogin, TokenResponse, ApiResponse
        print("   OK")
        
        print("5. Importing security...")
        from security import verify_password, get_password_hash, create_access_token
        print("   OK")
        
        print("6. Importing exceptions...")
        from exceptions import AuthException, ForbiddenException
        print("   OK")
        
        print("7. Importing dependencies...")
        from dependencies import get_current_user, require_admin
        print("   OK")
        
        print("8. Importing crud...")
        from crud import create_user, get_user_by_username
        print("   OK")
        
        print("9. Importing routes...")
        from routes.auth import router as auth_router
        from routes.users import router as users_router
        from routes.permission import router as permission_router
        print("   OK")
        
        print("10. Importing main...")
        from main import app
        print("   OK")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed with error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

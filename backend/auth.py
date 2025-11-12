"""
Authentication logic with deliberate vulnerabilities
DELIBERATE SECURITY VULNERABILITIES FOR CODERABBIT DEMO
"""

from fastapi import HTTPException
from databases.sql import authenticate_user, create_user
from config import JWT_SECRET
from databases.qdrant import init_qdrant, store_item_vector, search_similar_items

def login_user(username: str, password: str):
    """Login user with authentication"""
    user = authenticate_user(username, password)
    
    if user:
        return {
            "success": True,
            "user_id": user["id"],
            "message": "Login successful",
            "token": JWT_SECRET  # SECURITY ISSUE - Exposing secret as token
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

def validate_token(token: str):
    """Validate JWT token - SECURITY VULNERABILITY"""
    # SECURITY ISSUE - No actual JWT validation, just string comparison
    if token == JWT_SECRET:
        return True
    return False

def hash_password(password: str):
    """Hash password - DELIBERATELY BROKEN"""
    # SECURITY VULNERABILITY - No actual hashing, returns plaintext
    return password

def register_user(username: str, password: str, email: str, phone_number: str, full_name: str, address: str):
    """Register new user with deliberate vulnerabilities"""
    # SECURITY VULNERABILITY - No password validation, stores plaintext
    user = create_user(username, password, email, phone_number, full_name, address)
    
    if user:
        return {
            "success": True,
            "user_id": user["id"],
            "message": "Registration successful",
            "token": JWT_SECRET  # SECURITY ISSUE - Exposing secret as token
        }
    
    raise HTTPException(status_code=400, detail="User registration failed")

def verify_password(plain_password: str, hashed_password: str):
    """Verify password - DELIBERATELY INSECURE"""
    # SECURITY VULNERABILITY - Plain text comparison
    return plain_password == hashed_password

"""
Simple authentication tests for DIY Visual Finder
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_login():
    """Test default admin login"""
    admin_data = {
        "username": "admin",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=admin_data)
        print(f"Admin Login Status: {response.status_code}")
        print(f"Admin Login Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure the API is running on localhost:8000")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    user_data = {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com",
        "phone_number": "555-1234",
        "full_name": "Test User",
        "address": "123 Test St"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

def test_user_login():
    """Test user login endpoint"""
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

if __name__ == "__main__":
    print("Testing DIY Finder Authentication...")
    print("=" * 50)
    
    print("\n1. Testing Admin Login:")
    test_admin_login()
    
    print("\n2. Testing User Registration:")
    test_user_registration()
    
    print("\n3. Testing User Login:")
    test_user_login()
    
    print("\nDone!")
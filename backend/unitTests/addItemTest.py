"""
Unit tests for add item API endpoint
"""

import requests
import base64
import os

BASE_URL = "http://localhost:8000"

def create_test_image_data():
    """Create a simple base64 encoded test image"""
    # Read the hex-bolts.png image from testData folder
    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, "testData", "wood-test.jpg")
    
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    return f"data:image/png;base64,{image_data}"

def test_add_basic_item():
    """Test adding a basic DIY item"""
    item_data = {
        "username": "test_user",  # SECURITY VULNERABILITY - No authentication
        "image": create_test_image_data()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/items/add", json=item_data)
        print(f"Add Item Status: {response.status_code}")
        print(f"Add Item Response: {response.json()}")
        return response.status_code == 200 and response.json().get("success") == True
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure the API is running on localhost:8000")
        return False

def test_add_item_minimal_data():
    """Test adding item with different username"""
    item_data = {
        "username": "another_user",  # SECURITY VULNERABILITY - Any username accepted
        "image": create_test_image_data()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/items/add", json=item_data)
        print(f"Minimal Item Status: {response.status_code}")
        print(f"Minimal Item Response: {response.json()}")
        return response.status_code == 200 and response.json().get("success") == True
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

def test_add_item_invalid_data():
    """Test adding item with invalid/missing data"""
    invalid_item = {
        "username": "",  # Empty username
        "image": "invalid_image_data"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/items/add", json=invalid_item)
        print(f"Invalid Item Status: {response.status_code}")
        print(f"Invalid Item Response: {response.json()}")
        # Should fail validation
        return response.status_code == 422 or response.json().get("success") == False
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

def test_add_power_tool():
    """Test adding a power tool item with admin username"""
    tool_data = {
        "username": "admin",  # SECURITY VULNERABILITY - Can impersonate any user
        "image": create_test_image_data()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/items/add", json=tool_data)
        print(f"Power Tool Status: {response.status_code}")
        print(f"Power Tool Response: {response.json()}")
        return response.status_code == 200 and response.json().get("success") == True
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

if __name__ == "__main__":
    print("Testing DIY Finder Add Item API...")
    print("=" * 50)
    
    print("\n1. Testing Basic Item Addition:")
    test_add_basic_item()
    
    print("\n2. Testing Minimal Data Item:")
    test_add_item_minimal_data()
    
    print("\n3. Testing Invalid Data:")
    test_add_item_invalid_data()
    
    print("\n4. Testing Power Tool Addition:")
    test_add_power_tool()
    
    print("\nDone!")

"""
Unit tests for search item API endpoint
"""

import requests
import base64
import os

BASE_URL = "http://localhost:8000"

def create_test_image_data():
    """Create a simple base64 encoded test image"""
    # Read the wood-test.jpg image from testData folder
    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, "testData", "wood-test.jpg")
    
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    return f"data:image/png;base64,{image_data}"

def test_search_similar_items():
    """Test searching for similar items using image"""
    search_data = {
        "username": "test_user",  # SECURITY VULNERABILITY - No authentication
        "image": create_test_image_data()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search", json=search_data)
        print(f"Search Status: {response.status_code}")
        print(f"Search Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results = result.get("results", [])
                print(f"Found {len(results)} similar items")
                for i, item in enumerate(results):
                    print(f"  {i+1}. {item.get('name')} (Score: {item.get('score', 'N/A')})")
                return True
            else:
                print(f"Search failed: {result.get('error')}")
                return False
        return False
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure the API is running on localhost:8000")
        return False

def test_search_different_user():
    """Test searching with different username"""
    search_data = {
        "username": "another_user",  # SECURITY VULNERABILITY - Any username accepted
        "image": create_test_image_data()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search", json=search_data)
        print(f"Different User Search Status: {response.status_code}")
        print(f"Different User Search Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results = result.get("results", [])
                print(f"Found {len(results)} items for different user")
                return True
            return False
        return False
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

def test_search_empty_username():
    """Test searching with empty username"""
    search_data = {
        "username": "",  # Empty username
        "image": create_test_image_data()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search", json=search_data)
        print(f"Empty Username Search Status: {response.status_code}")
        print(f"Empty Username Search Response: {response.json()}")
        
        # Should still work but return no results
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

def test_search_invalid_image():
    """Test searching with invalid image data"""
    search_data = {
        "username": "test_user",
        "image": "invalid_image_data"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search", json=search_data)
        print(f"Invalid Image Search Status: {response.status_code}")
        print(f"Invalid Image Search Response: {response.json()}")
        
        # Should fail gracefully
        if response.status_code == 200:
            result = response.json()
            return result.get("success") == False
        return True  # Any error response is acceptable
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

def test_search_admin_user():
    """Test searching as admin user (security vulnerability demo)"""
    search_data = {
        "username": "admin",  # SECURITY VULNERABILITY - Can impersonate admin
        "image": create_test_image_data()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search", json=search_data)
        print(f"Admin Search Status: {response.status_code}")
        print(f"Admin Search Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results = result.get("results", [])
                print(f"Admin found {len(results)} items")
                return True
            return False
        return False
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        return False

if __name__ == "__main__":
    print("Testing DIY Finder Search API...")
    print("=" * 50)
    
    print("\n1. Testing Basic Image Search:")
    test_search_similar_items()
    
    print("\n2. Testing Different User Search:")
    test_search_different_user()
    
    print("\n3. Testing Empty Username:")
    test_search_empty_username()
    
    print("\n4. Testing Invalid Image:")
    test_search_invalid_image()
    
    print("\n5. Testing Admin User Search:")
    test_search_admin_user()
    
    print("\nDone!")

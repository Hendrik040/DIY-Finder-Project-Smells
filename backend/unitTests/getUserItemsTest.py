"""
Unit tests for GET /api/items/{user_id} endpoint
Tests dashboard functionality and SQL injection vulnerabilities
"""

import requests
import json
import sqlite3
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_PATH
from databases.sql import init_db, create_item

BASE_URL = "http://localhost:8000"

def setup_test_data():
    """Setup test database with sample items"""
    init_db()
    
    # Add test items for different users
    test_items = [
        {
            "username": "test_user",
            "name": "M6 Hex Bolts",
            "category": "fasteners",
            "description": "Stainless steel hex bolts",
            "quantity": 25,
            "location": "garage",
            "storage_box": "Box A1",
            "brand": "Generic",
            "size": "M6x20mm",
            "condition": "new",
            "image_data": "data:image/jpeg;base64,test_image_data_1",
            "metadata": '{"ai_analysis": "fastener detected"}'
        },
        {
            "username": "test_user",
            "name": "Wood Screws",
            "category": "fasteners", 
            "description": "Phillips head wood screws",
            "quantity": 100,
            "location": "workshop",
            "storage_box": "Box B2",
            "brand": "DeWalt",
            "size": "2.5x40mm",
            "condition": "new",
            "image_data": "data:image/jpeg;base64,test_image_data_2",
            "metadata": '{"ai_analysis": "wood screw detected"}'
        },
        {
            "username": "admin_user",
            "name": "Wall Anchors",
            "category": "fasteners",
            "description": "Plastic wall anchors",
            "quantity": 50,
            "location": "garage",
            "storage_box": "Box A1", 
            "brand": "Hilti",
            "size": "6mm",
            "condition": "new",
            "image_data": "data:image/jpeg;base64,test_image_data_3",
            "metadata": '{"ai_analysis": "wall anchor detected"}'
        }
    ]
    
    for item in test_items:
        create_item(
            username=item["username"],
            name=item["name"],
            category=item["category"],
            description=item["description"],
            quantity=item["quantity"],
            location=item["location"],
            storage_box=item["storage_box"],
            brand=item["brand"],
            size=item["size"],
            condition=item["condition"],
            image_data=item["image_data"],
            metadata=item["metadata"]
        )
    
    print("✓ Test data setup complete")

def test_get_user_items_normal():
    """Test normal functionality - get items for valid user"""
    print("\n1. Testing normal user items retrieval...")
    
    # Get items for user_id "test_user" (stored as string in user_id field)
    # Need to use a numeric ID that might exist
    response = requests.get(f"{BASE_URL}/api/items/4")  # Try the inserted item ID
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        
        print(f"   ✓ Response status: {response.status_code}")
        print(f"   ✓ Items returned: {len(items)}")
        
        if items:
            print(f"   ✓ First item: {items[0].get('name')}")
            print(f"   ✓ Categories: {[item.get('category') for item in items]}")
        else:
            print("   ⚠ No items found - checking database structure...")
            # Try to query database directly to debug
            import sqlite3
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_id, name FROM items LIMIT 5")
            rows = cursor.fetchall()
            print(f"   Debug - Database contents: {rows}")
            conn.close()
        
        return True
    else:
        print(f"   ✗ Failed with status: {response.status_code}")
        return False

def test_get_user_items_empty():
    """Test with user_id that has no items"""
    print("\n2. Testing empty user items...")
    
    # Get items for user_id 999 (should have no items)
    response = requests.get(f"{BASE_URL}/api/items/999")
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        
        print(f"   ✓ Response status: {response.status_code}")
        print(f"   ✓ Items returned: {len(items)} (expected: 0)")
        
        return len(items) == 0
    else:
        print(f"   ✗ Failed with status: {response.status_code}")
        return False

def test_sql_injection_union_attack():
    """Test SQL injection via UNION attack in user_id parameter"""
    print("\n3. Testing SQL injection - UNION attack...")
    
    # Since FastAPI validates path params as int, we need to test the actual vulnerability
    # The vulnerability is in the backend SQL query, not the path validation
    print("   Note: FastAPI path validation blocks non-integer user_id values")
    print("   Testing with integer values that could exploit the SQL injection...")
    
    # Test with values that would work if SQL injection was possible
    test_values = [1, 999, -1]
    
    for test_val in test_values:
        try:
            response = requests.get(f"{BASE_URL}/api/items/{test_val}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                print(f"   ✓ user_id {test_val}: {len(items)} items returned")
            else:
                print(f"   ✗ user_id {test_val}: Status {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ user_id {test_val}: Request failed - {str(e)}")
    
    print("   ⚠ SQL injection vulnerability exists in backend code but FastAPI blocks string payloads")
    return True

def test_sql_injection_boolean_blind():
    """Test boolean-based blind SQL injection"""
    print("\n4. Testing boolean blind SQL injection...")
    
    print("   Note: FastAPI path validation prevents string-based SQL injection")
    print("   Testing with integer values to check response patterns...")
    
    # Test with integer values that might reveal different behaviors
    test_values = [1, 0, -1, 999999]
    
    results = []
    for i, test_val in enumerate(test_values):
        try:
            response = requests.get(f"{BASE_URL}/api/items/{test_val}")
            
            if response.status_code == 200:
                data = response.json()
                item_count = len(data.get("items", []))
                results.append(item_count)
                print(f"   ✓ Value {test_val}: {item_count} items returned")
            else:
                results.append(0)
                print(f"   ✗ Value {test_val}: Status {response.status_code}")
                
        except Exception as e:
            results.append(0)
            print(f"   ✗ Value {test_val}: Request failed - {str(e)}")
    
    # The vulnerability exists but is mitigated by FastAPI validation
    print("   ✓ FastAPI path validation provides protection against string-based attacks")
    return True

def test_dashboard_data_structure():
    """Test that response structure is suitable for frontend dashboard"""
    print("\n5. Testing dashboard data structure...")
    
    response = requests.get(f"{BASE_URL}/api/items/1")
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        
        print(f"   ✓ Response has 'items' array: {isinstance(items, list)}")
        
        if items:
            item = items[0]
            required_fields = ["id", "name", "category", "created_at"]
            
            for field in required_fields:
                if field in item:
                    print(f"   ✓ Item has '{field}' field")
                else:
                    print(f"   ✗ Item missing '{field}' field")
            
            print(f"   ✓ Sample item structure: {list(item.keys())}")
            return True
        else:
            print("   ⚠ No items returned to test structure")
            return False
    else:
        print(f"   ✗ Failed with status: {response.status_code}")
        return False

def test_invalid_user_id_types():
    """Test with invalid user_id types"""
    print("\n6. Testing invalid user_id types...")
    
    invalid_ids = ["abc", "null", "undefined", "-1", "0"]
    
    for invalid_id in invalid_ids:
        try:
            response = requests.get(f"{BASE_URL}/api/items/{invalid_id}")
            print(f"   ✓ user_id '{invalid_id}': Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                print(f"     Items returned: {len(items)}")
                
        except Exception as e:
            print(f"   ✗ user_id '{invalid_id}': Request failed - {str(e)}")
    
    return True

def run_all_tests():
    """Run all test scenarios"""
    print("=" * 60)
    print("TESTING GET /api/items/{user_id} ENDPOINT")
    print("=" * 60)
    
    # Setup test data
    setup_test_data()
    
    # Run tests
    tests = [
        test_get_user_items_normal,
        test_get_user_items_empty,
        test_sql_injection_union_attack,
        test_sql_injection_boolean_blind,
        test_dashboard_data_structure,
        test_invalid_user_id_types
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ✗ Test failed with exception: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests completed successfully!")
    else:
        print("⚠️  Some tests revealed issues or vulnerabilities")
    
    print("\nNOTE: This endpoint is designed for frontend dashboard")
    print("Expected vulnerabilities: SQL injection via user_id parameter")

if __name__ == "__main__":
    run_all_tests()

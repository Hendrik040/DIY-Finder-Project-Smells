"""
Simple SQLite database viewer for DIY Finder
"""

import sqlite3
import json
import sys
import os

# Add parent directory to path to import config
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
from config import DATABASE_PATH

# Fix the database path to be relative to backend directory
DATABASE_PATH = os.path.join(backend_dir, DATABASE_PATH)

def view_all_users():
    """Display all users in the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    print("USERS TABLE:")
    print("-" * 120)
    print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Phone':<15} {'Full Name':<20} {'Address':<30}")
    print("-" * 120)
    
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[3]:<25} {user[4] or 'N/A':<15} {user[5] or 'N/A':<20} {user[6] or 'N/A':<30}")
    
    conn.close()
    return users

def view_all_items():
    """Display all items in the database (excluding base64 image data)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Select all fields except image_data and metadata to avoid printing base64
    cursor.execute("SELECT id, user_id, name, category, description, quantity, location, storage_box, brand, size, condition, purchase_date, created_at, last_updated FROM items")
    items = cursor.fetchall()
    
    print("\nITEMS TABLE (EXCLUDING IMAGE DATA):")
    print("-" * 180)
    print(f"{'ID':<3} {'User':<10} {'Name':<15} {'Cat':<8} {'Desc':<20} {'Qty':<3} {'Loc':<12} {'Box':<10} {'Brand':<8} {'Size':<8} {'Cond':<6} {'Created':<10} {'Updated':<10}")
    print("-" * 180)
    
    for item in items:
        # Format datetime strings to show just date
        created = item[11][:10] if item[11] else 'N/A'
        updated = item[12][:10] if item[12] else 'N/A'
        
        print(f"{item[0]:<3} {item[1] or 'N/A':<10} {item[2][:14] or 'N/A':<15} {item[3][:7] or 'N/A':<8} {item[4][:19] or 'N/A':<20} {item[5] or 1:<3} {item[6][:11] or 'N/A':<12} {item[7][:9] or 'N/A':<10} {item[8][:7] or 'N/A':<8} {item[9][:7] or 'N/A':<8} {item[10][:5] or 'N/A':<6} {created:<10} {updated:<10}")
    
    print(f"\nTotal items: {len(items)}")
    
    # Show detailed view of last 3 items
    if items:
        print(f"\nDETAILED VIEW (Last 3 items):")
        print("=" * 80)
        for item in items[-3:]:
            print(f"ID: {item[0]} | Username: {item[1]} | Name: {item[2]}")
            print(f"Category: {item[3]} | Description: {item[4]}")
            print(f"Quantity: {item[5]} | Location: {item[6]} | Storage Box: {item[7]}")
            print(f"Brand: {item[8]} | Size: {item[9]} | Condition: {item[10]}")
            print(f"Purchase Date: {item[11]} | Created: {item[12]} | Updated: {item[13]}")
            print("-" * 80)
    
    conn.close()
    return items

def view_table_schema():
    """Show database table schemas"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("\nDATABASE SCHEMA:")
    print("=" * 50)
    
    # Get users table schema
    cursor.execute("PRAGMA table_info(users)")
    users_schema = cursor.fetchall()
    print("\nUSERS TABLE SCHEMA:")
    for col in users_schema:
        print(f"  {col[1]} ({col[2]})")
    
    # Get items table schema
    cursor.execute("PRAGMA table_info(items)")
    items_schema = cursor.fetchall()
    print("\nITEMS TABLE SCHEMA:")
    for col in items_schema:
        print(f"  {col[1]} ({col[2]})")
    
    conn.close()

def count_records():
    """Count records in each table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM items")
    item_count = cursor.fetchone()[0]
    
    print(f"\nRECORD COUNTS:")
    print(f"Users: {user_count}")
    print(f"Items: {item_count}")
    
    conn.close()

if __name__ == "__main__":
    print("DIY Finder Database Viewer")
    print("=" * 50)
    
    try:
        count_records()
        view_table_schema()
        view_all_users()
        view_all_items()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the database exists and the server has been started at least once.")

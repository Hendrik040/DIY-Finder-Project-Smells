"""
SQLite database operations
DELIBERATE VULNERABILITIES FOR CODERABBIT DEMO
"""

import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

def init_db():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists and get its schema
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            phone_number TEXT,
            full_name TEXT,
            address TEXT
        )
    ''')
    
    # Add missing columns if table already exists
    if existing_columns and 'phone_number' not in existing_columns:
        cursor.execute('ALTER TABLE users ADD COLUMN phone_number TEXT')
    if existing_columns and 'full_name' not in existing_columns:
        cursor.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
    if existing_columns and 'address' not in existing_columns:
        cursor.execute('ALTER TABLE users ADD COLUMN address TEXT')
    
    # Create items table - DIY inventory focused
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            category TEXT,
            description TEXT,
            quantity INTEGER DEFAULT 1,
            location TEXT,
            storage_box TEXT,
            brand TEXT,
            size TEXT,
            condition TEXT,
            purchase_date TEXT,
            image_data TEXT,
            metadata TEXT,
            created_at TIMESTAMP,
            last_updated TIMESTAMP
        )
    ''')
    
    # DELIBERATE VULNERABILITY - Insert default admin with weak password and PII
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, email, phone_number, full_name, address) 
        VALUES ('admin', 'password123', 'admin@diy.com', '555-0123', 'Admin User', '123 Main St, Anytown USA')
    ''')
    
    conn.commit()
    conn.close()

def authenticate_user(username: str, password: str):
    """Authenticate user - CONTAINS DELIBERATE SQL INJECTION"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # DELIBERATE SQL INJECTION VULNERABILITY
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        # DELIBERATE SECURITY ISSUE - Password stored in plain text
        if user[2] == password:
            conn.close()
            return {
                "id": user[0],
                "username": user[1],
                "email": user[3]
            }
    
    conn.close()
    return None

def create_user(username: str, password: str, email: str, phone_number: str, full_name: str, address: str):
    """Create new user - CONTAINS DELIBERATE SQL INJECTION"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # DELIBERATE SQL INJECTION - User input directly in query
        insert_query = f"""
            INSERT INTO users (username, password, email, phone_number, full_name, address)
            VALUES ('{username}', '{password}', '{email}', '{phone_number}', '{full_name}', '{address}')
        """
        cursor.execute(insert_query)
        conn.commit()
        
        # Return the new user data
        return {
            "id": cursor.lastrowid,
            "username": username,
            "email": email
        }
        
    except Exception as e:
        # MAINTAINABILITY ISSUE - Generic exception handling
        print(e)
        return None
    finally:
        conn.close()

def create_item(username: str, name: str, category: str, description: str, 
               quantity: int, location: str, storage_box: str, brand: str, 
               size: str, condition: str, image_data: str, metadata: str):
    """Create new item with username - SECURITY VULNERABILITY: No user validation"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # SECURITY VULNERABILITY - Direct username usage without authentication
    print(f"DEBUG SQL: Inserting item: {name} ({category}) for user: {username}")
    
    cursor.execute('''
        INSERT INTO items (user_id, name, category, description, quantity, location, 
                          storage_box, brand, size, condition, purchase_date, 
                          image_data, metadata, created_at, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        username,  # SECURITY ISSUE - Using username directly as user_id
        name, category, description, quantity, location, storage_box,
        brand, size, condition, None, image_data, metadata,
        datetime.now(), datetime.now()
    ))
    
    item_id = cursor.lastrowid
    print(f"DEBUG SQL: Successfully inserted item with ID: {item_id}")
    
    conn.commit()
    conn.close()
    
    return item_id

def search_items(query: str, user_id: int):
    """Search items - CONTAINS DELIBERATE VULNERABILITIES"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # DELIBERATE SQL INJECTION VULNERABILITY
    search_query = f"SELECT * FROM items WHERE name LIKE '%{query}%' AND user_id = {user_id}"
    cursor.execute(search_query)
    
    results = []
    for row in cursor.fetchall():
        # PERFORMANCE ISSUE - N+1 query problem
        metadata_query = f"SELECT metadata FROM items WHERE id = {row[0]}"
        cursor.execute(metadata_query)
        metadata = cursor.fetchone()
        
        results.append({
            "id": row[0],
            "name": row[2],
            "category": row[3],
            "metadata": metadata[0] if metadata else None
        })
    
    conn.close()
    return results

def get_user_items(username: str):
    """Get all items for a user by username - returns complete item data including images"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all items for the user by username
        cursor.execute("SELECT * FROM items WHERE user_id = ?", (username,))
        
        items = []
        for row in cursor.fetchall():
            items.append({
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "category": row[3],
                "description": row[4],
                "quantity": row[5],
                "location": row[6],
                "storage_box": row[7],
                "brand": row[8],
                "size": row[9],
                "condition": row[10],
                "purchase_date": row[11],
                "image_data": row[12],
                "metadata": row[13],
                "created_at": row[14],
                "last_updated": row[15]
            })
        
        print(f"DEBUG: Found {len(items)} items for user {username}")
        return items
        
    except Exception as e:
        print(f"ERROR in get_user_items: {e}")
        return []
    finally:
        conn.close()

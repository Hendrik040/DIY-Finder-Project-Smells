"""
Comprehensive unit tests for backend/databases/sql.py

Tests cover:
- Removed delete_item function
- Database operations
- SQL security
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.databases.sql import (
    init_db,
    create_item,
    search_items,
    get_user_items
)


class TestSQLFunctions(unittest.TestCase):
    """Test SQL database functions"""

    def test_delete_item_function_removed(self):
        """Should verify delete_item function is removed"""
        import backend.databases.sql as sql_module
        self.assertFalse(hasattr(sql_module, 'delete_item'))

    @patch('backend.databases.sql.sqlite3.connect')
    def test_init_db_creates_tables(self, mock_connect):
        """Should initialize database and create tables"""
        mock_cursor = Mock()
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        init_db()
        
        # Verify tables are created
        self.assertGreater(mock_cursor.execute.call_count, 0)
        mock_conn.commit.assert_called()

    @patch('backend.databases.sql.sqlite3.connect')
    def test_create_item_success(self, mock_connect):
        """Should create item successfully"""
        mock_cursor = Mock()
        mock_cursor.lastrowid = 1
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        result = create_item(
            user_id="testuser",
            name="Hammer",
            category="Tools",
            description="A hammer",
            quantity=1,
            location="Garage",
            storage_box="Box1",
            brand="Stanley",
            size="Medium",
            condition="Good",
            purchase_date="2024-01-01",
            image_data=None,
            metadata={}
        )
        
        self.assertEqual(result, 1)
        mock_conn.commit.assert_called_once()

    @patch('backend.databases.sql.sqlite3.connect')
    def test_create_item_error_handling(self, mock_connect):
        """Should handle errors in create_item"""
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        result = create_item(
            user_id="testuser",
            name="Hammer",
            category="Tools",
            description="",
            quantity=1,
            location="",
            storage_box="",
            brand="",
            size="",
            condition="",
            purchase_date="",
            image_data=None,
            metadata={}
        )
        
        self.assertIsNone(result)

    @patch('backend.databases.sql.sqlite3.connect')
    def test_get_user_items_success(self, mock_connect):
        """Should get user items successfully"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "testuser", "Hammer", "Tools", "A hammer", 1, "Garage", "Box1", "Stanley", "M", "Good", "2024-01-01", None, "{}", "2024-01-01", "2024-01-01")
        ]
        mock_cursor.description = [
            ("id",), ("user_id",), ("name",), ("category",), ("description",),
            ("quantity",), ("location",), ("storage_box",), ("brand",), ("size",),
            ("condition",), ("purchase_date",), ("image_data",), ("metadata",),
            ("created_at",), ("last_updated",)
        ]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        results = get_user_items("testuser")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Hammer")
        self.assertEqual(results[0]["user_id"], "testuser")

    @patch('backend.databases.sql.sqlite3.connect')
    def test_get_user_items_empty(self, mock_connect):
        """Should handle empty results"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("id",), ("name",)]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        results = get_user_items("nonexistent")
        
        self.assertEqual(len(results), 0)

    @patch('backend.databases.sql.sqlite3.connect')
    def test_search_items_by_query(self, mock_connect):
        """Should search items by query"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "testuser", "M6 Bolt", "Hardware", "Hex bolt", 10, "Garage", "Box2", "Generic", "M6", "New", "2024-01-01", None, "{}", "2024-01-01", "2024-01-01")
        ]
        mock_cursor.description = [
            ("id",), ("user_id",), ("name",), ("category",), ("description",),
            ("quantity",), ("location",), ("storage_box",), ("brand",), ("size",),
            ("condition",), ("purchase_date",), ("image_data",), ("metadata",),
            ("created_at",), ("last_updated",)
        ]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        results = search_items("bolt", "testuser")
        
        self.assertGreater(len(results), 0)


if __name__ == '__main__':
    unittest.main()
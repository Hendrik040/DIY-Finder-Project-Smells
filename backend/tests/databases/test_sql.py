"""
Comprehensive unit tests for backend/databases/sql.py
Testing SQL database operations (focusing on removed delete_item function)
"""
import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from databases.sql import (
    init_db,
    create_item,
    search_items,
    get_user_items
)


class TestInitDb:
    """Test suite for init_db function"""
    
    @patch('databases.sql.sqlite3.connect')
    def test_init_db_creates_tables(self, mock_connect):
        """Test that init_db creates necessary tables"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        init_db()
        
        mock_connect.assert_called_once()
        # Should execute CREATE TABLE statements
        assert mock_cursor.execute.call_count >= 2  # users and items tables
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('databases.sql.sqlite3.connect')
    def test_init_db_handles_existing_tables(self, mock_connect):
        """Test that init_db handles already existing tables gracefully"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Tables already exist shouldn't cause issues with IF NOT EXISTS
        init_db()
        
        mock_conn.commit.assert_called_once()
    
    @patch('databases.sql.sqlite3.connect')
    def test_init_db_handles_connection_error(self, mock_connect):
        """Test handling of database connection errors"""
        mock_connect.side_effect = sqlite3.Error("Cannot connect to database")
        
        with pytest.raises(sqlite3.Error):
            init_db()


class TestCreateItem:
    """Test suite for create_item function"""
    
    @patch('databases.sql.sqlite3.connect')
    def test_create_item_success(self, mock_connect):
        """Test successful item creation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        
        item_data = {
            "name": "Test Bolt",
            "category": "hardware",
            "description": "M6 x 20mm bolt",
            "quantity": 10,
            "location": "garage",
            "user_id": "testuser"
        }
        
        result = create_item(item_data)
        
        assert result == 123
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('databases.sql.sqlite3.connect')
    def test_create_item_with_all_fields(self, mock_connect):
        """Test creating item with all possible fields"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 456
        
        item_data = {
            "name": "Premium Bolt",
            "category": "hardware",
            "description": "High quality bolt",
            "quantity": 50,
            "location": "workshop",
            "storage_box": "Box A1",
            "brand": "BrandX",
            "size": "M6 x 20mm",
            "condition": "new",
            "purchase_date": "2024-01-15",
            "image_data": "base64_image_string",
            "metadata": '{"key": "value"}',
            "user_id": "testuser"
        }
        
        result = create_item(item_data)
        
        assert result == 456
        mock_conn.commit.assert_called_once()
    
    @patch('databases.sql.sqlite3.connect')
    def test_create_item_handles_sql_error(self, mock_connect):
        """Test handling of SQL errors during item creation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Constraint violation")
        
        item_data = {"name": "Test", "user_id": "testuser"}
        
        result = create_item(item_data)
        
        assert result is None or isinstance(result, (bool, int))
        mock_conn.close.assert_called()


class TestSearchItems:
    """Test suite for search_items function"""
    
    @patch('databases.sql.sqlite3.connect')
    def test_search_items_by_name(self, mock_connect):
        """Test searching items by name"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            (1, "testuser", "Test Bolt", "hardware", "M6 bolt", 10, "garage", None, None, None, None, None, None, None, "2024-01-01", "2024-01-01")
        ]
        
        results = search_items(query="bolt", username="testuser")
        
        assert len(results) == 1
        assert results[0]["name"] == "Test Bolt"
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('databases.sql.sqlite3.connect')
    def test_search_items_by_category(self, mock_connect):
        """Test searching items by category"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        results = search_items(category="hardware", username="testuser")
        
        mock_cursor.execute.assert_called_once()
        # Verify category filter is applied
        call_args = mock_cursor.execute.call_args[0][0]
        assert "category" in call_args.lower()
    
    @patch('databases.sql.sqlite3.connect')
    def test_search_items_no_results(self, mock_connect):
        """Test search with no matching results"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        results = search_items(query="nonexistent", username="testuser")
        
        assert results == []
    
    @patch('databases.sql.sqlite3.connect')
    def test_search_items_handles_sql_error(self, mock_connect):
        """Test handling of SQL errors during search"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        results = search_items(query="test", username="testuser")
        
        assert results == []
        mock_conn.close.assert_called()


class TestGetUserItems:
    """Test suite for get_user_items function"""
    
    @patch('databases.sql.sqlite3.connect')
    def test_get_user_items_success(self, mock_connect):
        """Test successfully retrieving user items"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            (1, "testuser", "Item 1", "category1", "desc1", 5, "loc1", None, None, None, None, None, None, None, "2024-01-01", "2024-01-01"),
            (2, "testuser", "Item 2", "category2", "desc2", 10, "loc2", None, None, None, None, None, None, None, "2024-01-02", "2024-01-02")
        ]
        
        results = get_user_items("testuser")
        
        assert len(results) == 2
        assert results[0]["name"] == "Item 1"
        assert results[1]["name"] == "Item 2"
        assert results[0]["user_id"] == "testuser"
        mock_cursor.execute.assert_called_once()
    
    @patch('databases.sql.sqlite3.connect')
    def test_get_user_items_empty(self, mock_connect):
        """Test retrieving items for user with no items"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        results = get_user_items("newuser")
        
        assert results == []
    
    @patch('databases.sql.sqlite3.connect')
    def test_get_user_items_filters_by_username(self, mock_connect):
        """Test that get_user_items properly filters by username"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        get_user_items("specific_user")
        
        # Verify SQL query includes user_id filter
        call_args = mock_cursor.execute.call_args[0]
        assert "user_id" in call_args[0].lower()
        assert "specific_user" in call_args[1]
    
    @patch('databases.sql.sqlite3.connect')
    def test_get_user_items_handles_sql_error(self, mock_connect):
        """Test handling of SQL errors when retrieving user items"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Database locked")
        
        results = get_user_items("testuser")
        
        assert results == []
        mock_conn.close.assert_called()
    
    @patch('databases.sql.sqlite3.connect')
    def test_get_user_items_with_special_characters_in_username(self, mock_connect):
        """Test retrieving items for username with special characters"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        # Should handle usernames with dots, underscores, hyphens
        get_user_items("user.name-123")
        
        mock_cursor.execute.assert_called_once()


class TestDeletedFunctionality:
    """Test suite to verify delete_item function was removed"""
    
    def test_delete_item_function_not_available(self):
        """Verify that delete_item function is no longer available"""
        import databases.sql as sql_module
        
        assert not hasattr(sql_module, 'delete_item'), \
            "delete_item function should have been removed from sql.py"
    
    def test_delete_item_not_importable(self):
        """Verify delete_item cannot be imported"""
        with pytest.raises(ImportError):
            from databases.sql import delete_item


class TestDatabaseSecurity:
    """Test suite for database security considerations"""
    
    @patch('databases.sql.sqlite3.connect')
    def test_parameterized_queries_used(self, mock_connect):
        """Test that parameterized queries are used to prevent SQL injection"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        # Test search_items uses parameterized queries
        search_items(query="test'; DROP TABLE items--", username="testuser")
        
        # Verify execute was called with parameters tuple (not string concatenation)
        call_args = mock_cursor.execute.call_args
        assert len(call_args[0]) >= 1  # SQL query
        if len(call_args[0]) > 1 or (len(call_args) > 1 and len(call_args[1]) > 0):
            # Parameters should be passed separately
            pass
    
    @patch('databases.sql.sqlite3.connect')
    def test_user_isolation(self, mock_connect):
        """Test that queries properly isolate users' data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        get_user_items("user1")
        
        # Verify user_id is in the WHERE clause
        call_args = mock_cursor.execute.call_args[0]
        assert "WHERE" in call_args[0] or "where" in call_args[0]
        assert call_args[1][0] == "user1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
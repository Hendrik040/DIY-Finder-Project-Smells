"""
Comprehensive unit tests for backend/utils.py

Tests cover:
- SQL query validation functions
- Username sanitization
- Chat with database functionality
- Edge cases and security scenarios
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sqlite3
import json
from backend.utils import (
    _validate_sql_query,
    _sanitize_username,
    chat_with_database,
    process_item_data,
    generate_embedding,
    extract_diy_metadata
)


class TestValidateSQLQuery(unittest.TestCase):
    """Test SQL query validation for security"""

    def test_valid_select_query_with_user_id_filter(self):
        """Should accept valid SELECT query with user_id filter"""
        query = "SELECT * FROM items WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_select_with_like_clause(self):
        """Should accept SELECT with LIKE for fuzzy matching"""
        query = "SELECT * FROM items WHERE user_id = ? AND name LIKE '%bolt%'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_select_with_sum_aggregate(self):
        """Should accept SELECT with SUM aggregate function"""
        query = "SELECT SUM(quantity) FROM items WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_reject_drop_query(self):
        """Should reject DROP queries"""
        query = "DROP TABLE items"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("DROP", error)

    def test_reject_delete_query(self):
        """Should reject DELETE queries"""
        query = "DELETE FROM items WHERE user_id = 'testuser'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("SELECT", error)

    def test_reject_update_query(self):
        """Should reject UPDATE queries"""
        query = "UPDATE items SET quantity = 0 WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("SELECT", error)

    def test_reject_insert_query(self):
        """Should reject INSERT queries"""
        query = "INSERT INTO items (name, user_id) VALUES ('test', 'user')"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("SELECT", error)

    def test_reject_query_without_user_id_filter(self):
        """Should reject query on items table without user_id filter"""
        query = "SELECT * FROM items WHERE name LIKE '%bolt%'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("user_id filter", error)

    def test_reject_union_injection_attempt(self):
        """Should reject UNION-based SQL injection"""
        query = "SELECT * FROM items WHERE user_id = ? UNION SELECT * FROM users"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("UNION", error)

    def test_reject_comment_injection(self):
        """Should reject queries with SQL comments"""
        query = "SELECT * FROM items WHERE user_id = ? -- AND deleted = 0"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("--", error)

    def test_reject_multiline_comment_injection(self):
        """Should reject queries with multiline comments"""
        query = "SELECT * FROM items /* comment */ WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("/*", error)

    def test_reject_semicolon_injection(self):
        """Should reject queries with semicolons (multiple statements)"""
        query = "SELECT * FROM items WHERE user_id = ?; DROP TABLE items;"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn(";", error)

    def test_reject_access_to_users_table(self):
        """Should reject queries accessing users table"""
        query = "SELECT * FROM users WHERE username = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("users table", error)

    def test_reject_join_with_users_table(self):
        """Should reject JOIN with users table"""
        query = "SELECT * FROM items JOIN users ON items.user_id = users.username WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("users table", error)

    def test_case_insensitive_keyword_detection(self):
        """Should detect dangerous keywords regardless of case"""
        queries = [
            "select * from items where user_id = ? union select * from users",
            "SeLeCt * FrOm items WhErE user_id = ? UnIoN SeLeCt * FrOm users",
            "SELECT * FROM items WHERE user_id = ? delete from items"
        ]
        for query in queries:
            is_valid, error = _validate_sql_query(query, "testuser")
            self.assertFalse(is_valid, f"Should reject: {query}")

    def test_whitespace_normalization(self):
        """Should normalize whitespace in queries"""
        query = "SELECT   *  FROM   items  WHERE   user_id   =   ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertTrue(is_valid)

    def test_reject_alter_table(self):
        """Should reject ALTER TABLE queries"""
        query = "ALTER TABLE items ADD COLUMN test TEXT"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("ALTER", error)

    def test_reject_create_table(self):
        """Should reject CREATE TABLE queries"""
        query = "CREATE TABLE malicious (id INTEGER)"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("CREATE", error)

    def test_reject_truncate_table(self):
        """Should reject TRUNCATE queries"""
        query = "TRUNCATE TABLE items"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        self.assertFalse(is_valid)
        self.assertIn("TRUNCATE", error)

    def test_reject_exec_execute(self):
        """Should reject EXEC/EXECUTE queries"""
        queries = ["EXEC sp_something", "EXECUTE stored_proc"]
        for query in queries:
            is_valid, error = _validate_sql_query(query, "testuser")
            self.assertFalse(is_valid, f"Should reject: {query}")
            self.assertIn("EXEC", error)


class TestSanitizeUsername(unittest.TestCase):
    """Test username sanitization for SQL injection prevention"""

    def test_valid_alphanumeric_username(self):
        """Should allow valid alphanumeric username"""
        username = "testuser123"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "testuser123")

    def test_username_with_underscore(self):
        """Should allow underscores in username"""
        username = "test_user"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "test_user")

    def test_username_with_hyphen(self):
        """Should allow hyphens in username"""
        username = "test-user"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "test-user")

    def test_username_with_dot(self):
        """Should allow dots in username"""
        username = "test.user"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "test.user")

    def test_remove_sql_injection_characters(self):
        """Should remove SQL injection characters"""
        username = "test'; DROP TABLE items; --"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "testDROPTABLEitems--")

    def test_remove_quotes(self):
        """Should remove single and double quotes"""
        username = "test'user\"name"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "testusername")

    def test_remove_special_characters(self):
        """Should remove special characters"""
        username = "test@user#name$"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "testusername")

    def test_remove_parentheses_brackets(self):
        """Should remove parentheses and brackets"""
        username = "test(user)[name]{}"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "testusername")

    def test_remove_backslashes(self):
        """Should remove backslashes"""
        username = "test\\user\\name"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "testusername")

    def test_empty_username(self):
        """Should return empty string for invalid username"""
        username = "!@#$%^&*()"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "")

    def test_unicode_characters_removed(self):
        """Should remove unicode characters"""
        username = "test用户name"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "testname")

    def test_email_like_username(self):
        """Should sanitize email-like usernames"""
        username = "user@example.com"
        sanitized = _sanitize_username(username)
        self.assertEqual(sanitized, "userexample.com")


class TestChatWithDatabase(unittest.TestCase):
    """Test chat with database functionality"""

    @patch('backend.utils.Mistral')
    @patch('backend.utils.sqlite3.connect')
    def test_valid_chat_query_execution(self, mock_connect, mock_mistral):
        """Should execute valid chat query successfully"""
        # Setup mocks
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        # Mock first response with function call
        mock_tool_call = Mock()
        mock_tool_call.function.name = "execute_sql_query"
        mock_tool_call.function.arguments = json.dumps({
            "sql_query": "SELECT * FROM items WHERE user_id = ?",
            "explanation": "Finding all items"
        })
        
        mock_first_response = Mock()
        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]
        
        # Mock second response with final answer
        mock_second_response = Mock()
        mock_second_response.choices = [Mock()]
        mock_second_response.choices[0].message.content = "You have 5 items in your inventory"
        
        mock_client.chat.complete.side_effect = [mock_first_response, mock_second_response]
        
        # Mock database
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "testuser", "Hammer", "Tools", "A hammer", 1, "Garage", "Box1", "Brand", "M", "Good", "2024-01-01", None, None, "2024-01-01", "2024-01-01")
        ]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Execute
        result = chat_with_database("testuser", "Show me all my items")
        
        # Verify
        self.assertIn("5 items", result)
        mock_cursor.execute.assert_called_once()

    @patch('backend.utils.Mistral')
    def test_invalid_username_rejected(self, mock_mistral):
        """Should reject invalid username format"""
        result = chat_with_database("test'; DROP TABLE items; --", "Show items")
        self.assertIn("Invalid username format", result)

    @patch('backend.utils.Mistral')
    def test_sql_injection_in_message_rejected(self, mock_mistral):
        """Should reject messages with SQL injection attempts"""
        result = chat_with_database("testuser", "Show items; DROP TABLE items;")
        self.assertIn("invalid characters", result)

    @patch('backend.utils.Mistral')
    def test_message_length_limit(self, mock_mistral):
        """Should limit message length to prevent abuse"""
        long_message = "A" * 1000
        result = chat_with_database("testuser", long_message)
        # Message should be truncated to 500 chars

    @patch('backend.utils.Mistral')
    @patch('backend.utils.sqlite3.connect')
    def test_dangerous_query_blocked(self, mock_connect, mock_mistral):
        """Should block dangerous queries from AI"""
        # Setup mocks
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        # Mock AI trying to execute dangerous query
        mock_tool_call = Mock()
        mock_tool_call.function.name = "execute_sql_query"
        mock_tool_call.function.arguments = json.dumps({
            "sql_query": "DELETE FROM items WHERE user_id = ?",
            "explanation": "Deleting items"
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        
        mock_client.chat.complete.return_value = mock_response
        
        # Execute
        result = chat_with_database("testuser", "Delete all my items")
        
        # Verify dangerous query was blocked
        self.assertIn("security reasons", result)

    @patch('backend.utils.Mistral')
    @patch('backend.utils.sqlite3.connect')
    def test_query_without_user_id_filter_blocked(self, mock_connect, mock_mistral):
        """Should block queries without user_id filter"""
        # Setup mocks
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        # Mock AI trying to query without user filter
        mock_tool_call = Mock()
        mock_tool_call.function.name = "execute_sql_query"
        mock_tool_call.function.arguments = json.dumps({
            "sql_query": "SELECT * FROM items",
            "explanation": "Finding all items"
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        
        mock_client.chat.complete.return_value = mock_response
        
        # Execute
        result = chat_with_database("testuser", "Show all items")
        
        # Verify query was blocked
        self.assertIn("security reasons", result)

    @patch('backend.utils.Mistral')
    @patch('backend.utils.sqlite3.connect')
    def test_sql_error_handling(self, mock_connect, mock_mistral):
        """Should handle SQL errors gracefully without exposing details"""
        # Setup mocks
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        mock_tool_call = Mock()
        mock_tool_call.function.name = "execute_sql_query"
        mock_tool_call.function.arguments = json.dumps({
            "sql_query": "SELECT * FROM items WHERE user_id = ?",
            "explanation": "Finding items"
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        
        mock_client.chat.complete.return_value = mock_response
        
        # Mock database error
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Execute
        result = chat_with_database("testuser", "Show items")
        
        # Verify error is handled gracefully
        self.assertIn("encountered an error", result)
        self.assertNotIn("Database error", result)  # Should not expose SQL error

    @patch('backend.utils.Mistral')
    @patch('backend.utils.sqlite3.connect')
    def test_parameterized_query_execution(self, mock_connect, mock_mistral):
        """Should execute queries with parameterized username"""
        # Setup mocks
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        mock_tool_call = Mock()
        mock_tool_call.function.name = "execute_sql_query"
        mock_tool_call.function.arguments = json.dumps({
            "sql_query": "SELECT * FROM items WHERE user_id = ?",
            "explanation": "Finding items"
        })
        
        mock_first_response = Mock()
        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]
        
        mock_second_response = Mock()
        mock_second_response.choices = [Mock()]
        mock_second_response.choices[0].message.content = "Found items"
        
        mock_client.chat.complete.side_effect = [mock_first_response, mock_second_response]
        
        # Mock database
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Execute
        result = chat_with_database("testuser", "Show items")
        
        # Verify parameterized query was used
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        self.assertIn("testuser", call_args[0][1])  # Username as parameter

    @patch('backend.utils.Mistral')
    def test_no_function_call_response(self, mock_mistral):
        """Should handle responses without function calls"""
        # Setup mocks
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "I can help you with your inventory"
        
        mock_client.chat.complete.return_value = mock_response
        
        # Execute
        result = chat_with_database("testuser", "Hello")
        
        # Verify
        self.assertIn("help you", result)


class TestProcessItemData(unittest.TestCase):
    """Test item data processing"""

    @patch('backend.utils.encode_image_base64')
    @patch('backend.utils.analyze_with_vision')
    def test_process_item_with_image(self, mock_vision, mock_encode):
        """Should process item with image successfully"""
        mock_encode.return_value = "base64_encoded_image"
        mock_vision.return_value = {
            "name": "Hammer",
            "category": "Tools",
            "description": "A claw hammer"
        }
        
        mock_file = Mock()
        mock_file.filename = "hammer.jpg"
        
        result = process_item_data(
            file=mock_file,
            name="",
            category="",
            description="",
            quantity=1,
            location="",
            storage_box="",
            brand="",
            size="",
            condition="",
            purchase_date=""
        )
        
        self.assertEqual(result["name"], "Hammer")
        self.assertEqual(result["category"], "Tools")

    def test_process_item_without_image(self):
        """Should process item without image"""
        result = process_item_data(
            file=None,
            name="Hammer",
            category="Tools",
            description="A tool",
            quantity=1,
            location="Garage",
            storage_box="Box1",
            brand="Stanley",
            size="Medium",
            condition="Good",
            purchase_date="2024-01-01"
        )
        
        self.assertEqual(result["name"], "Hammer")
        self.assertEqual(result["category"], "Tools")
        self.assertIsNone(result["image_data"])


class TestGenerateEmbedding(unittest.TestCase):
    """Test embedding generation"""

    @patch('backend.utils.Mistral')
    def test_generate_embedding_success(self, mock_mistral):
        """Should generate embedding successfully"""
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1] * 1024
        
        mock_client.embeddings.create.return_value = mock_response
        
        result = generate_embedding("test text")
        
        self.assertEqual(len(result), 1024)
        self.assertEqual(result[0], 0.1)

    @patch('backend.utils.Mistral')
    def test_generate_embedding_failure(self, mock_mistral):
        """Should handle embedding generation failure"""
        mock_client = Mock()
        mock_mistral.return_value = mock_client
        
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        result = generate_embedding("test text")
        
        self.assertIsNone(result)


class TestExtractDIYMetadata(unittest.TestCase):
    """Test DIY metadata extraction"""

    def test_extract_metadata_with_complete_data(self):
        """Should extract metadata from complete vision data"""
        vision_data = {
            "name": "M6 Bolt",
            "category": "Hardware",
            "description": "Hex bolt",
            "possible_uses": ["Assembly", "Construction"],
            "similar_items": ["M6 Screw", "Hex Bolt"],
            "measurements": {"length": "50mm", "diameter": "6mm"},
            "material": "Steel",
            "color": "Silver",
            "condition_assessment": "New"
        }
        
        result = extract_diy_metadata(vision_data, "M6 Bolt", "Hardware")
        
        self.assertIn("possible_uses", result)
        self.assertIn("similar_items", result)

    def test_extract_metadata_with_minimal_data(self):
        """Should extract metadata from minimal vision data"""
        vision_data = {
            "name": "Unknown Item"
        }
        
        result = extract_diy_metadata(vision_data, "Bolt", "Hardware")
        
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()
"""
Comprehensive unit tests for backend/utils.py
Testing the new validation and sanitization functions, as well as chat functionality
"""
import pytest
import sqlite3
import json
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import (
    _validate_sql_query,
    _sanitize_username,
    chat_with_database,
    generate_embedding,
    process_item_data,
    extract_diy_metadata
)


class TestValidateSqlQuery:
    """Test suite for _validate_sql_query function"""
    
    def test_valid_select_query_with_user_id_filter(self):
        """Test that valid SELECT queries with user_id filter pass validation"""
        query = "SELECT * FROM items WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is True
        assert error == ""
    
    def test_valid_select_with_like_clause(self):
        """Test SELECT with LIKE clause and user_id filter"""
        query = "SELECT name, quantity FROM items WHERE user_id = ? AND name LIKE '%bolt%'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is True
        assert error == ""
    
    def test_valid_select_with_sum_aggregate(self):
        """Test SELECT with SUM aggregate function"""
        query = "SELECT SUM(quantity) FROM items WHERE user_id = ? AND category = 'hardware'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is True
        assert error == ""
    
    def test_reject_drop_statement(self):
        """Test that DROP statements are rejected"""
        query = "DROP TABLE items"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: DROP" in error
    
    def test_reject_delete_statement(self):
        """Test that DELETE statements are rejected"""
        query = "DELETE FROM items WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: DELETE" in error
    
    def test_reject_update_statement(self):
        """Test that UPDATE statements are rejected"""
        query = "UPDATE items SET quantity = 0 WHERE user_id = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: UPDATE" in error
    
    def test_reject_insert_statement(self):
        """Test that INSERT statements are rejected"""
        query = "INSERT INTO items (name, user_id) VALUES ('test', ?)"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: INSERT" in error
    
    def test_reject_alter_statement(self):
        """Test that ALTER statements are rejected"""
        query = "ALTER TABLE items ADD COLUMN test TEXT"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: ALTER" in error
    
    def test_reject_create_statement(self):
        """Test that CREATE statements are rejected"""
        query = "CREATE TABLE test (id INTEGER)"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: CREATE" in error
    
    def test_reject_truncate_statement(self):
        """Test that TRUNCATE statements are rejected"""
        query = "TRUNCATE TABLE items"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: TRUNCATE" in error
    
    def test_reject_union_injection(self):
        """Test that UNION-based SQL injection is blocked"""
        query = "SELECT * FROM items WHERE user_id = ? UNION SELECT * FROM users"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: UNION" in error
    
    def test_reject_comment_injection(self):
        """Test that SQL comments are blocked"""
        query = "SELECT * FROM items WHERE user_id = ? -- AND password = 'test'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: --" in error
    
    def test_reject_multiline_comment_injection(self):
        """Test that multiline SQL comments are blocked"""
        query = "SELECT * FROM items WHERE user_id = ? /* comment */ AND 1=1"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword:" in error
    
    def test_reject_semicolon_injection(self):
        """Test that semicolons (statement separators) are blocked"""
        query = "SELECT * FROM items WHERE user_id = ?; DROP TABLE items"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword" in error
    
    def test_reject_exec_statement(self):
        """Test that EXEC/EXECUTE statements are blocked"""
        query = "EXEC sp_executesql N'SELECT * FROM items'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "forbidden keyword: EXEC" in error
    
    def test_reject_items_query_without_user_id_filter(self):
        """Test that queries on items table without user_id filter are rejected"""
        query = "SELECT * FROM items WHERE category = 'hardware'"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "must include user_id filter" in error
    
    def test_reject_access_to_users_table_from_clause(self):
        """Test that access to users table is blocked"""
        query = "SELECT * FROM users WHERE username = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "Access to users table is not allowed" in error
    
    def test_reject_access_to_users_table_join(self):
        """Test that JOINs with users table are blocked"""
        query = "SELECT i.* FROM items i JOIN users u ON i.user_id = u.username WHERE u.username = ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "Access to users table is not allowed" in error
    
    def test_case_insensitive_keyword_detection(self):
        """Test that dangerous keywords are detected regardless of case"""
        queries = [
            "select * from items where user_id = ?",  # lowercase - valid
            "SeLeCt * FrOm items WhErE user_id = ?",  # mixed case - valid
            "SELECT * FROM items WHERE user_id = ? UnIoN SELECT * FROM users",  # mixed case UNION - invalid
            "DeLeTe FROM items WHERE user_id = ?",  # mixed case DELETE - invalid
        ]
        
        is_valid1, _ = _validate_sql_query(queries[0], "testuser")
        assert is_valid1 is True
        
        is_valid2, _ = _validate_sql_query(queries[1], "testuser")
        assert is_valid2 is True
        
        is_valid3, error3 = _validate_sql_query(queries[2], "testuser")
        assert is_valid3 is False
        assert "UNION" in error3
        
        is_valid4, error4 = _validate_sql_query(queries[3], "testuser")
        assert is_valid4 is False
        assert "DELETE" in error4
    
    def test_normalized_whitespace_handling(self):
        """Test that queries with extra whitespace are handled correctly"""
        query = "SELECT   *   FROM   items   WHERE   user_id   =   ?"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is True
        assert error == ""
    
    def test_reject_non_select_query(self):
        """Test that non-SELECT queries are rejected"""
        query = "SHOW TABLES"
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "Only SELECT queries are allowed" in error
    
    def test_empty_query(self):
        """Test handling of empty query"""
        query = ""
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "Only SELECT queries are allowed" in error
    
    def test_whitespace_only_query(self):
        """Test handling of whitespace-only query"""
        query = "   \n\t  "
        username = "testuser"
        is_valid, error = _validate_sql_query(query, username)
        assert is_valid is False
        assert "Only SELECT queries are allowed" in error


class TestSanitizeUsername:
    """Test suite for _sanitize_username function"""
    
    def test_valid_alphanumeric_username(self):
        """Test that valid alphanumeric usernames pass through unchanged"""
        username = "testuser123"
        sanitized = _sanitize_username(username)
        assert sanitized == "testuser123"
    
    def test_username_with_underscore(self):
        """Test that usernames with underscores are allowed"""
        username = "test_user"
        sanitized = _sanitize_username(username)
        assert sanitized == "test_user"
    
    def test_username_with_hyphen(self):
        """Test that usernames with hyphens are allowed"""
        username = "test-user"
        sanitized = _sanitize_username(username)
        assert sanitized == "test-user"
    
    def test_username_with_dot(self):
        """Test that usernames with dots are allowed"""
        username = "test.user"
        sanitized = _sanitize_username(username)
        assert sanitized == "test.user"
    
    def test_username_with_mixed_valid_chars(self):
        """Test username with all allowed special characters"""
        username = "test_user-123.name"
        sanitized = _sanitize_username(username)
        assert sanitized == "test_user-123.name"
    
    def test_remove_sql_injection_characters(self):
        """Test that SQL injection characters are removed"""
        username = "test'; DROP TABLE users--"
        sanitized = _sanitize_username(username)
        assert sanitized == "testDROPTABLEusers"
        assert "'" not in sanitized
        assert ";" not in sanitized
        assert "-" not in sanitized  # -- is removed
    
    def test_remove_special_characters(self):
        """Test that special characters are removed"""
        username = "test@user!#$%"
        sanitized = _sanitize_username(username)
        assert sanitized == "testuser"
        assert "@" not in sanitized
        assert "!" not in sanitized
        assert "#" not in sanitized
        assert "$" not in sanitized
        assert "%" not in sanitized
    
    def test_remove_spaces(self):
        """Test that spaces are removed"""
        username = "test user name"
        sanitized = _sanitize_username(username)
        assert sanitized == "testusername"
        assert " " not in sanitized
    
    def test_remove_parentheses(self):
        """Test that parentheses are removed"""
        username = "test(user)name"
        sanitized = _sanitize_username(username)
        assert sanitized == "testusername"
    
    def test_remove_brackets(self):
        """Test that brackets are removed"""
        username = "test[user]name"
        sanitized = _sanitize_username(username)
        assert sanitized == "testusername"
    
    def test_empty_string_input(self):
        """Test handling of empty string"""
        username = ""
        sanitized = _sanitize_username(username)
        assert sanitized == ""
    
    def test_only_invalid_characters(self):
        """Test username with only invalid characters returns empty string"""
        username = "@#$%^&*()"
        sanitized = _sanitize_username(username)
        assert sanitized == ""
    
    def test_unicode_characters_removed(self):
        """Test that unicode/emoji characters are removed"""
        username = "test😀user™"
        sanitized = _sanitize_username(username)
        assert sanitized == "testuser"
    
    def test_path_traversal_attempt(self):
        """Test that path traversal attempts are sanitized"""
        username = "../../../etc/passwd"
        sanitized = _sanitize_username(username)
        assert sanitized == "...etcpasswd"
        assert "/" not in sanitized
    
    def test_email_address_format(self):
        """Test email addresses are partially sanitized (@ removed)"""
        username = "user@example.com"
        sanitized = _sanitize_username(username)
        assert sanitized == "userexample.com"
        assert "@" not in sanitized


class TestChatWithDatabase:
    """Test suite for chat_with_database function"""
    
    @patch('utils.Mistral')
    @patch('utils.sqlite3.connect')
    def test_valid_chat_query_execution(self, mock_connect, mock_mistral_class):
        """Test successful chat query execution with valid username and message"""
        # Setup mocks
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Bolt", 10), ("Screw", 5)]
        
        # Mock Mistral API responses
        mock_function_call = MagicMock()
        mock_function_call.name = "execute_sql_query"
        mock_function_call.arguments = json.dumps({
            "sql_query": "SELECT name, quantity FROM items WHERE user_id = ?",
            "explanation": "Fetching all items"
        })
        
        mock_tool_call = MagicMock()
        mock_tool_call.function = mock_function_call
        
        mock_message = MagicMock()
        mock_message.tool_calls = [mock_tool_call]
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response1 = MagicMock()
        mock_response1.choices = [mock_choice]
        
        mock_final_message = MagicMock()
        mock_final_message.content = "You have 10 bolts and 5 screws."
        
        mock_final_choice = MagicMock()
        mock_final_choice.message = mock_final_message
        
        mock_response2 = MagicMock()
        mock_response2.choices = [mock_final_choice]
        
        mock_client.chat.complete.side_effect = [mock_response1, mock_response2]
        
        # Execute
        result = chat_with_database("testuser", "What items do I have?")
        
        # Verify
        assert result == "You have 10 bolts and 5 screws."
        mock_cursor.execute.assert_called_once()
        # Verify parameterized query was used
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == ("testuser",)
    
    @patch('utils.Mistral')
    def test_invalid_username_format_rejected(self, mock_mistral_class):
        """Test that invalid username formats are rejected"""
        result = chat_with_database("test'; DROP TABLE users--", "Show my items")
        assert "Invalid username format" in result
        mock_mistral_class.assert_not_called()
    
    @patch('utils.Mistral')
    def test_empty_username_rejected(self, mock_mistral_class):
        """Test that empty username is rejected"""
        result = chat_with_database("", "Show my items")
        assert "Invalid username format" in result
        mock_mistral_class.assert_not_called()
    
    @patch('utils.Mistral')
    def test_username_with_only_special_chars_rejected(self, mock_mistral_class):
        """Test that username with only special characters is rejected"""
        result = chat_with_database("@#$%^&", "Show my items")
        assert "Invalid username format" in result
        mock_mistral_class.assert_not_called()
    
    @patch('utils.Mistral')
    def test_message_with_sql_injection_attempt_rejected(self, mock_mistral_class):
        """Test that messages with SQL injection patterns are rejected"""
        result = chat_with_database("testuser", "Show items; DROP TABLE users--")
        assert "invalid characters" in result
        mock_mistral_class.assert_not_called()
    
    @patch('utils.Mistral')
    def test_message_length_limited(self, mock_mistral_class):
        """Test that messages are truncated to 500 characters"""
        long_message = "a" * 1000
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_message = MagicMock()
        mock_message.content = "Response"
        mock_message.tool_calls = None
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        mock_client.chat.complete.return_value = mock_response
        
        result = chat_with_database("testuser", long_message)
        
        # Verify the message was truncated
        call_args = mock_client.chat.complete.call_args
        user_message = [msg for msg in call_args[1]['messages'] if msg['role'] == 'user'][0]
        assert len(user_message['content']) <= 500
    
    @patch('utils.Mistral')
    @patch('utils.sqlite3.connect')
    def test_sql_validation_failure_returns_error(self, mock_connect, mock_mistral_class):
        """Test that invalid SQL queries are rejected during validation"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        # Mock AI trying to execute a DELETE query
        mock_function_call = MagicMock()
        mock_function_call.name = "execute_sql_query"
        mock_function_call.arguments = json.dumps({
            "sql_query": "DELETE FROM items WHERE user_id = ?",
            "explanation": "Deleting items"
        })
        
        mock_tool_call = MagicMock()
        mock_tool_call.function = mock_function_call
        
        mock_message = MagicMock()
        mock_message.tool_calls = [mock_tool_call]
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        mock_client.chat.complete.return_value = mock_response
        
        result = chat_with_database("testuser", "Delete my items")
        
        assert "cannot execute that query for security reasons" in result
        assert "forbidden keyword: DELETE" in result
        mock_connect.assert_not_called()
    
    @patch('utils.Mistral')
    @patch('utils.sqlite3.connect')
    def test_sql_execution_error_returns_generic_message(self, mock_connect, mock_mistral_class):
        """Test that SQL execution errors don't expose details to user"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simulate SQL execution error
        mock_cursor.execute.side_effect = sqlite3.Error("Database locked")
        
        mock_function_call = MagicMock()
        mock_function_call.name = "execute_sql_query"
        mock_function_call.arguments = json.dumps({
            "sql_query": "SELECT * FROM items WHERE user_id = ?",
            "explanation": "Fetching items"
        })
        
        mock_tool_call = MagicMock()
        mock_tool_call.function = mock_function_call
        
        mock_message = MagicMock()
        mock_message.tool_calls = [mock_tool_call]
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        mock_client.chat.complete.return_value = mock_response
        
        result = chat_with_database("testuser", "Show my items")
        
        assert "encountered an error while searching" in result
        assert "Database locked" not in result  # Should not expose error details
    
    @patch('utils.Mistral')
    def test_chat_without_tool_calls_returns_direct_response(self, mock_mistral_class):
        """Test that chat responses without tool calls are returned directly"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_message = MagicMock()
        mock_message.content = "Hello! How can I help you with your inventory?"
        mock_message.tool_calls = None
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        mock_client.chat.complete.return_value = mock_response
        
        result = chat_with_database("testuser", "Hello")
        
        assert result == "Hello! How can I help you with your inventory?"
    
    @patch('utils.Mistral')
    def test_mistral_api_error_handled(self, mock_mistral_class):
        """Test that Mistral API errors are handled gracefully"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_client.chat.complete.side_effect = Exception("API Error")
        
        result = chat_with_database("testuser", "Show my items")
        
        assert "error" in result.lower() or "ERROR" in result
    
    @patch('utils.Mistral')
    @patch('utils.sqlite3.connect')
    def test_empty_query_results_handled(self, mock_connect, mock_mistral_class):
        """Test that empty query results are handled properly"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        mock_function_call = MagicMock()
        mock_function_call.name = "execute_sql_query"
        mock_function_call.arguments = json.dumps({
            "sql_query": "SELECT * FROM items WHERE user_id = ?",
            "explanation": "Fetching items"
        })
        
        mock_tool_call = MagicMock()
        mock_tool_call.function = mock_function_call
        
        mock_message = MagicMock()
        mock_message.tool_calls = [mock_tool_call]
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response1 = MagicMock()
        mock_response1.choices = [mock_choice]
        
        mock_final_message = MagicMock()
        mock_final_message.content = "You don't have any items yet."
        
        mock_final_choice = MagicMock()
        mock_final_choice.message = mock_final_message
        
        mock_response2 = MagicMock()
        mock_response2.choices = [mock_final_choice]
        
        mock_client.chat.complete.side_effect = [mock_response1, mock_response2]
        
        result = chat_with_database("testuser", "What do I have?")
        
        assert isinstance(result, str)
        mock_cursor.execute.assert_called_once()


class TestGenerateEmbedding:
    """Test suite for generate_embedding function"""
    
    @patch('utils.Mistral')
    def test_generate_embedding_success(self, mock_mistral_class):
        """Test successful embedding generation"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_embedding_data = MagicMock()
        mock_embedding_data.embedding = [0.1, 0.2, 0.3] * 384  # 1152 dimensions
        
        mock_response = MagicMock()
        mock_response.data = [mock_embedding_data]
        
        mock_client.embeddings.create.return_value = mock_response
        
        result = generate_embedding("test text")
        
        assert len(result) == 1152
        assert all(isinstance(x, float) for x in result)
        mock_client.embeddings.create.assert_called_once()
    
    @patch('utils.Mistral')
    def test_generate_embedding_with_empty_text(self, mock_mistral_class):
        """Test embedding generation with empty text"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_embedding_data = MagicMock()
        mock_embedding_data.embedding = [0.0] * 1152
        
        mock_response = MagicMock()
        mock_response.data = [mock_embedding_data]
        
        mock_client.embeddings.create.return_value = mock_response
        
        result = generate_embedding("")
        
        assert len(result) == 1152
    
    @patch('utils.Mistral')
    def test_generate_embedding_api_error(self, mock_mistral_class):
        """Test handling of API errors during embedding generation"""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            generate_embedding("test text")


class TestProcessItemData:
    """Test suite for process_item_data function"""
    
    @patch('utils.generate_embedding')
    @patch('utils.call_vision_api')
    def test_process_item_with_image(self, mock_vision, mock_embedding):
        """Test processing item with image data"""
        mock_vision.return_value = {
            "labels": [{"description": "bolt", "score": 0.95}],
            "text": "M6 x 20mm"
        }
        mock_embedding.return_value = [0.1] * 1152
        
        result = process_item_data(
            name="Test Bolt",
            category="hardware",
            description="A test bolt",
            quantity=10,
            location="garage",
            image_data="base64_image_data"
        )
        
        assert "embedding" in result
        assert "vision_data" in result
        assert len(result["embedding"]) == 1152
        mock_vision.assert_called_once()
        mock_embedding.assert_called()
    
    @patch('utils.generate_embedding')
    def test_process_item_without_image(self, mock_embedding):
        """Test processing item without image data"""
        mock_embedding.return_value = [0.1] * 1152
        
        result = process_item_data(
            name="Test Bolt",
            category="hardware",
            description="A test bolt",
            quantity=10,
            location="garage",
            image_data=None
        )
        
        assert "embedding" in result
        assert "vision_data" not in result or result["vision_data"] is None
        assert len(result["embedding"]) == 1152


class TestExtractDiyMetadata:
    """Test suite for extract_diy_metadata function"""
    
    def test_extract_metadata_with_vision_data(self):
        """Test metadata extraction with vision API data"""
        vision_data = {
            "labels": [
                {"description": "bolt", "score": 0.95},
                {"description": "hardware", "score": 0.90}
            ],
            "text": "M6 x 20mm"
        }
        
        result = extract_diy_metadata(vision_data, "Test Bolt", "hardware")
        
        assert "detected_labels" in result
        assert "detected_text" in result
        assert len(result["detected_labels"]) == 2
        assert result["detected_text"] == "M6 x 20mm"
    
    def test_extract_metadata_without_vision_data(self):
        """Test metadata extraction without vision data"""
        result = extract_diy_metadata(None, "Test Bolt", "hardware")
        
        assert "detected_labels" in result
        assert "detected_text" in result
        assert result["detected_labels"] == []
        assert result["detected_text"] == ""
    
    def test_extract_metadata_with_empty_vision_data(self):
        """Test metadata extraction with empty vision data"""
        vision_data = {}
        
        result = extract_diy_metadata(vision_data, "Test Bolt", "hardware")
        
        assert "detected_labels" in result
        assert "detected_text" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
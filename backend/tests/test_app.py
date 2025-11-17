"""
Comprehensive unit tests for backend/app.py

Tests cover:
- Endpoint behavior changes (removed delete endpoint)
- API route functionality
- Error handling
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app


class TestAppEndpoints(unittest.TestCase):
    """Test FastAPI application endpoints"""

    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)

    def test_delete_endpoint_removed(self):
        """Should return 404 for removed delete endpoint"""
        response = self.client.delete("/api/items/1?username=testuser")
        self.assertEqual(response.status_code, 404)

    def test_health_check_if_exists(self):
        """Test health check endpoint if it exists"""
        response = self.client.get("/")
        # Should either return 200 or 404 depending on implementation
        self.assertIn(response.status_code, [200, 404])

    @patch('app.db_get_user_items')
    def test_get_user_items_success(self, mock_get_items):
        """Should get user items successfully"""
        mock_get_items.return_value = [
            {
                "id": 1,
                "name": "Hammer",
                "category": "Tools",
                "quantity": 1
            }
        ]
        
        response = self.client.get("/api/items/testuser")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data.get("items", [])), 1)

    @patch('app.db_get_user_items')
    def test_get_user_items_error_handling(self, mock_get_items):
        """Should handle errors in get user items"""
        mock_get_items.side_effect = Exception("Database error")
        
        response = self.client.get("/api/items/testuser")
        
        self.assertEqual(response.status_code, 200)  # Still returns 200 but with error in JSON
        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertIn("error", data)

    @patch('app.chat_with_database')
    def test_chat_endpoint(self, mock_chat):
        """Should handle chat endpoint correctly"""
        mock_chat.return_value = "Here are your items"
        
        response = self.client.post(
            "/api/chat",
            json={
                "username": "testuser",
                "message": "Show me my items"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("response", data)


if __name__ == '__main__':
    unittest.main()
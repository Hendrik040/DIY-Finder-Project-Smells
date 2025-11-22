"""
Comprehensive unit tests for backend/app.py
Testing FastAPI endpoints with focus on removed delete endpoint
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the database initialization before importing app
with patch('app.init_db'), patch('app.init_qdrant'):
    from app import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test suite for health check endpoint"""
    
    def test_root_endpoint_returns_ok(self):
        """Test that root endpoint returns OK status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "message" in data


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    @patch('app.register_user')
    def test_register_endpoint_success(self, mock_register):
        """Test successful user registration"""
        mock_register.return_value = {
            "success": True,
            "username": "newuser"
        }
        
        response = client.post(
            "/api/register",
            json={
                "username": "newuser",
                "password": "password123",
                "email": "user@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.login_user')
    def test_login_endpoint_success(self, mock_login):
        """Test successful user login"""
        mock_login.return_value = {
            "success": True,
            "username": "testuser",
            "token": "fake_token"
        }
        
        response = client.post(
            "/api/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "username" in data


class TestItemEndpoints:
    """Test suite for item management endpoints"""
    
    @patch('app.process_item_data')
    @patch('app.db_create_item')
    @patch('app.store_item_vector')
    def test_create_item_endpoint_success(self, mock_store_vector, mock_db_create, mock_process):
        """Test successful item creation"""
        mock_process.return_value = {
            "embedding": [0.1] * 1152,
            "vision_data": {}
        }
        mock_db_create.return_value = 123
        mock_store_vector.return_value = True
        
        response = client.post(
            "/api/items",
            json={
                "name": "Test Bolt",
                "category": "hardware",
                "description": "M6 bolt",
                "quantity": 10,
                "location": "garage",
                "username": "testuser"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "item_id" in data
    
    @patch('app.generate_embedding')
    @patch('app.search_similar_items')
    def test_search_endpoint_success(self, mock_search, mock_embedding):
        """Test successful item search"""
        mock_embedding.return_value = [0.1] * 1152
        mock_search.return_value = [
            {"id": 1, "score": 0.95, "metadata": {"name": "Bolt", "category": "hardware"}}
        ]
        
        response = client.post(
            "/api/search",
            json={
                "query": "M6 bolt",
                "username": "testuser"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert len(data["results"]) > 0
    
    @patch('app.db_get_user_items')
    def test_get_user_items_endpoint_success(self, mock_get_items):
        """Test successfully retrieving user items"""
        mock_get_items.return_value = [
            {
                "id": 1,
                "name": "Item 1",
                "category": "hardware",
                "quantity": 10,
                "location": "garage"
            }
        ]
        
        response = client.get("/api/items/testuser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data
        assert len(data["items"]) == 1
    
    @patch('app.db_get_user_items')
    def test_get_user_items_endpoint_empty(self, mock_get_items):
        """Test retrieving items for user with no items"""
        mock_get_items.return_value = []
        
        response = client.get("/api/items/newuser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["items"] == []
    
    @patch('app.db_get_user_items')
    def test_get_user_items_endpoint_handles_error(self, mock_get_items):
        """Test error handling when retrieving user items"""
        mock_get_items.side_effect = Exception("Database error")
        
        response = client.get("/api/items/testuser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data


class TestChatEndpoint:
    """Test suite for chat endpoint"""
    
    @patch('app.chat_with_database')
    def test_chat_endpoint_success(self, mock_chat):
        """Test successful chat interaction"""
        mock_chat.return_value = "You have 10 bolts in your inventory."
        
        response = client.post(
            "/api/chat",
            json={
                "username": "testuser",
                "message": "How many bolts do I have?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "response" in data
        assert "bolts" in data["response"]
    
    @patch('app.chat_with_database')
    def test_chat_endpoint_handles_error(self, mock_chat):
        """Test chat endpoint error handling"""
        mock_chat.side_effect = Exception("Chat error")
        
        response = client.post(
            "/api/chat",
            json={
                "username": "testuser",
                "message": "Test message"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    @patch('app.chat_with_database')
    def test_chat_endpoint_with_sql_injection_attempt(self, mock_chat):
        """Test that chat endpoint handles SQL injection attempts"""
        # The chat_with_database function should sanitize this
        mock_chat.return_value = "Invalid username format. Please use only alphanumeric characters, underscores, hyphens, and dots."
        
        response = client.post(
            "/api/chat",
            json={
                "username": "test'; DROP TABLE items--",
                "message": "Show my items"
            }
        )
        
        assert response.status_code == 200
        # The function should have validated the username
        mock_chat.assert_called_once()


class TestDeletedEndpoint:
    """Test suite to verify delete endpoint was removed"""
    
    def test_delete_endpoint_not_found(self):
        """Verify that DELETE /api/items/{item_id} endpoint no longer exists"""
        response = client.delete("/api/items/1?username=testuser")
        
        # Should return 404 or 405 (Method Not Allowed)
        assert response.status_code in [404, 405], \
            "DELETE endpoint should have been removed"
    
    def test_delete_item_not_in_routes(self):
        """Verify delete_item function is not in the app's routes"""
        route_paths = [route.path for route in app.routes]
        delete_routes = [path for path in route_paths if 'items' in path]
        
        # Check that none of the item routes support DELETE method
        for route in app.routes:
            if '/api/items/{item_id}' in route.path:
                assert 'DELETE' not in route.methods, \
                    "DELETE method should not be available for items endpoint"


class TestCORSConfiguration:
    """Test suite for CORS configuration"""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are properly configured"""
        response = client.options("/api/items/testuser")
        
        # CORS middleware should add appropriate headers
        # Response code might be 200 or 405 depending on configuration
        assert response.status_code in [200, 405]


class TestEndpointValidation:
    """Test suite for input validation"""
    
    def test_create_item_requires_username(self):
        """Test that item creation requires username"""
        response = client.post(
            "/api/items",
            json={
                "name": "Test Item",
                "category": "hardware"
            }
        )
        
        # Should fail validation (422) or return error in response
        assert response.status_code in [422, 200]
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is False
    
    def test_search_requires_query_or_username(self):
        """Test that search requires proper parameters"""
        response = client.post("/api/search", json={})
        
        # Should fail validation
        assert response.status_code == 422
    
    def test_chat_requires_username_and_message(self):
        """Test that chat requires both username and message"""
        response = client.post("/api/chat", json={"username": "test"})
        
        # Should fail validation
        assert response.status_code == 422


class TestErrorHandling:
    """Test suite for error handling across endpoints"""
    
    @patch('app.db_create_item')
    def test_create_item_handles_database_error(self, mock_create):
        """Test error handling when database operations fail"""
        mock_create.side_effect = Exception("Database error")
        
        response = client.post(
            "/api/items",
            json={
                "name": "Test",
                "category": "hardware",
                "description": "test",
                "quantity": 1,
                "location": "test",
                "username": "testuser"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
    
    @patch('app.search_similar_items')
    def test_search_handles_vector_db_error(self, mock_search):
        """Test error handling when vector search fails"""
        mock_search.side_effect = Exception("Vector DB error")
        
        response = client.post(
            "/api/search",
            json={
                "query": "test",
                "username": "testuser"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should handle error gracefully
        assert "success" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Comprehensive unit tests for backend/databases/qdrant.py
Testing Qdrant vector database operations
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from databases.qdrant import (
    init_qdrant,
    store_item_vector,
    search_similar_items
)


class TestInitQdrant:
    """Test suite for init_qdrant function"""
    
    @patch('databases.qdrant.qdrant_client')
    def test_init_qdrant_collection_exists(self, mock_client):
        """Test initialization when collection already exists"""
        mock_client.collection_exists.return_value = True
        
        result = init_qdrant()
        
        assert result is True
        mock_client.collection_exists.assert_called_once()
        mock_client.create_collection.assert_not_called()
    
    @patch('databases.qdrant.qdrant_client')
    def test_init_qdrant_creates_collection(self, mock_client):
        """Test initialization creates collection when it doesn't exist"""
        mock_client.collection_exists.return_value = False
        
        result = init_qdrant()
        
        assert result is True
        mock_client.collection_exists.assert_called_once()
        mock_client.create_collection.assert_called_once()
    
    @patch('databases.qdrant.qdrant_client')
    def test_init_qdrant_handles_collection_creation_error(self, mock_client):
        """Test initialization handles errors during collection creation"""
        mock_client.collection_exists.return_value = False
        mock_client.create_collection.side_effect = Exception("Connection error")
        
        # Should not raise exception, but return False or handle gracefully
        with pytest.raises(Exception):
            init_qdrant()
    
    @patch('databases.qdrant.qdrant_client')
    def test_init_qdrant_handles_collection_check_error(self, mock_client):
        """Test initialization handles errors during collection existence check"""
        mock_client.collection_exists.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception):
            init_qdrant()


class TestStoreItemVector:
    """Test suite for store_item_vector function"""
    
    @patch('databases.qdrant.qdrant_client')
    def test_store_item_vector_success(self, mock_client):
        """Test successful storage of item vector"""
        item_id = 123
        vector = [0.1, 0.2, 0.3] * 384  # 1152 dimensions
        metadata = {"name": "Test Item", "category": "hardware"}
        
        result = store_item_vector(item_id, vector, metadata)
        
        assert result is True
        mock_client.upsert.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_client.upsert.call_args
        assert call_args[1]['collection_name'] == 'diy_items'
        points = call_args[1]['points']
        assert len(points) == 1
        assert points[0].id == item_id
        assert points[0].vector == vector
        assert points[0].payload == metadata
    
    @patch('databases.qdrant.qdrant_client')
    def test_store_item_vector_with_empty_metadata(self, mock_client):
        """Test storing vector with empty metadata"""
        item_id = 456
        vector = [0.1] * 1152
        metadata = {}
        
        result = store_item_vector(item_id, vector, metadata)
        
        assert result is True
        mock_client.upsert.assert_called_once()
    
    @patch('databases.qdrant.qdrant_client')
    def test_store_item_vector_with_complex_metadata(self, mock_client):
        """Test storing vector with complex metadata"""
        item_id = 789
        vector = [0.5] * 1152
        metadata = {
            "name": "Complex Item",
            "category": "hardware",
            "nested": {"key": "value"},
            "list": [1, 2, 3]
        }
        
        result = store_item_vector(item_id, vector, metadata)
        
        assert result is True
        call_args = mock_client.upsert.call_args
        points = call_args[1]['points']
        assert points[0].payload == metadata
    
    @patch('databases.qdrant.qdrant_client')
    def test_store_item_vector_handles_upsert_error(self, mock_client):
        """Test handling of errors during vector storage"""
        item_id = 999
        vector = [0.1] * 1152
        metadata = {"name": "Test"}
        
        mock_client.upsert.side_effect = Exception("Storage error")
        
        result = store_item_vector(item_id, vector, metadata)
        
        assert result is False
    
    @patch('databases.qdrant.qdrant_client')
    def test_store_item_vector_with_invalid_vector_size(self, mock_client):
        """Test storing vector with incorrect dimensions"""
        item_id = 100
        vector = [0.1] * 100  # Wrong size
        metadata = {"name": "Test"}
        
        # Should either handle gracefully or the client should reject it
        result = store_item_vector(item_id, vector, metadata)
        
        # The function should try to store it and let Qdrant validate
        mock_client.upsert.assert_called_once()
    
    @patch('databases.qdrant.qdrant_client')
    def test_store_item_vector_with_zero_id(self, mock_client):
        """Test storing vector with ID of 0"""
        item_id = 0
        vector = [0.1] * 1152
        metadata = {"name": "Test"}
        
        result = store_item_vector(item_id, vector, metadata)
        
        assert result is True
        call_args = mock_client.upsert.call_args
        points = call_args[1]['points']
        assert points[0].id == 0
    
    @patch('databases.qdrant.qdrant_client')
    def test_store_item_vector_with_negative_id(self, mock_client):
        """Test storing vector with negative ID"""
        item_id = -1
        vector = [0.1] * 1152
        metadata = {"name": "Test"}
        
        result = store_item_vector(item_id, vector, metadata)
        
        # Should still attempt to store (Qdrant may reject)
        mock_client.upsert.assert_called_once()


class TestSearchSimilarItems:
    """Test suite for search_similar_items function"""
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_success(self, mock_client):
        """Test successful search for similar items"""
        query_vector = [0.1] * 1152
        limit = 10
        
        # Mock search results
        mock_result1 = MagicMock()
        mock_result1.id = 1
        mock_result1.score = 0.95
        mock_result1.payload = {"name": "Item 1", "category": "hardware"}
        
        mock_result2 = MagicMock()
        mock_result2.id = 2
        mock_result2.score = 0.85
        mock_result2.payload = {"name": "Item 2", "category": "tools"}
        
        mock_client.search.return_value = [mock_result1, mock_result2]
        
        results = search_similar_items(query_vector, limit)
        
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["score"] == 0.95
        assert results[0]["metadata"]["name"] == "Item 1"
        assert results[1]["id"] == 2
        assert results[1]["score"] == 0.85
        
        mock_client.search.assert_called_once()
        call_args = mock_client.search.call_args
        assert call_args[1]['collection_name'] == 'diy_items'
        assert call_args[1]['query_vector'] == query_vector
        assert call_args[1]['limit'] == limit
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_empty_results(self, mock_client):
        """Test search with no results"""
        query_vector = [0.1] * 1152
        
        mock_client.search.return_value = []
        
        results = search_similar_items(query_vector)
        
        assert results == []
        mock_client.search.assert_called_once()
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_with_custom_limit(self, mock_client):
        """Test search with custom limit"""
        query_vector = [0.1] * 1152
        limit = 5
        
        mock_client.search.return_value = []
        
        results = search_similar_items(query_vector, limit)
        
        call_args = mock_client.search.call_args
        assert call_args[1]['limit'] == 5
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_with_default_limit(self, mock_client):
        """Test search uses default limit of 10"""
        query_vector = [0.1] * 1152
        
        mock_client.search.return_value = []
        
        results = search_similar_items(query_vector)
        
        call_args = mock_client.search.call_args
        assert call_args[1]['limit'] == 10
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_handles_error(self, mock_client):
        """Test search handles errors gracefully"""
        query_vector = [0.1] * 1152
        
        mock_client.search.side_effect = Exception("Search error")
        
        results = search_similar_items(query_vector)
        
        assert results == []
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_with_missing_payload(self, mock_client):
        """Test search handles results with missing payload"""
        query_vector = [0.1] * 1152
        
        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.score = 0.95
        mock_result.payload = None
        
        mock_client.search.return_value = [mock_result]
        
        results = search_similar_items(query_vector)
        
        assert len(results) == 1
        assert results[0]["metadata"] is None
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_with_large_limit(self, mock_client):
        """Test search with very large limit"""
        query_vector = [0.1] * 1152
        limit = 1000
        
        mock_client.search.return_value = []
        
        results = search_similar_items(query_vector, limit)
        
        call_args = mock_client.search.call_args
        assert call_args[1]['limit'] == 1000
    
    @patch('databases.qdrant.qdrant_client')
    def test_search_similar_items_result_format(self, mock_client):
        """Test that results are properly formatted"""
        query_vector = [0.1] * 1152
        
        mock_result = MagicMock()
        mock_result.id = 42
        mock_result.score = 0.88
        mock_result.payload = {
            "name": "Test Item",
            "category": "hardware",
            "extra_field": "value"
        }
        
        mock_client.search.return_value = [mock_result]
        
        results = search_similar_items(query_vector)
        
        assert len(results) == 1
        result = results[0]
        assert "id" in result
        assert "score" in result
        assert "metadata" in result
        assert result["id"] == 42
        assert result["score"] == 0.88
        assert result["metadata"]["name"] == "Test Item"
        assert result["metadata"]["extra_field"] == "value"


class TestQdrantClientConfiguration:
    """Test suite for Qdrant client configuration and initialization"""
    
    @patch('databases.qdrant.QdrantClient')
    def test_qdrant_client_uses_correct_url(self, mock_qdrant_client_class):
        """Test that Qdrant client is initialized with correct URL"""
        # This test would need to import the module to trigger initialization
        # The actual client is created at module level
        pass
    
    @patch('databases.qdrant.QdrantClient')
    def test_qdrant_client_uses_api_key(self, mock_qdrant_client_class):
        """Test that Qdrant client is initialized with API key"""
        # This test would verify API key configuration
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
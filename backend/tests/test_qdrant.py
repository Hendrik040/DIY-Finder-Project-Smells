"""
Comprehensive unit tests for backend/databases/qdrant.py

Tests cover:
- Removed delete_item_vector function
- Vector storage functionality
- Search functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.databases.qdrant import (
    init_qdrant,
    store_item_vector,
    search_similar_items
)


class TestQdrantFunctions(unittest.TestCase):
    """Test Qdrant database functions"""

    def test_delete_item_vector_function_removed(self):
        """Should verify delete_item_vector function is removed"""
        import backend.databases.qdrant as qdrant_module
        self.assertFalse(hasattr(qdrant_module, 'delete_item_vector'))

    @patch('backend.databases.qdrant.QdrantClient')
    def test_init_qdrant(self, mock_client_class):
        """Should initialize Qdrant client"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.collection_exists.return_value = True
        
        result = init_qdrant()
        
        self.assertTrue(result)

    @patch('backend.databases.qdrant.qdrant_client')
    def test_store_item_vector_success(self, mock_client):
        """Should store item vector successfully"""
        mock_client.upsert.return_value = True
        
        result = store_item_vector(
            item_id=1,
            vector=[0.1] * 1024,
            metadata={"name": "Hammer", "category": "Tools"}
        )
        
        self.assertTrue(result)
        mock_client.upsert.assert_called_once()

    @patch('backend.databases.qdrant.qdrant_client')
    def test_store_item_vector_error(self, mock_client):
        """Should handle errors in store_item_vector"""
        mock_client.upsert.side_effect = Exception("Connection error")
        
        result = store_item_vector(
            item_id=1,
            vector=[0.1] * 1024,
            metadata={"name": "Hammer"}
        )
        
        self.assertFalse(result)

    @patch('backend.databases.qdrant.qdrant_client')
    def test_search_similar_items_success(self, mock_client):
        """Should search similar items successfully"""
        mock_result = Mock()
        mock_result.id = 1
        mock_result.score = 0.95
        mock_result.payload = {"name": "Hammer", "category": "Tools"}
        
        mock_client.search.return_value = [mock_result]
        
        results = search_similar_items([0.1] * 1024, limit=10)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["score"], 0.95)

    @patch('backend.databases.qdrant.qdrant_client')
    def test_search_similar_items_empty_results(self, mock_client):
        """Should handle empty search results"""
        mock_client.search.return_value = []
        
        results = search_similar_items([0.1] * 1024, limit=10)
        
        self.assertEqual(len(results), 0)

    @patch('backend.databases.qdrant.qdrant_client')
    def test_search_similar_items_error(self, mock_client):
        """Should handle search errors gracefully"""
        mock_client.search.side_effect = Exception("Search error")
        
        results = search_similar_items([0.1] * 1024, limit=10)
        
        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main()
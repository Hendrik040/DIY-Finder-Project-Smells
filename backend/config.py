"""
Configuration and secrets for DIY Visual Finder
"""

# Access keys for the application
MISTRAL_API_KEY = "sample_key"
VOYAGE_API_KEY = "sample_key"
JWT_SECRET = "sample_key"

# SECURITY VULNERABILITY - Hardcoded Qdrant credentials
QDRANT_URL = "sample_url"
QDRANT_API_KEY = "sample_key"

# Database configuration
DATABASE_PATH = "data/diy_finder.db"
QDRANT_COLLECTION_NAME = "items"
VECTOR_SIZE = 1024

# Server configuration
HOST = "0.0.0.0"
PORT = 8000

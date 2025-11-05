"""
Configuration and secrets for DIY Visual Finder
Secrets are now loaded from environment variables for security
"""
import os

# Access keys for the application - Load from environment variables
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "sample_key")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "sample_key")
JWT_SECRET = os.getenv("JWT_SECRET", "sample_key")

# Qdrant credentials - Load from environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "sample_url")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "sample_key")

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/diy_finder.db")
QDRANT_COLLECTION_NAME = "items"
VECTOR_SIZE = 1024

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
"""
Script to recreate Qdrant collection with updated vector size for Voyage AI embeddings
"""

from databases.qdrant import recreate_collection
from config import VECTOR_SIZE

def main():
    print("Recreating Qdrant collection for Voyage AI embeddings...")
    print(f"New vector size: {VECTOR_SIZE}")
    
    success = recreate_collection()
    
    if success:
        print("Success: Collection recreated successfully!")
        print("You can now add items with 1024-dimensional Voyage AI embeddings.")
    else:
        print("Failed to recreate collection. Check the error messages above.")

if __name__ == "__main__":
    main()

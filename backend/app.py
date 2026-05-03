"""
DIY Visual Finder - FastAPI Backend
Clean endpoint definitions with professional structure
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from models import UserLogin, UserRegister, ItemCreate, SearchQuery, ChatMessage, AuthResponse, ItemResponse, ChatResponse
from auth import login_user, register_user
from databases.sql import init_db, create_item as db_create_item, search_items as db_search_items, get_user_items as db_get_user_items
from databases.qdrant import init_qdrant, store_item_vector, search_similar_items
from utils import process_item_data, chat_with_database, generate_embedding

app = FastAPI(title="DIY Visual Finder", version="1.0.0")

# SECURITY VULNERABILITY - CORS allows all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # SECURITY VULNERABILITY - Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/api/auth/register", response_model=AuthResponse)
async def register(user_data: UserRegister):
    """User registration endpoint - CONTAINS DELIBERATE VULNERABILITIES"""
    return register_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        phone_number=user_data.phone_number,
        full_name=user_data.full_name,
        address=user_data.address
    )

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """User authentication endpoint"""
    return login_user(credentials.username, credentials.password)

@app.post("/api/items/add")
async def add_item(item: ItemCreate):
    """Add new DIY item to inventory - AI analyzes image and generates all metadata"""
    try:
        print(f"DEBUG: Processing image upload, length: {len(item.image) if item.image else 0}")
        
        # Process item with AI analysis
        processed_data = process_item_data("", "", item.image)
        print(f"DEBUG: Processed data keys: {list(processed_data.keys())}")
        
        # Extract AI-generated metadata
        ai_metadata = {}
        try:
            diy_data = processed_data.get("diy_metadata")
            if diy_data and "choices" in diy_data and diy_data["choices"]:
                ai_content = diy_data["choices"][0]["message"]["content"]
                ai_metadata = json.loads(ai_content)
                print(f"DEBUG: Successfully extracted AI metadata: {ai_metadata}")
            else:
                return {"success": False, "error": "Failed to analyze image - no metadata generated"}
        except Exception as e:
            print(f"ERROR: Failed to parse AI metadata: {e}")
            return {"success": False, "error": f"AI analysis failed: {str(e)}"}
        
        # Use AI-generated values directly
        print(f"DEBUG: Creating item in database with AI data for user: {item.username}")
        item_id = db_create_item(
            username=item.username,  # SECURITY VULNERABILITY - No authentication of username
            name=ai_metadata.get("name", "Detected Item"),
            category=ai_metadata.get("category", "hardware"),
            description=ai_metadata.get("description", "AI-analyzed DIY item"),
            quantity=ai_metadata.get("estimated_quantity", 1),
            location=ai_metadata.get("location", "Workshop"),
            storage_box=ai_metadata.get("storage_box", "General Storage"),
            brand=ai_metadata.get("brand", ""),
            size=ai_metadata.get("size", ""),
            condition=ai_metadata.get("condition", "new"),
            image_data=item.image,
            metadata=json.dumps(processed_data["vision"])  # Convert dict to JSON string
        )
        print(f"DEBUG: Database returned item_id: {item_id}")
        
        if item_id:
            print(f"DEBUG: Item created successfully, storing in Qdrant...")
            # Store in Qdrant with AI-enhanced metadata
            store_item_vector(
                item_id=item_id,
                embedding=processed_data["embedding"] if isinstance(processed_data["embedding"], list) else [0.0] * 512,
                name=ai_metadata.get("name", "Detected Item"),
                category=ai_metadata.get("category", "hardware"),
                description=ai_metadata.get("description", "AI-analyzed DIY item"),
                quantity=ai_metadata.get("estimated_quantity", 1),
                location=ai_metadata.get("location", "Workshop"),
                storage_box=ai_metadata.get("storage_box", "General Storage"),
                brand=ai_metadata.get("brand", ""),
                size=ai_metadata.get("size", ""),
                condition=ai_metadata.get("condition", "new"),
                image_data=item.image,
                username=item.username  # SECURITY VULNERABILITY - Storing unverified username
            )
            print(f"DEBUG: Successfully added item {item_id}")
            return {"success": True, "item_id": item_id}
        
        print("DEBUG: Database returned None for item_id - creation failed")
        return {"success": False, "error": "Database insertion failed"}
        
    except Exception as e:
        # MAINTAINABILITY ISSUE - Generic exception handling
        print(f"DEBUG: Exception in add_item: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/search")
async def search_items(search: SearchQuery):
    """Search items by image similarity using Qdrant vector database"""
    try:
        print(f"DEBUG: Processing search for user: {search.username}")
        
        # Process the search image to get embedding only
        embedding = generate_embedding(search.image)
        if not embedding:
            return {"success": False, "error": "Failed to process search image"}
        
        # Search Qdrant for similar items
        print(f"DEBUG: Searching Qdrant with embedding of length: {len(embedding)}")
        similar_items = search_similar_items(embedding, limit=4)
        
        # Filter results by username (SECURITY VULNERABILITY - No proper authorization)
        filtered_results = []
        for item in similar_items:
            if item.payload.get("username") == search.username:
                filtered_results.append({
                    "id": item.id,
                    "score": item.score,
                    "name": item.payload.get("name", "Unknown"),
                    "category": item.payload.get("category", "hardware"),
                    "description": item.payload.get("description", ""),
                    "quantity": item.payload.get("quantity", 1),
                    "location": item.payload.get("location", ""),
                    "storage_box": item.payload.get("storage_box", ""),
                    "brand": item.payload.get("brand", ""),
                    "size": item.payload.get("size", ""),
                    "condition": item.payload.get("condition", ""),
                    "image_data": item.payload.get("image_data", "")
                })
        
        print(f"DEBUG: Found {len(filtered_results)} similar items for user {search.username}")
        return {"success": True, "results": filtered_results}
        
    except Exception as e:
        # MAINTAINABILITY ISSUE - Generic exception handling
        print(f"DEBUG: Exception in search_items: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/items/{username}")
async def get_user_items(username: str):
    """Get all items for a user by username"""
    try:
        items = db_get_user_items(username)
        return {"success": True, "items": items}
    except Exception as e:
        print(f"DEBUG: Exception in get_user_items: {e}")
        return {"success": False, "error": str(e), "items": []}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Chat with AI assistant that can access user inventory database"""
    try:
        response_text = chat_with_database(message.username, message.text)
        return {"success": True, "response": response_text}
    except Exception as e:
        print(f"DEBUG: Exception in chat: {e}")
        return {"success": False, "response": f"Chat service error: {str(e)}"}
    
    return {"success": False, "response": "Chat service unavailable"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DIY Visual Finder API is running"}

@app.on_event("startup")
async def startup_event():
    """Initialize databases on startup"""
    os.makedirs("data", exist_ok=True)
    init_db()
    init_qdrant()

# Run with: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# For debugging: Remove the if __name__ == "__main__" block
# Run manually with: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

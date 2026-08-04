"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str
    full_name: str
    address: str

class ItemCreate(BaseModel):
    username: str  # SECURITY VULNERABILITY - No authentication, direct username exposure
    image: str     # base64 encoded - AI will analyze and generate all other fields

class SearchQuery(BaseModel):
    username: str  # SECURITY VULNERABILITY - No authentication of username
    image: str     # base64 encoded image for similarity search

class ItemResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str
    quantity: int
    location: str
    storage_box: str
    brand: str
    size: str
    condition: str
    created_at: str
    last_updated: str
    metadata: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    token: Optional[str] = None

class ChatMessage(BaseModel):
    username: str  # SECURITY VULNERABILITY - No authentication of username
    text: str

class ChatResponse(BaseModel):
    success: bool
    response: str

"""
API utilities for vision, embedding, and LLM calls
DELIBERATE PERFORMANCE ISSUES FOR CODERABBIT DEMO
"""
import re
import requests
import json
import base64
import os
from mistralai import Mistral
from config import MISTRAL_API_KEY, VOYAGE_API_KEY

def get_vision_analysis(image_data: str):
    """Call Mistral Pixtral for DIY item detection and metadata extraction"""
    try:
        # Initialize the Mistral client using environment variable or config
        api_key = MISTRAL_API_KEY
        client = Mistral(api_key=api_key)
        
        # Handle base64 image data format
        print(f"DEBUG: Original image_data length: {len(image_data)}")
        print(f"DEBUG: Image data starts with: {image_data[:50]}...")
        
        if image_data.startswith("data:image"):
            # Extract just the base64 part after the comma
            if ',' in image_data:
                base64_data = image_data.split(',', 1)[1]
                print(f"DEBUG: Extracted base64 length: {len(base64_data)}")
                formatted_image_data = image_data  # Use original data URI format
            else:
                print("DEBUG: No comma found in data URI")
                formatted_image_data = image_data
        else:
            # Assume it's raw base64, add proper data URI format
            formatted_image_data = f"data:image/png;base64,{image_data}"
        
        print(f"DEBUG: Final formatted image_data length: {len(formatted_image_data)}")
        print(f"DEBUG: Final starts with: {formatted_image_data[:50]}...")
        
        # Define the messages for DIY item analysis
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """You are a hardware expert analyzing DIY/construction items. Analyze this image and extract detailed specifications. Always give an educated guess of the size if it is not visible in the image.

                            REQUIRED JSON SCHEMA:
                            {
                            "name": "string - specific item name (e.g., 'M6 Hex Bolts', 'Phillips Wood Screws')",
                            "category": "string - category (fasteners, tools, lumber, electrical, plumbing, hardware, safety)",
                            "item_type": "string - specific hardware type (e.g., 'hex bolt', 'wood screw', 'wall anchor')",
                            "brand": "string or null - manufacturer name if visible",
                            "size": "string or null - dimensions/specifications (e.g., 'M6x25mm', '1/4-20x1.5in', '#8x2in')",
                            "condition": "string - 'new', 'used', or 'worn'",
                            "quantity": "number - count of items visible",
                            "description": "string - detailed description for inventory",
                            "location": "string - suggested storage location (e.g., 'Workshop', 'Garage', 'Toolbox')",
                            "storage_box": "string - suggested container (e.g., 'Hardware Drawer', 'Fastener Box', 'Tool Cabinet')",
                            "visible_text": "string or null - any text/markings on items or packaging"
                            }

                            EXAMPLES:
                            - Hex bolts: Look for thread pitch markings, head size, length. Common sizes: M6, M8, M10, M12
                            - Wood screws: Look for gauge numbers (#6, #8, #10), length markings
                            - Machine screws: Look for thread specifications (1/4-20, 10-32, etc.)
                            - Washers: Look for inner/outer diameter markings
                            - Nuts: Look for thread specifications matching bolt sizes

                            ANALYSIS FOCUS:
                            1. Examine threads closely for size markings
                            2. Look for stamped numbers on bolt heads
                            3. Check for metric (M6, M8) vs imperial (1/4", 3/8") sizing
                            4. Count items carefully
                            5. Assess surface finish and wear
                            6. Suggest appropriate storage location and container

                            Return ONLY valid JSON matching the schema above."""
                    },
                    {
                        "type": "image_url",
                        "image_url": formatted_image_data
                    }
                ]
            }
        ]
        
        # Get the chat response using Pixtral model
        chat_response = client.chat.complete(
            model="pixtral-large-latest",
            messages=messages
        )
        
        # Return structured response similar to Google Vision format
        return {
            "responses": [{
                "labelAnnotations": [{"description": "DIY item"}],
                "textAnnotations": [{"description": chat_response.choices[0].message.content}],
                "mistral_analysis": chat_response.choices[0].message.content
            }]
        }
        
    except Exception as e:
        print(f"Mistral API error: {e}")
        # Fallback to mock data
        return {
            "responses": [{
                "labelAnnotations": [{"description": "hardware"}],
                "textAnnotations": [{"description": "DIY item"}]
            }]
        }

def generate_embedding(image_data: str):
    """Generate embeddings using Voyage AI multimodal embeddings"""
    try:
        import voyageai
        from PIL import Image
        import base64
        import io
        
        # Initialize Voyage AI client
        vo = voyageai.Client(api_key=VOYAGE_API_KEY)
        
        # Extract base64 data and convert to PIL Image
        if image_data.startswith("data:image"):
            base64_data = image_data.split(',', 1)[1] if ',' in image_data else image_data
        else:
            base64_data = image_data
        
        # Decode base64 to PIL Image
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Create input for Voyage AI (text + image pair)
        inputs = [["DIY hardware item", image]]
        
        # Generate multimodal embedding
        result = vo.multimodal_embed(inputs, model="voyage-multimodal-3")
        
        # Return the embedding vector
        return result.embeddings[0]
        
    except Exception as e:
        print(f"Voyage AI embedding error: {e}")
        # Return mock embedding on error
        return [0.1] * 1024  # Voyage embeddings are typically 1024-dimensional

def extract_diy_metadata(vision_data: dict, name: str, category: str):
    """Extract DIY-specific metadata from Mistral analysis"""
    
    try:
        # Get Mistral analysis from vision data
        mistral_analysis = vision_data.get('responses', [{}])[0].get('mistral_analysis', '')
        
        if mistral_analysis:
            # Extract JSON from the markdown code block
            json_match = re.search(r'```json\n(.*?)\n```', mistral_analysis, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                mistral_data = json.loads(json_str)
                
                # Map Mistral fields to expected format
                return {
                    "choices": [{
                        "message": {
                            "content": json.dumps({
                                "name": mistral_data.get("name", "Detected Item"),
                                "estimated_quantity": mistral_data.get("quantity", 1),
                                "brand": mistral_data.get("brand") or "",
                                "size": mistral_data.get("size") or "",
                                "condition": mistral_data.get("condition", "new"),
                                "description": f"{mistral_data.get('item_type', 'Detected Item')} - {category}",
                                "location": mistral_data.get("location", ""),
                                "storage_box": mistral_data.get("storage_box", "")
                            })
                        }
                    }]
                }
                
    except Exception as e:
        print(f"Error parsing Mistral metadata: {e}")



def _validate_sql_query(sql_query: str, username: str):
    """
    Validate SQL query for security - only allow SELECT queries that access user's own data.
    Returns (is_valid, error_message)
    """
    import re
    
    # Normalize query - remove extra whitespace
    normalized_query = ' '.join(sql_query.split()).upper()
    
    # Only allow SELECT queries
    if not normalized_query.strip().startswith('SELECT'):
        return False, "Only SELECT queries are allowed"
    
    # Block dangerous SQL keywords
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 
                        'EXEC', 'EXECUTE', 'UNION', '--', '/*', '*/', ';']
    for keyword in dangerous_keywords:
        if keyword in normalized_query:
            return False, f"Query contains forbidden keyword: {keyword}"
    
    # Ensure query includes user_id filter for security
    # Check if query references items table and includes user_id filter
    if 'ITEMS' in normalized_query:
        # Use parameterized check - username will be validated separately
        if 'USER_ID' not in normalized_query:
            return False, "Query must include user_id filter for security"
    
    # Block access to users table (sensitive data)
    if 'FROM USERS' in normalized_query or 'JOIN USERS' in normalized_query:
        return False, "Access to users table is not allowed"
    
    return True, ""

def _sanitize_username(username: str) -> str:
    """Sanitize username to prevent SQL injection in prompts"""
    # Remove any SQL injection characters
    import re
    # Only allow alphanumeric, underscore, hyphen, and dot
    sanitized = re.sub(r'[^a-zA-Z0-9_\-.]', '', username)
    return sanitized

def chat_with_database(username: str, message_text: str):
    """Chat interface with SQL database access using Mistral function calling"""
    try:
        from databases.sql import DATABASE_PATH
        import sqlite3
        
        # Sanitize username to prevent prompt injection
        sanitized_username = _sanitize_username(username)
        if not sanitized_username or sanitized_username != username:
            return "Invalid username format. Please use only alphanumeric characters, underscores, hyphens, and dots."
        
        # Sanitize message text to prevent prompt injection
        # Remove any attempt to inject SQL or system instructions
        sanitized_message = message_text[:500]  # Limit length
        # Remove common injection patterns
        if any(pattern in sanitized_message.upper() for pattern in ['DROP', 'DELETE', 'UPDATE', 'INSERT', ';--', '/*']):
            return "Your message contains invalid characters. Please rephrase your question."
        
        # Initialize the Mistral client
        api_key = MISTRAL_API_KEY
        client = Mistral(api_key=api_key)
        
        # Define SQL execution function for Mistral with stricter description
        sql_execution_tool = {
            "type": "function",
            "function": {
                "name": "execute_sql_query",
                "description": "Execute SELECT queries on the items table only. Queries must include user_id filter. Only SELECT queries are allowed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "A SELECT query on the items table. Must include WHERE user_id = ? clause."
                        },
                        "explanation": {
                            "type": "string", 
                            "description": "Brief explanation of what the query does"
                        }
                    },
                    "required": ["sql_query", "explanation"]
                }
            }
        }
        
        # Secure system prompt - removed sensitive schema details and use parameterized approach
        system_prompt = """You are a DIY assistant with access to a SQLite database containing user inventory data.

DATABASE SCHEMA (items table only):
- id (INTEGER), user_id (TEXT), name (TEXT), category (TEXT), description (TEXT), quantity (INTEGER), location (TEXT), storage_box (TEXT), brand (TEXT), size (TEXT), condition (TEXT), purchase_date (TEXT), image_data (TEXT), metadata (TEXT), created_at (TIMESTAMP), last_updated (TIMESTAMP)

SECURITY RULES:
- You can ONLY execute SELECT queries on the items table
- Every query MUST include: WHERE user_id = ? (use parameterized query)
- You CANNOT access the users table
- You CANNOT use DROP, DELETE, UPDATE, INSERT, or any modification commands
- Use parameterized queries with ? placeholders for user_id

SEARCH STRATEGIES:
- Use LIKE '%term%' for fuzzy matching on name, description, size, brand fields
- Use SUM(quantity) for counting items
- Always filter by user_id using parameterized queries

EXAMPLE QUERIES (use ? for user_id parameter):
- "How many M6 bolts?" → SELECT SUM(quantity) FROM items WHERE user_id = ? AND (name LIKE '%M6%' OR size LIKE '%M6%' OR description LIKE '%M6%')
- "What's in my garage?" → SELECT * FROM items WHERE user_id = ? AND location LIKE '%garage%'
- "Show all items" → SELECT * FROM items WHERE user_id = ?

The current user's username will be provided as a parameter when executing queries."""

        # Get response with function calling
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": sanitized_message}
            ],
            tools=[sql_execution_tool],
            tool_choice="auto"
        )
        
        # Check if model wants to call the SQL function
        if chat_response.choices[0].message.tool_calls:
            tool_call = chat_response.choices[0].message.tool_calls[0]
            
            if tool_call.function.name == "execute_sql_query":
                # Parse function arguments
                import json
                function_args = json.loads(tool_call.function.arguments)
                sql_query = function_args.get("sql_query", "")
                explanation = function_args.get("explanation", "")
                
                print(f"DEBUG: AI wants to execute SQL: {sql_query}")
                print(f"DEBUG: AI explanation: {explanation}")
                
                # Validate SQL query before execution
                is_valid, error_msg = _validate_sql_query(sql_query, sanitized_username)
                if not is_valid:
                    return f"I cannot execute that query for security reasons: {error_msg}. Please rephrase your question."
                
                # Execute query with parameterized username to prevent SQL injection
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                
                try:
                    # Use parameterized query - replace ? placeholder with actual username
                    # This prevents SQL injection even if validation is bypassed
                    if '?' in sql_query:
                        # Query already has placeholder - use parameterized execution
                        cursor.execute(sql_query, (sanitized_username,))
                    else:
                        # Fallback: if no placeholder, add user_id filter manually with parameterized query
                        if 'WHERE' in sql_query.upper():
                            safe_query = f"{sql_query} AND user_id = ?"
                        else:
                            safe_query = f"{sql_query} WHERE user_id = ?"
                        cursor.execute(safe_query, (sanitized_username,))
                    
                    results = cursor.fetchall()
                    
                    # Format results for user
                    if results:
                        result_text = f"Query executed: {explanation}\n\nResults:\n"
                        for row in results:
                            result_text += f"- {', '.join(str(col) for col in row)}\n"
                    else:
                        result_text = f"Query executed: {explanation}\n\nNo results found."
                        
                    conn.close()
                    
                    # Get final response from AI with the results
                    final_response = client.chat.complete(
                        model="mistral-large-latest",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": sanitized_message},
                            {"role": "assistant", "content": "I executed a query to find your items."},
                            {"role": "user", "content": f"Query results: {result_text}"}
                        ]
                    )
                    
                    return final_response.choices[0].message.content
                    
                except Exception as sql_error:
                    conn.close()
                    # Don't expose SQL errors to user - security best practice
                    print(f"SQL execution error: {sql_error}")
                    return "I encountered an error while searching your inventory. Please try rephrasing your question."
        
        # If no function call, return regular response
        return chat_response.choices[0].message.content
        
    except Exception as e:
        # MAINTAINABILITY ISSUE - Generic exception handling
        print(f"Database chat error: {e}")
        return f"Sorry, I had trouble accessing your inventory data. Error: {str(e)}"

def process_item_data(item_name: str, item_category: str, image_data: str):
    """Process item with multiple API calls - PERFORMANCE ISSUES"""
    # PERFORMANCE ISSUE - Sequential API calls instead of async
    vision_data = get_vision_analysis(image_data)
    embedding = generate_embedding(image_data)
    
    # Extract DIY-specific metadata from vision analysis
    diy_metadata = extract_diy_metadata(vision_data, item_name, item_category)
    
    return {
        "vision": vision_data,
        "embedding": embedding,
        "diy_metadata": diy_metadata
    }

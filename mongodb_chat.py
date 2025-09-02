#!/usr/bin/env python3
"""
MongoDB chat history system for medibot
This file handles chat history storage using MongoDB while keeping user authentication in MySQL
"""

import pymongo
import uuid
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple

# Load environment variables
load_dotenv()

class MongoDBChatHistory:
    def __init__(self):
        """Initialize MongoDB connection for chat history"""
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'medibot_chats')
        self.client = None
        self.db = None
        self.db_available = False
        
        try:
            self.connect()
            self.init_collections()
            self.db_available = True
            print("✅ MongoDB chat history initialized successfully")
        except Exception as e:
            print(f"⚠️  MongoDB initialization failed: {e}")
            print("📋 Chat history will not be persistent")
            self.db_available = False
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = pymongo.MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000
            )
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            print(f"✅ Connected to MongoDB: {self.database_name}")
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            raise
    
    def init_collections(self):
        """Initialize MongoDB collections and indexes"""
        if not self.db:
            return
            
        # Create collections if they don't exist
        collections = self.db.list_collection_names()
        
        # Chat messages collection
        if 'chat_messages' not in collections:
            self.db.create_collection('chat_messages')
            print("✅ Created chat_messages collection")
        
        # Chat sessions collection  
        if 'chat_sessions' not in collections:
            self.db.create_collection('chat_sessions')
            print("✅ Created chat_sessions collection")
        
        # Create indexes for better performance
        self.db.chat_messages.create_index([("user_id", 1), ("timestamp", -1)])
        self.db.chat_messages.create_index([("conversation_id", 1), ("message_order", 1)])
        self.db.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)])
        self.db.chat_sessions.create_index([("conversation_id", 1)])
        
        print("✅ MongoDB indexes created")
    
    def save_chat_message(self, user_id: int, message: str, response: str, 
                         conversation_id: str = None, session_token: str = None) -> bool:
        """Save chat message and response to MongoDB"""
        if not self.db_available:
            print("⚠️  MongoDB not available, cannot save chat message")
            return False
            
        try:
            # Generate conversation_id if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Get or create session
            session = self.get_or_create_session(user_id, conversation_id, message)
            
            # Get next message order for this conversation
            last_message = self.db.chat_messages.find_one(
                {"conversation_id": conversation_id},
                sort=[("message_order", -1)]
            )
            next_order = (last_message["message_order"] + 1) if last_message else 1
            
            timestamp = datetime.now(timezone.utc)
            
            # Save user message
            user_message_doc = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_type": "user",
                "message": message,
                "timestamp": timestamp,
                "message_order": next_order
            }
            self.db.chat_messages.insert_one(user_message_doc)
            
            # Save assistant response
            assistant_message_doc = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_type": "assistant", 
                "message": response,
                "response": response,  # Keep both for compatibility
                "timestamp": timestamp,
                "message_order": next_order + 1
            }
            self.db.chat_messages.insert_one(assistant_message_doc)
            
            # Update session
            self.db.chat_sessions.update_one(
                {"conversation_id": conversation_id},
                {
                    "$set": {
                        "updated_at": timestamp,
                        "message_count": next_order + 1
                    }
                }
            )
            
            print(f"💾 Chat message saved to MongoDB: {conversation_id}")
            return True
            
        except Exception as e:
            print(f"Save chat message error: {e}")
            return False
    
    def get_or_create_session(self, user_id: int, conversation_id: str, first_message: str) -> Dict:
        """Get existing session or create new one"""
        session = self.db.chat_sessions.find_one({"conversation_id": conversation_id})
        
        if not session:
            # Create new session
            title = first_message[:50] + "..." if len(first_message) > 50 else first_message
            session = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "session_title": title,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "is_active": True,
                "message_count": 0
            }
            self.db.chat_sessions.insert_one(session)
            print(f"📝 Created new session: {conversation_id}")
        
        return session
    
    def get_chat_history(self, user_id: int, limit: int = 50) -> List[Tuple[str, str, datetime]]:
        """Get user's recent chat history"""
        if not self.db_available:
            print("⚠️  MongoDB not available, returning empty chat history")
            return []
            
        try:
            # Get user messages paired with their responses
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "message_type": "user"
                    }
                },
                {
                    "$sort": {"timestamp": -1}
                },
                {
                    "$limit": limit
                },
                {
                    "$lookup": {
                        "from": "chat_messages",
                        "let": {
                            "conv_id": "$conversation_id", 
                            "msg_order": "$message_order"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$conversation_id", "$$conv_id"]},
                                            {"$eq": ["$message_order", {"$add": ["$$msg_order", 1]}]},
                                            {"$eq": ["$message_type", "assistant"]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "assistant_response"
                    }
                }
            ]
            
            results = list(self.db.chat_messages.aggregate(pipeline))
            
            history = []
            for doc in results:
                user_message = doc["message"]
                assistant_response = "No response"
                if doc["assistant_response"]:
                    assistant_response = doc["assistant_response"][0]["message"]
                timestamp = doc["timestamp"]
                
                history.append((user_message, assistant_response, timestamp))
            
            return history
            
        except Exception as e:
            print(f"Get chat history error: {e}")
            return []
    
    def clear_all_user_chats(self, user_id: int) -> int:
        """Clear all chat history for a user"""
        if not self.db_available:
            print("⚠️  MongoDB not available, cannot clear chats")
            return 0
            
        try:
            # Count messages before deletion
            message_count = self.db.chat_messages.count_documents({"user_id": user_id})
            
            # Delete all user's chat messages
            self.db.chat_messages.delete_many({"user_id": user_id})
            
            # Deactivate all user's sessions
            self.db.chat_sessions.update_many(
                {"user_id": user_id},
                {"$set": {"is_active": False}}
            )
            
            print(f"🗑️  Cleared all chats for user {user_id}: {message_count} messages deleted")
            return message_count
            
        except Exception as e:
            print(f"Clear chats error: {e}")
            return 0
    
    def get_user_conversations(self, user_id: int) -> List[Dict]:
        """Get all conversations for a user"""
        if not self.db_available:
            return []
            
        try:
            conversations = list(self.db.chat_sessions.find(
                {"user_id": user_id, "is_active": True},
                sort=[("updated_at", -1)]
            ))
            
            result = []
            for conv in conversations:
                result.append({
                    'id': conv['conversation_id'],
                    'title': conv['session_title'],
                    'created_at': conv['created_at'].isoformat() if conv['created_at'] else None,
                    'updated_at': conv['updated_at'].isoformat() if conv['updated_at'] else None,
                    'message_count': conv.get('message_count', 0)
                })
            
            return result
            
        except Exception as e:
            print(f"Get conversations error: {e}")
            return []
    
    def get_conversation_messages(self, conversation_id: str, user_id: int) -> List[Dict]:
        """Get all messages in a specific conversation"""
        if not self.db_available:
            return []
            
        try:
            messages = list(self.db.chat_messages.find(
                {
                    "conversation_id": conversation_id,
                    "user_id": user_id
                },
                sort=[("message_order", 1)]
            ))
            
            result = []
            for msg in messages:
                result.append({
                    'type': msg['message_type'],
                    'message': msg['message'],
                    'timestamp': msg['timestamp'].isoformat() if msg['timestamp'] else None,
                    'message_order': msg['message_order']
                })
            
            return result
            
        except Exception as e:
            print(f"Get conversation messages error: {e}")
            return []
    
    def delete_conversation(self, conversation_id: str, user_id: int) -> bool:
        """Delete a specific conversation"""
        if not self.db_available:
            return False
            
        try:
            # Delete all messages in the conversation
            self.db.chat_messages.delete_many({
                "conversation_id": conversation_id,
                "user_id": user_id
            })
            
            # Deactivate the session
            self.db.chat_sessions.update_one(
                {"conversation_id": conversation_id, "user_id": user_id},
                {"$set": {"is_active": False}}
            )
            
            print(f"🗑️  Deleted conversation: {conversation_id}")
            return True
            
        except Exception as e:
            print(f"Delete conversation error: {e}")
            return False
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")


# Test the MongoDB functionality
if __name__ == "__main__":
    print("Testing MongoDB chat history system...")
    print("Make sure MongoDB is running and environment variables are set!")
    
    try:
        # Initialize the chat history system
        mongo_chat = MongoDBChatHistory()
        
        if mongo_chat.db_available:
            print("✅ MongoDB chat history system is working!")
            
            # Test saving a message
            test_user_id = 1
            test_conversation_id = str(uuid.uuid4())
            
            success = mongo_chat.save_chat_message(
                test_user_id,
                "Hello, this is a test message",
                "Hello! This is a test response from the AI.",
                test_conversation_id
            )
            
            if success:
                print("✅ Test message saved successfully")
                
                # Test retrieving history
                history = mongo_chat.get_chat_history(test_user_id, 10)
                print(f"✅ Retrieved {len(history)} messages from history")
                
                # Test getting conversations
                conversations = mongo_chat.get_user_conversations(test_user_id)
                print(f"✅ Retrieved {len(conversations)} conversations")
                
                # Clean up test data
                mongo_chat.delete_conversation(test_conversation_id, test_user_id)
                print("✅ Test data cleaned up")
            else:
                print("❌ Failed to save test message")
        else:
            print("❌ MongoDB not available")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
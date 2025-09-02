#!/usr/bin/env python3
"""
MongoDB setup and connection test script for medibot chat history
This script connects to MongoDB, creates necessary collections and indexes
"""

import os
import sys
from dotenv import load_dotenv
from mongodb_chat import MongoDBChatHistory
import pymongo
from datetime import datetime

def check_env_variables():
    """Check if MongoDB environment variables are set"""
    print("🔍 Checking MongoDB environment variables:")
    
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_database = os.getenv('MONGODB_DATABASE')
    
    if mongodb_uri:
        # Mask credentials in URI for display
        display_uri = mongodb_uri
        if '@' in display_uri:
            # Hide username:password part
            parts = display_uri.split('@')
            if len(parts) > 1:
                display_uri = f"mongodb://***:***@{parts[1]}"
        print(f"   ✅ MONGODB_URI: {display_uri}")
    else:
        print("   ❌ MONGODB_URI: Not set")
        return False
    
    if mongodb_database:
        print(f"   ✅ MONGODB_DATABASE: {mongodb_database}")
    else:
        print("   ⚠️  MONGODB_DATABASE: Not set (will use default: medibot_chats)")
    
    return True

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("\n🔗 Testing MongoDB connection...")
    
    try:
        mongo_chat = MongoDBChatHistory()
        
        if not mongo_chat.db_available:
            print("❌ MongoDB connection failed")
            return False
        
        # Test basic operations
        print("✅ MongoDB connection successful")
        
        # Test database and collections
        db = mongo_chat.db
        collections = db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        # Test indexes
        chat_messages_indexes = list(db.chat_messages.list_indexes())
        chat_sessions_indexes = list(db.chat_sessions.list_indexes())
        
        print(f"📊 chat_messages indexes: {len(chat_messages_indexes)}")
        print(f"📊 chat_sessions indexes: {len(chat_sessions_indexes)}")
        
        # Test a sample operation
        print("\n🧪 Testing sample operations...")
        
        test_user_id = 999999  # Use a test user ID that won't conflict
        test_message = "Test connection message"
        test_response = "Test connection response"
        
        # Save test message
        success = mongo_chat.save_chat_message(
            test_user_id, 
            test_message, 
            test_response
        )
        
        if success:
            print("✅ Test message saved successfully")
            
            # Retrieve test message
            history = mongo_chat.get_chat_history(test_user_id, 1)
            if history and len(history) > 0:
                print("✅ Test message retrieved successfully")
                
                # Clean up test data
                deleted_count = mongo_chat.clear_all_user_chats(test_user_id)
                print(f"✅ Test data cleaned up ({deleted_count} messages deleted)")
            else:
                print("⚠️  Could not retrieve test message")
        else:
            print("❌ Failed to save test message")
        
        mongo_chat.close_connection()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

def show_mongodb_info():
    """Display MongoDB configuration information"""
    print("\n📋 MongoDB Configuration:")
    
    mongodb_uri = os.getenv('MONGODB_URI', 'Not set')
    mongodb_database = os.getenv('MONGODB_DATABASE', 'medibot_chats')
    
    # Mask credentials for display
    display_uri = mongodb_uri
    if '@' in display_uri and mongodb_uri != 'Not set':
        parts = display_uri.split('@')
        if len(parts) > 1:
            display_uri = f"mongodb://***:***@{parts[1]}"
    
    print(f"   URI: {display_uri}")
    print(f"   Database: {mongodb_database}")

def create_mongodb_database():
    """Create MongoDB database and collections"""
    print("\n🏗️  Setting up MongoDB database...")
    
    try:
        mongo_chat = MongoDBChatHistory()
        
        if mongo_chat.db_available:
            print("✅ MongoDB database setup completed successfully")
            
            # Show collection stats
            db = mongo_chat.db
            for collection_name in ['chat_messages', 'chat_sessions']:
                if collection_name in db.list_collection_names():
                    count = db[collection_name].count_documents({})
                    print(f"   📊 {collection_name}: {count} documents")
            
            mongo_chat.close_connection()
            return True
        else:
            print("❌ Failed to setup MongoDB database")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 MongoDB Chat History Setup for Medibot")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print("⚠️  .env file not found!")
        print("Please create a .env file with your MongoDB credentials:")
        print("MONGODB_URI=mongodb://username:password@your-mongodb-host:27017/medibot_chats?authSource=admin")
        print("MONGODB_DATABASE=medibot_chats")
        return False
    
    # Check environment variables
    env_ok = check_env_variables()
    if not env_ok:
        print("\n❌ Missing required environment variables")
        print("Please check your .env file and add:")
        print("MONGODB_URI=mongodb://username:password@your-mongodb-host:27017/medibot_chats?authSource=admin")
        return False
    
    # Show configuration
    show_mongodb_info()
    
    # Create database and collections
    setup_success = create_mongodb_database()
    
    if setup_success:
        # Test connection
        test_success = test_mongodb_connection()
        
        if test_success:
            print("\n🎉 MongoDB setup completed successfully!")
            print("\nNext steps:")
            print("1. Your MongoDB database is ready for chat history storage")
            print("2. User authentication will still use MySQL")
            print("3. Run the main application: python main.py")
            print("4. All new chat conversations will be stored in MongoDB")
            return True
        else:
            print("\n⚠️  Database created but connection test failed")
            print("Please check your MongoDB configuration")
            return False
    else:
        print("\n❌ MongoDB setup failed")
        print("Please check your MongoDB connection and credentials")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
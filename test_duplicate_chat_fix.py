#!/usr/bin/env python3
"""
Test script to verify the duplicate chat fix
This script tests the new conversation ID generation and ensures no duplicate chats are created
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime, timezone

# Add current directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_conversation_id_generation():
    """Test that new conversation IDs are generated properly"""
    print("🧪 Testing Conversation ID Generation")
    print("=" * 50)
    
    try:
        # Import the authentication database
        from medibot2_auth import MedibotAuthDatabase
        
        # Initialize database connection
        print("📡 Connecting to MySQL database...")
        auth_db = MedibotAuthDatabase()
        
        if not auth_db.db_available:
            print("❌ MySQL database not available. Please check your database connection.")
            return False
        
        print("✅ MySQL database connection successful")
        
        # Test user ID (use a test user ID)
        test_user_id = 999  # Use a test user ID that won't conflict with real users
        
        print(f"\n📝 Testing with user ID: {test_user_id}")
        
        # Test 1: Create first session
        print("\n📤 Test 1: Creating first session...")
        session_token_1 = auth_db.create_session(test_user_id)
        
        if not session_token_1:
            print("❌ Failed to create first session")
            return False
        
        print(f"✅ First session created: {session_token_1[:20]}...")
        
        # Get conversation ID from first session
        user_session_1 = auth_db.verify_session(session_token_1)
        conversation_id_1 = user_session_1.get('conversation_id') if user_session_1 else None
        
        if not conversation_id_1:
            print("❌ Failed to get conversation ID from first session")
            return False
        
        print(f"✅ First conversation ID: {conversation_id_1}")
        
        # Test 2: Create second session (simulating "new chat")
        print("\n📤 Test 2: Creating second session (new chat)...")
        session_token_2 = auth_db.create_session(test_user_id)
        
        if not session_token_2:
            print("❌ Failed to create second session")
            return False
        
        print(f"✅ Second session created: {session_token_2[:20]}...")
        
        # Get conversation ID from second session
        user_session_2 = auth_db.verify_session(session_token_2)
        conversation_id_2 = user_session_2.get('conversation_id') if user_session_2 else None
        
        if not conversation_id_2:
            print("❌ Failed to get conversation ID from second session")
            return False
        
        print(f"✅ Second conversation ID: {conversation_id_2}")
        
        # Test 3: Verify conversation IDs are different
        print("\n🔍 Test 3: Verifying conversation IDs are different...")
        if conversation_id_1 == conversation_id_2:
            print("❌ Conversation IDs are the same! This will cause duplicate chats.")
            return False
        
        print("✅ Conversation IDs are different - no duplicate chats will be created")
        
        # Test 4: Test MongoDB chat saving with different conversation IDs
        print("\n📤 Test 4: Testing MongoDB chat saving...")
        from mongodb_chat import MongoDBChatHistory
        
        mongo_chat = MongoDBChatHistory()
        if not mongo_chat.db_available:
            print("❌ MongoDB not available")
            return False
        
        # Save message to first conversation
        success_1 = mongo_chat.save_chat_message(
            user_id=test_user_id,
            message="First conversation message",
            response="First conversation response",
            conversation_id=conversation_id_1
        )
        
        if not success_1:
            print("❌ Failed to save message to first conversation")
            return False
        
        print("✅ Message saved to first conversation")
        
        # Save message to second conversation
        success_2 = mongo_chat.save_chat_message(
            user_id=test_user_id,
            message="Second conversation message",
            response="Second conversation response",
            conversation_id=conversation_id_2
        )
        
        if not success_2:
            print("❌ Failed to save message to second conversation")
            return False
        
        print("✅ Message saved to second conversation")
        
        # Test 5: Verify conversations are separate
        print("\n🔍 Test 5: Verifying conversations are separate...")
        
        # Get first conversation messages
        messages_1 = mongo_chat.get_conversation_messages(conversation_id_1, test_user_id)
        print(f"📊 First conversation has {len(messages_1)} messages")
        
        # Get second conversation messages
        messages_2 = mongo_chat.get_conversation_messages(conversation_id_2, test_user_id)
        print(f"📊 Second conversation has {len(messages_2)} messages")
        
        if len(messages_1) != 2 or len(messages_2) != 2:
            print("❌ Expected 2 messages in each conversation")
            return False
        
        # Verify messages are different
        if messages_1[0]['message'] == messages_2[0]['message']:
            print("❌ Messages are the same in both conversations")
            return False
        
        print("✅ Conversations are properly separated")
        
        # Test 6: Get user conversations
        print("\n📚 Test 6: Testing user conversations retrieval...")
        conversations = mongo_chat.get_user_conversations(test_user_id)
        print(f"📊 User has {len(conversations)} conversations")
        
        if len(conversations) != 2:
            print(f"❌ Expected 2 conversations, got {len(conversations)}")
            return False
        
        # Verify conversation IDs match
        conv_ids = [conv['id'] for conv in conversations]
        if conversation_id_1 not in conv_ids or conversation_id_2 not in conv_ids:
            print("❌ Conversation IDs don't match retrieved conversations")
            return False
        
        print("✅ User conversations retrieved correctly")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        mongo_chat.db.chat_messages.delete_many({
            "user_id": test_user_id,
            "conversation_id": {"$in": [conversation_id_1, conversation_id_2]}
        })
        mongo_chat.db.chat_sessions.delete_many({
            "user_id": test_user_id,
            "conversation_id": {"$in": [conversation_id_1, conversation_id_2]}
        })
        
        # Clean up MySQL sessions
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_sessions WHERE user_id = %s", (test_user_id,))
        conn.commit()
        conn.close()
        
        print("✅ Test data cleaned up")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ New conversation IDs are generated properly")
        print("✅ No duplicate chats will be created")
        print("✅ Conversations are properly separated")
        print("✅ The duplicate chat issue should now be fixed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reset_api_simulation():
    """Test the reset API logic simulation"""
    print("\n🧪 Testing Reset API Logic Simulation")
    print("=" * 50)
    
    try:
        from medibot2_auth import MedibotAuthDatabase
        
        auth_db = MedibotAuthDatabase()
        if not auth_db.db_available:
            print("❌ MySQL database not available")
            return False
        
        test_user_id = 999
        
        # Simulate the reset API logic
        print("🔄 Simulating reset API logic...")
        
        # 1. Create initial session
        session_token_1 = auth_db.create_session(test_user_id)
        user_session_1 = auth_db.verify_session(session_token_1)
        conversation_id_1 = user_session_1.get('conversation_id')
        
        print(f"✅ Initial session: {conversation_id_1}")
        
        # 2. Simulate reset (create new session)
        session_token_2 = auth_db.create_session(test_user_id)
        user_session_2 = auth_db.verify_session(session_token_2)
        conversation_id_2 = user_session_2.get('conversation_id')
        
        print(f"✅ New session after reset: {conversation_id_2}")
        
        # 3. Verify they are different
        if conversation_id_1 == conversation_id_2:
            print("❌ Reset API logic failed - same conversation ID")
            return False
        
        print("✅ Reset API logic works correctly - new conversation ID generated")
        
        # Clean up
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_sessions WHERE user_id = %s", (test_user_id,))
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Reset API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Duplicate Chat Fix Verification")
    print("=" * 60)
    
    # Test conversation ID generation
    conversation_success = test_conversation_id_generation()
    
    # Test reset API logic
    reset_success = test_reset_api_simulation()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if conversation_success and reset_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ New conversation IDs are generated properly")
        print("✅ Reset API creates new conversation IDs")
        print("✅ No duplicate chats will be created")
        print("✅ The duplicate chat issue should now be fixed")
        print("\n📋 NEXT STEPS:")
        print("1. Start the application: python main.py")
        print("2. Clear all chats")
        print("3. Start a new chat and send 2 messages")
        print("4. Refresh the page")
        print("5. Verify only ONE chat appears in the sidebar")
        print("6. Click on the chat to verify it shows all messages")
    else:
        print("❌ SOME TESTS FAILED!")
        if not conversation_success:
            print("❌ Conversation ID generation test failed")
        if not reset_success:
            print("❌ Reset API logic test failed")
        print("\n🔧 Please check the error messages above and fix the issues")
    
    print("=" * 60)

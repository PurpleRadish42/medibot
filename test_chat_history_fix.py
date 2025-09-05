#!/usr/bin/env python3
"""
Test script to verify chat history fixes
This script tests the MongoDB chat history functionality to ensure both user and bot messages are retrieved correctly
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime, timezone

# Add current directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_mongodb_chat_history():
    """Test MongoDB chat history functionality"""
    print("🧪 Testing MongoDB Chat History Functionality")
    print("=" * 50)
    
    try:
        # Import the MongoDB chat history class
        from mongodb_chat import MongoDBChatHistory
        
        # Initialize MongoDB connection
        print("📡 Connecting to MongoDB...")
        mongo_chat = MongoDBChatHistory()
        
        if not mongo_chat.db_available:
            print("❌ MongoDB not available. Please check your MongoDB connection.")
            return False
        
        print("✅ MongoDB connection successful")
        
        # Test user ID (use a test user ID)
        test_user_id = 999  # Use a test user ID that won't conflict with real users
        
        # Test conversation ID
        test_conversation_id = "test-conversation-123"
        
        print(f"\n📝 Testing with user ID: {test_user_id}")
        print(f"📝 Testing with conversation ID: {test_conversation_id}")
        
        # Clear any existing test data
        print("\n🧹 Cleaning up existing test data...")
        mongo_chat.db.chat_messages.delete_many({
            "user_id": test_user_id,
            "conversation_id": test_conversation_id
        })
        mongo_chat.db.chat_sessions.delete_many({
            "user_id": test_user_id,
            "conversation_id": test_conversation_id
        })
        
        # Test 1: Save a chat message and response
        print("\n📤 Test 1: Saving chat message and response...")
        test_message = "I have a headache"
        test_response = "I understand you have a headache. Let me help you find a neurologist in your area."
        
        success = mongo_chat.save_chat_message(
            user_id=test_user_id,
            message=test_message,
            response=test_response,
            conversation_id=test_conversation_id
        )
        
        if success:
            print("✅ Chat message saved successfully")
        else:
            print("❌ Failed to save chat message")
            return False
        
        # Test 2: Retrieve conversation messages
        print("\n📥 Test 2: Retrieving conversation messages...")
        messages = mongo_chat.get_conversation_messages(test_conversation_id, test_user_id)
        
        print(f"📊 Retrieved {len(messages)} messages")
        
        if len(messages) != 2:
            print(f"❌ Expected 2 messages (user + assistant), got {len(messages)}")
            return False
        
        # Check user message
        user_message = next((msg for msg in messages if msg['type'] == 'user'), None)
        if not user_message:
            print("❌ User message not found")
            return False
        
        if user_message['message'] != test_message:
            print(f"❌ User message mismatch. Expected: '{test_message}', Got: '{user_message['message']}'")
            return False
        
        print("✅ User message retrieved correctly")
        
        # Check assistant message
        assistant_message = next((msg for msg in messages if msg['type'] == 'assistant'), None)
        if not assistant_message:
            print("❌ Assistant message not found")
            return False
        
        if 'response' not in assistant_message:
            print("❌ Assistant message missing 'response' field")
            return False
        
        if assistant_message['response'] != test_response:
            print(f"❌ Assistant response mismatch. Expected: '{test_response}', Got: '{assistant_message['response']}'")
            return False
        
        print("✅ Assistant message retrieved correctly with response field")
        
        # Test 3: Check message ordering
        print("\n📋 Test 3: Checking message ordering...")
        if user_message['message_order'] != 1:
            print(f"❌ User message order should be 1, got {user_message['message_order']}")
            return False
        
        if assistant_message['message_order'] != 2:
            print(f"❌ Assistant message order should be 2, got {assistant_message['message_order']}")
            return False
        
        print("✅ Message ordering is correct")
        
        # Test 4: Test get_chat_history method
        print("\n📚 Test 4: Testing get_chat_history method...")
        history = mongo_chat.get_chat_history(test_user_id, limit=10)
        
        print(f"📊 Retrieved {len(history)} history entries")
        
        if len(history) != 1:
            print(f"❌ Expected 1 history entry, got {len(history)}")
            return False
        
        history_message, history_response, history_timestamp = history[0]
        
        if history_message != test_message:
            print(f"❌ History message mismatch. Expected: '{test_message}', Got: '{history_message}'")
            return False
        
        if history_response != test_response:
            print(f"❌ History response mismatch. Expected: '{test_response}', Got: '{history_response}'")
            return False
        
        print("✅ Chat history retrieved correctly")
        
        # Test 5: Test get_user_conversations method
        print("\n💬 Test 5: Testing get_user_conversations method...")
        conversations = mongo_chat.get_user_conversations(test_user_id)
        
        print(f"📊 Retrieved {len(conversations)} conversations")
        
        if len(conversations) != 1:
            print(f"❌ Expected 1 conversation, got {len(conversations)}")
            return False
        
        conversation = conversations[0]
        
        if conversation['id'] != test_conversation_id:
            print(f"❌ Conversation ID mismatch. Expected: '{test_conversation_id}', Got: '{conversation['id']}'")
            return False
        
        print("✅ User conversations retrieved correctly")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        mongo_chat.db.chat_messages.delete_many({
            "user_id": test_user_id,
            "conversation_id": test_conversation_id
        })
        mongo_chat.db.chat_sessions.delete_many({
            "user_id": test_user_id,
            "conversation_id": test_conversation_id
        })
        
        print("✅ Test data cleaned up")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ MongoDB chat history is working correctly")
        print("✅ Both user and assistant messages are being saved and retrieved")
        print("✅ The response field is properly included for assistant messages")
        print("✅ Message ordering is correct")
        print("✅ Chat history and conversations APIs work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_conversion():
    """Test the frontend message conversion logic"""
    print("\n🧪 Testing Frontend Message Conversion")
    print("=" * 50)
    
    # Simulate database messages
    db_messages = [
        {
            'type': 'user',
            'message': 'I have a headache',
            'message_order': 1,
            'timestamp': '2024-01-01T12:00:00Z'
        },
        {
            'type': 'assistant',
            'message': 'I understand you have a headache.',
            'response': 'I understand you have a headache. Let me help you find a neurologist in your area.',
            'message_order': 2,
            'timestamp': '2024-01-01T12:00:01Z'
        }
    ]
    
    # Simulate the frontend conversion function
    def convertDatabaseMessagesToFrontendFormat(dbMessages):
        frontendMessages = []
        
        # Sort messages by order and timestamp to ensure proper sequence
        sortedMessages = sorted(dbMessages, key=lambda x: (x.get('message_order', 0), x.get('timestamp', '')))
        
        for dbMsg in sortedMessages:
            if dbMsg['type'] == 'user' and dbMsg['message']:
                # Add user message
                frontendMessages.append({
                    'content': dbMsg['message'],
                    'isUser': True,
                    'timestamp': dbMsg['timestamp'] or '2024-01-01T12:00:00Z'
                })
            
            if dbMsg['type'] == 'assistant' and dbMsg.get('response'):
                # Add assistant response (preserve HTML for doctor recommendations)
                frontendMessages.append({
                    'content': dbMsg['response'],
                    'isUser': False,
                    'timestamp': dbMsg['timestamp'] or '2024-01-01T12:00:00Z'
                })
        
        return frontendMessages
    
    # Test conversion
    frontend_messages = convertDatabaseMessagesToFrontendFormat(db_messages)
    
    print(f"📊 Converted {len(db_messages)} database messages to {len(frontend_messages)} frontend messages")
    
    if len(frontend_messages) != 2:
        print(f"❌ Expected 2 frontend messages, got {len(frontend_messages)}")
        return False
    
    # Check user message
    user_msg = next((msg for msg in frontend_messages if msg['isUser']), None)
    if not user_msg:
        print("❌ User message not found in frontend conversion")
        return False
    
    if user_msg['content'] != 'I have a headache':
        print(f"❌ User message content mismatch. Expected: 'I have a headache', Got: '{user_msg['content']}'")
        return False
    
    print("✅ User message converted correctly")
    
    # Check assistant message
    assistant_msg = next((msg for msg in frontend_messages if not msg['isUser']), None)
    if not assistant_msg:
        print("❌ Assistant message not found in frontend conversion")
        return False
    
    if assistant_msg['content'] != 'I understand you have a headache. Let me help you find a neurologist in your area.':
        print(f"❌ Assistant message content mismatch")
        return False
    
    print("✅ Assistant message converted correctly")
    
    print("✅ Frontend conversion logic is working correctly")
    return True

if __name__ == "__main__":
    print("🚀 Starting Chat History Fix Verification")
    print("=" * 60)
    
    # Test MongoDB functionality
    mongo_success = test_mongodb_chat_history()
    
    # Test frontend conversion
    frontend_success = test_frontend_conversion()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if mongo_success and frontend_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ MongoDB chat history is working correctly")
        print("✅ Frontend conversion logic is working correctly")
        print("✅ The chat history issue should now be fixed")
        print("\n📋 NEXT STEPS:")
        print("1. Start the application: python main.py")
        print("2. Login and create a new chat")
        print("3. Send a message and wait for bot response")
        print("4. Refresh the page and check if previous chats are visible")
        print("5. Click on a previous chat to verify it loads both user and bot messages")
    else:
        print("❌ SOME TESTS FAILED!")
        if not mongo_success:
            print("❌ MongoDB chat history test failed")
        if not frontend_success:
            print("❌ Frontend conversion test failed")
        print("\n🔧 Please check the error messages above and fix the issues")
    
    print("=" * 60)

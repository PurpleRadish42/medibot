#!/usr/bin/env python3
"""
Final comprehensive test to ensure everything works correctly
"""

import requests
import json

def test_complete_system():
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    # Test the chat API directly
    chat_url = "http://localhost:5000/api/chat"
    
    # Test message that should trigger orthopedist recommendation
    test_message = "I had an accident and my hand is in pain. I fell down and landed on my elbow."
    
    print(f"📨 Testing message: {test_message}")
    
    # Prepare the request data
    data = {
        "message": test_message,
        "city": "Bangalore",
        "sortPreference": "rating"
    }
    
    try:
        print("🔄 Sending request to chat API...")
        
        # Note: This will fail if authentication is required, but let's see the error
        response = requests.post(chat_url, json=data)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result.get('response', '')
            
            print(f"✅ Response received")
            print(f"📤 Response length: {len(bot_response)} characters")
            print(f"📤 Response preview (first 200 chars):")
            print(bot_response[:200])
            print("...")
            
            # Check for key elements
            if "<table" in bot_response:
                print("✅ Response contains HTML table")
                table_count = bot_response.count("<tr")
                print(f"📊 Table has {table_count} rows")
            else:
                print("❌ Response does NOT contain HTML table")
                
            if "orthopedist" in bot_response.lower():
                print("✅ Response contains orthopedist recommendation")
            else:
                print("❌ Response does NOT contain orthopedist recommendation")
                
            # Check for important elements
            checks = [
                ("Doctor name", "Dr." in bot_response),
                ("Consultation fee", "₹" in bot_response),
                ("Rating", "★" in bot_response),
                ("Distance", "km" in bot_response),
                ("Profile link", "View Profile" in bot_response),
                ("Important notes", "Important Notes" in bot_response)
            ]
            
            print("\n🔍 Content Analysis:")
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}: {'Found' if check_result else 'Missing'}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_complete_system()

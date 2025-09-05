#!/usr/bin/env python3
"""
Test the actual chat response to see what's happening with the table display
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_actual_chat_response():
    print("🧪 Testing Actual Chat Response Generation")
    print("=" * 50)
    
    try:
        # Test the medical recommender directly
        from src.llm.recommender import MedicalRecommender
        print("✅ Imported MedicalRecommender")
        
        recommender = MedicalRecommender()
        print("✅ Created MedicalRecommender instance")
        
        # Simulate the exact scenario from your test
        history = []
        message = "I had an accident and my hand is in pain. I fell down and landed on my elbow."
        
        print(f"\n📨 Testing message: {message}")
        
        response = recommender.generate_response(
            history, 
            message, 
            user_city="Bangalore",
            sort_preference="rating"
        )
        
        print(f"\n📤 Full Response Length: {len(response)} characters")
        print(f"📤 Full Response:\n{response}")
        
        # Check if response contains table
        if "<table" in response:
            print("\n✅ Response contains HTML table")
        else:
            print("\n❌ Response does NOT contain HTML table")
            
        # Check if response contains SPECIALIST_RECOMMENDATION
        if "SPECIALIST_RECOMMENDATION:" in response:
            print("✅ Response contains specialist recommendation")
        else:
            print("❌ Response does NOT contain specialist recommendation")
            
    except Exception as e:
        print(f"❌ Error testing medical recommender: {e}")
        import traceback
        traceback.print_exc()
        
        # Test fallback function
        print("\n🔄 Testing fallback response...")
        try:
            sys.path.insert(0, str(project_root))
            from main import fallback_medical_response
            
            fallback_response = fallback_medical_response(
                message, 
                sort_preference="rating"
            )
            
            print(f"\n📤 Fallback Response Length: {len(fallback_response)} characters")
            print(f"📤 Fallback Response:\n{fallback_response}")
            
            if "<table" in fallback_response:
                print("\n✅ Fallback response contains HTML table")
            else:
                print("\n❌ Fallback response does NOT contain HTML table")
                
        except Exception as e2:
            print(f"❌ Error testing fallback: {e2}")

if __name__ == "__main__":
    test_actual_chat_response()

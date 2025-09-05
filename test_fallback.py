#!/usr/bin/env python3
"""
Test the fallback medical response to see why the table isn't showing
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_fallback_response():
    print("🧪 Testing Fallback Medical Response")
    print("=" * 50)
    
    try:
        from main import fallback_medical_response
        print("✅ Imported fallback_medical_response")
        
        # Test with the exact message from your scenario
        message = "I had an accident and my hand is in pain. I fell down and landed on my elbow."
        
        print(f"\n📨 Testing message: {message}")
        
        response = fallback_medical_response(
            message, 
            sort_preference="rating"
        )
        
        print(f"\n📤 Response Length: {len(response)} characters")
        print(f"📤 Response:\n{response}")
        print(f"📤 Response (first 500 chars):\n{response[:500]}")
        
        # Check if response contains table
        if "<table" in response:
            print("\n✅ Response contains HTML table")
            # Count table rows
            table_rows = response.count("<tr")
            print(f"📊 Table has {table_rows} rows")
        else:
            print("\n❌ Response does NOT contain HTML table")
            
        # Check if response contains key elements
        if "orthopedist" in response.lower():
            print("✅ Response contains orthopedist recommendation")
        else:
            print("❌ Response does NOT contain orthopedist recommendation")
            
    except Exception as e:
        print(f"❌ Error testing fallback response: {e}")
        import traceback
        traceback.print_exc()
        
        # Test doctor recommender directly
        print("\n🔄 Testing DoctorRecommender directly...")
        try:
            from doctor_recommender import DoctorRecommender
            dr = DoctorRecommender()
            dr.load_doctors_data()
            
            doctors = dr.recommend_doctors("orthopedist", "Bangalore", limit=3, sort_by="rating")
            print(f"✅ Found {len(doctors)} orthopedists")
            
            if doctors:
                formatted = dr.format_doctor_recommendations(doctors, "Orthopedist")
                print(f"📤 Formatted recommendations length: {len(formatted)} characters")
                print(f"📤 Formatted recommendations (first 300 chars):\n{formatted[:300]}")
                
                if "<table" in formatted:
                    print("✅ Formatted recommendations contain HTML table")
                else:
                    print("❌ Formatted recommendations do NOT contain HTML table")
                    
        except Exception as e2:
            print(f"❌ Error testing DoctorRecommender: {e2}")

if __name__ == "__main__":
    test_fallback_response()

#!/usr/bin/env python3
"""
Debug the specific orthopedist recommendation issue
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def debug_orthopedist_issue():
    print("🐛 DEBUGGING ORTHOPEDIST RECOMMENDATION ISSUE")
    print("=" * 60)
    
    try:
        # Test 1: Extract specialist from the exact response you got
        from src.llm.recommender import MedicalRecommender
        
        recommender = MedicalRecommender()
        
        # Your exact response
        test_response = "I'm sorry to hear that you had an accident and that your hand is in pain. Given the severity of the pain and the fact that you landed on your elbow, I recommend that you see an Orthopedist to evaluate your injury and provide the appropriate treatment. SPECIALIST_RECOMMENDATION: Orthopedist"
        
        print("🔍 Testing specialist extraction:")
        specialist = recommender.extract_specialist_recommendation(test_response)
        print(f"  Extracted specialist: '{specialist}'")
        
        if specialist:
            print("✅ Specialist extraction working")
            
            # Test 2: Check if we can get doctor recommendations for this specialist
            print("\n🔍 Testing doctor recommendations:")
            try:
                doctor_recs = recommender.get_doctor_recommendations(
                    specialist_type=specialist,
                    user_city="Bangalore",
                    sort_by="rating"
                )
                
                print(f"  Doctor recommendations length: {len(doctor_recs)} characters")
                if "<table" in doctor_recs:
                    print("✅ Doctor recommendations contain table")
                    print(f"  Preview: {doctor_recs[:200]}...")
                else:
                    print("❌ Doctor recommendations do NOT contain table")
                    print(f"  Content: {doctor_recs}")
                    
            except Exception as e:
                print(f"❌ Error getting doctor recommendations: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("❌ Specialist extraction failed")
            
        # Test 3: Test doctor recommender mapping directly
        print("\n🔍 Testing doctor recommender mapping:")
        from doctor_recommender import DoctorRecommender
        
        dr = DoctorRecommender()
        dr.load_doctors_data()
        
        # Test mapping
        mapped_specialty = dr.find_specialty_match("Orthopedist")
        print(f"  'Orthopedist' maps to: '{mapped_specialty}'")
        
        mapped_specialty2 = dr.find_specialty_match("orthopedist")
        print(f"  'orthopedist' maps to: '{mapped_specialty2}'")
        
        if mapped_specialty:
            doctors = dr.recommend_doctors(mapped_specialty, "Bangalore", limit=3, sort_by="rating")
            print(f"  Found {len(doctors)} doctors for '{mapped_specialty}'")
            
            if doctors:
                formatted = dr.format_doctor_recommendations(doctors, "Orthopedist")
                print(f"  Formatted response length: {len(formatted)} characters")
                if "<table" in formatted:
                    print("✅ Formatted response contains table")
                else:
                    print("❌ Formatted response does NOT contain table")
        
        # Test 4: Simulate the full process
        print("\n🔍 Testing full process simulation:")
        
        # Simulate removing SPECIALIST_RECOMMENDATION line
        import re
        cleaned_response = re.sub(r"SPECIALIST_RECOMMENDATION:.*", "", test_response, flags=re.IGNORECASE).strip()
        print(f"  Cleaned response: '{cleaned_response}'")
        
        if specialist:
            doctor_recs = recommender.get_doctor_recommendations(
                specialist_type=specialist,
                user_city="Bangalore",
                sort_by="rating"
            )
            
            final_response = cleaned_response + "\n\n" + doctor_recs
            print(f"  Final response length: {len(final_response)} characters")
            
            if "<table" in final_response:
                print("✅ Final response contains table")
            else:
                print("❌ Final response does NOT contain table")
                
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_orthopedist_issue()

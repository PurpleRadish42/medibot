#!/usr/bin/env python3
"""
Quick test to debug why doctor recommendations aren't showing
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "llm"))

def test_specialist_recommendation():
    print("🔬 Testing Specialist Recommendation Processing")
    print("=" * 60)
    
    # Import here to avoid path issues
    from src.llm.recommender import MedicalRecommender
    
    recommender = MedicalRecommender()
    
    # Test the extract_specialist_recommendation method
    test_response = "Thank you for sharing that your back pain is quite severe at an 8.5. Given the intensity of your pain, it's important to seek medical attention. I recommend that you see an Orthopedist to evaluate your back pain and determine the appropriate treatment. SPECIALIST_RECOMMENDATION: Orthopedist"
    
    print("🧪 Testing specialist extraction...")
    specialist = recommender.extract_specialist_recommendation(test_response)
    print(f"Extracted specialist: '{specialist}'")
    
    if specialist:
        print("✅ Specialist extraction working!")
        
        # Test doctor recommendations
        print("\n🏥 Testing doctor recommendations...")
        try:
            doctor_recs = recommender.get_doctor_recommendations(
                specialist, 
                user_city="Bangalore", 
                sort_by="rating"
            )
            
            print(f"Doctor recommendations length: {len(doctor_recs)}")
            print(f"First 200 chars: {doctor_recs[:200]}...")
            
            if "Dr." in doctor_recs or "<table" in doctor_recs:
                print("✅ Doctor recommendations working!")
            else:
                print("❌ Doctor recommendations not working properly")
                
        except Exception as e:
            print(f"❌ Error getting doctor recommendations: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Specialist extraction not working!")
    
    print("\n" + "="*60)
    print("🔄 Testing full generate_response...")
    
    # Test the full flow
    history = [
        ("I have back pain", "I'm sorry to hear that you're experiencing back pain. To assist you better, could you please tell me how long you have been experiencing this pain?"),
        ("yes", "Thank you for your response. It seems there was a misunderstanding, as I didn't receive the details about your pain's severity."),
        ("8.5", "Thank you for sharing that your back pain is quite severe at an 8.5. Given the intensity of your pain, it's important to seek medical attention. I recommend that you see an Orthopedist to evaluate your back pain and determine the appropriate treatment. SPECIALIST_RECOMMENDATION: Orthopedist")
    ]
    
    try:
        response = recommender.generate_response(
            history=history,
            message="show me doctors",
            user_city="Bangalore",
            sort_preference="rating"
        )
        
        print("📝 Full response:")
        print(response)
        
        if "Dr." in response or "<table" in response:
            print("\n✅ Full flow working - doctor recommendations included!")
        else:
            print("\n❌ Full flow not working - no doctor recommendations")
            
    except Exception as e:
        print(f"❌ Error in full generate_response: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specialist_recommendation()

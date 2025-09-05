#!/usr/bin/env python3
"""
Quick test of the fixed sorting implementation
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def test_sorting():
    print("🧪 Testing Fixed Doctor Sorting")
    print("=" * 50)
    
    recommender = DoctorRecommender()
    recommender.load_data()
    
    # Test all three sorting methods
    print("\n1. 🏥 Testing Rating-based sorting:")
    doctors_rating = recommender.find_doctors("cardiologist", city="Bangalore", sort_by="rating", limit=3)
    
    print("\n2. 📍 Testing Location-based sorting (Koramangala):")
    doctors_location = recommender.find_doctors("cardiologist", city="Bangalore", sort_by="location", 
                                               user_lat=12.9352, user_lng=77.6245, limit=3)
    
    print("\n3. 🎓 Testing Experience-based sorting:")
    doctors_experience = recommender.find_doctors("cardiologist", city="Bangalore", sort_by="experience", limit=3)
    
    print("\n✅ All sorting methods completed successfully!")
    
    # Check if we get different results (which is expected)
    rating_names = [doc['name'] for doc in doctors_rating]
    location_names = [doc['name'] for doc in doctors_location]
    experience_names = [doc['name'] for doc in doctors_experience]
    
    print(f"\n📊 Result Analysis:")
    print(f"Rating sort first doctor: {rating_names[0] if rating_names else 'None'}")
    print(f"Location sort first doctor: {location_names[0] if location_names else 'None'}")
    print(f"Experience sort first doctor: {experience_names[0] if experience_names else 'None'}")
    
    if rating_names != location_names or rating_names != experience_names:
        print("✅ Different sorting methods return different results - GOOD!")
    else:
        print("⚠️ All sorting methods return same results - might need investigation")

if __name__ == "__main__":
    test_sorting()

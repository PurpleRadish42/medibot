#!/usr/bin/env python3
"""
Quick test of the sorting functionality after the fix
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def test_simple_sorting():
    print("🧪 Testing Simple Doctor Sorting (Fixed)")
    print("=" * 50)
    
    recommender = DoctorRecommender()
    recommender.load_doctors_data()
    
    print("\n1. 🏥 Rating-based sorting:")
    rating_results = recommender.recommend_doctors("cardiologist", city="Bangalore", sort_by="rating", limit=3)
    for i, doc in enumerate(rating_results, 1):
        print(f"  {i}. {doc['name']} - {doc['rating']}")
    
    print("\n2. 🎓 Experience-based sorting:")
    exp_results = recommender.recommend_doctors("cardiologist", city="Bangalore", sort_by="experience", limit=3)
    for i, doc in enumerate(exp_results, 1):
        print(f"  {i}. {doc['name']} - {doc['experience_years']} years")
    
    print("\n3. 📍 Location-based sorting (from Koramangala):")
    loc_results = recommender.recommend_doctors("cardiologist", city="Bangalore", sort_by="location", 
                                          user_lat=12.9352, user_lng=77.6245, limit=3)
    for i, doc in enumerate(loc_results, 1):
        distance = doc.get('distance', 'N/A')
        print(f"  {i}. {doc['name']} - {distance}")
    
    print("\n✅ All sorting tests completed!")

if __name__ == "__main__":
    test_simple_sorting()

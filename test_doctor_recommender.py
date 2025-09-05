#!/usr/bin/env python3
"""
Test the doctor recommender directly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from doctor_recommender import DoctorRecommender

def test_doctor_recommender():
    """Test doctor recommendations"""
    print("🧪 Testing Doctor Recommender...")
    
    try:
        # Initialize doctor recommender
        dr = DoctorRecommender()
        
        print("\n1. Testing orthopedist search in Bangalore:")
        orthopedists = dr.recommend_doctors("orthopedist", "Bangalore", limit=5)
        print(f"   Found {len(orthopedists)} orthopedists")
        
        if orthopedists:
            for i, doc in enumerate(orthopedists[:3], 1):
                print(f"   {i}. Dr. {doc.get('name', 'Unknown')} - {doc.get('specialty', 'Unknown')} - {doc.get('city', 'Unknown')}")
        
        print("\n2. Testing dermatologist search in Bangalore:")
        dermatologists = dr.recommend_doctors("dermatologist", "Bangalore", limit=5)
        print(f"   Found {len(dermatologists)} dermatologists")
        
        if dermatologists:
            for i, doc in enumerate(dermatologists[:3], 1):
                print(f"   {i}. Dr. {doc.get('name', 'Unknown')} - {doc.get('specialty', 'Unknown')} - {doc.get('city', 'Unknown')}")
        
        print("\n3. Testing orthopedist search in ALL cities:")
        all_orthopedists = dr.recommend_doctors("orthopedist", None, limit=5)
        print(f"   Found {len(all_orthopedists)} orthopedists total")
        
        print("\n4. Testing specialty mapping:")
        mapped_specialty = dr.find_specialty_match("orthopedist")
        print(f"   'orthopedist' maps to: '{mapped_specialty}'")
        
        # Check if we have the data
        if dr.doctors_df is not None:
            print(f"\n5. Database stats:")
            print(f"   Total doctors: {len(dr.doctors_df)}")
            orthopedist_count = len(dr.doctors_df[dr.doctors_df['speciality'] == 'orthopedist'])
            print(f"   Orthopedists in database: {orthopedist_count}")
            bangalore_orthopedists = len(dr.doctors_df[
                (dr.doctors_df['speciality'] == 'orthopedist') & 
                (dr.doctors_df['city'].str.contains('Bangalore', case=False, na=False))
            ])
            print(f"   Orthopedists in Bangalore: {bangalore_orthopedists}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_doctor_recommender()

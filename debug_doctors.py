#!/usr/bin/env python3
"""
Debug script to check doctor data and columns
"""

from doctor_recommender import DoctorRecommender

# Initialize doctor recommender
dr = DoctorRecommender()

# Get first few doctors to see data structure
print("=== DATABASE COLUMNS ===")
print("Columns in dataframe:", list(dr.doctors_df.columns))
print()

print("=== FIRST 3 DOCTORS ===")
for i, (idx, doctor) in enumerate(dr.doctors_df.head(3).iterrows()):
    print(f"\nDoctor {i+1}:")
    for col in ['name', 'specialty', 'speciality', 'degree', 'year_of_experience', 'consultation_fee', 'dp_score']:
        if col in doctor:
            print(f"  {col}: '{doctor[col]}'")
        else:
            print(f"  {col}: MISSING")

# Test orthopedist search
print("\n=== ORTHOPEDIST SEARCH TEST ===")
orthopedists = dr.recommend_doctors("orthopedist", limit=2)
print(f"Found {len(orthopedists)} orthopedists")

if orthopedists:
    print("\nFirst orthopedist:")
    for key, value in orthopedists[0].items():
        print(f"  {key}: '{value}'")

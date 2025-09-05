#!/usr/bin/env python3
"""
Test script to verify API response format
"""
import requests
import json

# Test the doctor recommendation directly
from doctor_recommender import DoctorRecommender

dr = DoctorRecommender()

# Get orthopedist recommendations
orthopedists = dr.recommend_doctors("orthopedist", limit=3)
print("=== DIRECT DOCTOR RECOMMENDATIONS ===")
print(f"Found {len(orthopedists)} orthopedists")

if orthopedists:
    print("\nFirst doctor:")
    for key, value in orthopedists[0].items():
        print(f"  {key}: {value}")

# Test the HTML formatting
print("\n=== HTML FORMATTING ===")
html_table = dr.format_doctor_recommendations(orthopedists, "Orthopedist")
print("HTML table length:", len(html_table))
print("HTML preview (first 500 chars):")
print(html_table[:500])

# Check if HTML contains actual data
if "Dr." in html_table and "orthopedist" in html_table.lower():
    print("✅ HTML table contains doctor names and specialties")
else:
    print("❌ HTML table missing doctor data")

# Test the enhanced medical analysis
print("\n=== ENHANCED ANALYSIS TEST ===")
try:
    from src.ai.enhanced_medical_analysis import EnhancedMedicalAnalysis
    
    # Create a dummy image (small bytes)
    dummy_image = b"dummy_image_data"
    
    enhanced_analyzer = EnhancedMedicalAnalysis()
    
    # Test with orthopedic context
    result = enhanced_analyzer.analyze_with_doctor_integration(
        image_data=dummy_image,
        image_type='bone',
        symptoms='fracture in wrist',
        context='X-ray showing broken bone',
        user_city='Bangalore'
    )
    
    print("Enhanced analysis success:", result.get('success'))
    if result.get('success'):
        doctors = result['enhanced_analysis']['doctor_recommendations']['primary_doctors']
        print(f"Found {len(doctors)} doctors in enhanced analysis")
        
except Exception as e:
    print(f"Enhanced analysis error: {e}")

print("\n=== TEST COMPLETE ===")

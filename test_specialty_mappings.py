#!/usr/bin/env python3
"""
Test script to verify specialty mappings work correctly
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime, timezone

# Add current directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_specialty_mappings():
    """Test all specialty mappings"""
    print("🧪 Testing Specialty Mappings")
    print("=" * 50)
    
    try:
        # Import the doctor recommender
        from doctor_recommender import DoctorRecommender
        
        # Create instance
        dr = DoctorRecommender()
        
        # Test cases: (input, expected_database_specialty)
        test_cases = [
            # General physician variations
            ("general physician", "general-physician"),
            ("general practitioner", "general-physician"),
            ("gp", "general-physician"),
            ("family doctor", "general-physician"),
            ("primary care", "general-physician"),
            
            # Surgeon variations
            ("cardiac surgeon", "cardiac-surgeon"),
            ("plastic surgeon", "plastic-surgeon"),
            ("vascular surgeon", "vascular-surgeon"),
            
            # ENT variations
            ("ent specialist", "ent-specialist"),
            ("ent", "ent-specialist"),
            ("ear nose throat", "ent-specialist"),
            
            # Standard specialties (should match exactly)
            ("neurologist", "neurologist"),
            ("cardiologist", "cardiologist"),
            ("dermatologist", "dermatologist"),
            ("orthopedist", "orthopedist"),
            ("pediatrician", "pediatrician"),
            ("psychiatrist", "psychiatrist"),
            ("gastroenterologist", "gastroenterologist"),
            ("gynecologist", "gynecologist"),
            ("urologist", "urologist"),
            ("pulmonologist", "pulmonologist"),
            ("rheumatologist", "rheumatologist"),
            ("endocrinologist", "endocrinologist"),
            ("nephrologist", "nephrologist"),
            ("oncologist", "oncologist"),
            ("ophthalmologist", "ophthalmologist"),
            ("dentist", "dentist"),
            ("anesthesiologist", "anesthesiologist"),
            ("neurosurgeon", "neurosurgeon"),
            ("pathologist", "pathologist"),
            ("radiologist", "radiologist"),
            ("sexologist", "sexologist"),
            ("surgeon", "surgeon"),
            ("trichologist", "trichologist"),
            ("unani", "unani"),
            ("ayurveda", "ayurveda"),
        ]
        
        print(f"📋 Testing {len(test_cases)} specialty mappings...")
        
        passed = 0
        failed = 0
        
        for input_specialty, expected in test_cases:
            result = dr.find_specialty_match(input_specialty)
            
            if result == expected:
                print(f"  ✅ '{input_specialty}' → '{result}'")
                passed += 1
            else:
                print(f"  ❌ '{input_specialty}' → '{result}' (expected: '{expected}')")
                failed += 1
        
        print(f"\n📊 Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All specialty mappings work correctly!")
            return True
        else:
            print(f"❌ {failed} specialty mappings failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_specialties():
    """Test that we can find all database specialties"""
    print("\n🧪 Testing Database Specialty Discovery")
    print("=" * 50)
    
    try:
        from doctor_recommender import DoctorRecommender
        
        dr = DoctorRecommender()
        
        if dr.doctors_df is None:
            print("❌ No doctor data loaded")
            return False
        
        # Get all unique specialties from database
        available_specialties = dr.doctors_df['speciality'].unique()
        print(f"📋 Found {len(available_specialties)} specialties in database:")
        
        for specialty in sorted(available_specialties):
            count = len(dr.doctors_df[dr.doctors_df['speciality'] == specialty])
            print(f"  • {specialty} ({count} doctors)")
        
        # Test that we can find each specialty
        print(f"\n🔍 Testing specialty matching for all database specialties...")
        
        all_found = True
        for specialty in available_specialties:
            result = dr.find_specialty_match(specialty)
            if result != specialty:
                print(f"  ❌ '{specialty}' → '{result}' (should match itself)")
                all_found = False
            else:
                print(f"  ✅ '{specialty}' → '{result}'")
        
        if all_found:
            print("🎉 All database specialties can be found!")
            return True
        else:
            print("❌ Some database specialties could not be found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_doctor_recommendations():
    """Test that doctor recommendations actually work"""
    print("\n🧪 Testing Doctor Recommendations")
    print("=" * 50)
    
    try:
        from doctor_recommender import DoctorRecommender
        
        dr = DoctorRecommender()
        
        # Test general physician recommendation
        print("📝 Testing general physician recommendation...")
        doctors = dr.recommend_doctors("general-physician", "Bangalore", limit=3, sort_by="rating")
        
        if not doctors:
            print("❌ No general physicians found")
            return False
        
        print(f"  ✅ Found {len(doctors)} general physicians")
        
        # Check that all returned doctors are general physicians
        for doctor in doctors:
            if doctor['specialty'] != 'general-physician':
                print(f"  ❌ Wrong specialty: {doctor['specialty']} (expected: general-physician)")
                return False
        
        print("  ✅ All returned doctors are general physicians")
        
        # Test neurologist recommendation
        print("\n📝 Testing neurologist recommendation...")
        doctors = dr.recommend_doctors("neurologist", "Bangalore", limit=3, sort_by="rating")
        
        if not doctors:
            print("❌ No neurologists found")
            return False
        
        print(f"  ✅ Found {len(doctors)} neurologists")
        
        # Check that all returned doctors are neurologists
        for doctor in doctors:
            if doctor['specialty'] != 'neurologist':
                print(f"  ❌ Wrong specialty: {doctor['specialty']} (expected: neurologist)")
                return False
        
        print("  ✅ All returned doctors are neurologists")
        
        print("\n🎉 Doctor recommendations work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Specialty Mapping Verification")
    print("=" * 70)
    
    # Test specialty mappings
    mapping_success = test_specialty_mappings()
    
    # Test database specialties
    db_success = test_database_specialties()
    
    # Test doctor recommendations
    rec_success = test_doctor_recommendations()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    if mapping_success and db_success and rec_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Specialty mappings work correctly")
        print("✅ Database specialties can be found")
        print("✅ Doctor recommendations work")
        print("✅ Fixed 'general physician' → 'general-physician' mapping")
        print("✅ Fixed all surgeon mappings with hyphens")
        print("✅ Enhanced matching logic with multiple strategies")
        print("✅ No more 'No matching specialty found' errors!")
        
        print("\n📋 WHAT WAS FIXED:")
        print("1. ✅ Added 'general physician' → 'general-physician' mapping")
        print("2. ✅ Fixed surgeon mappings: 'cardiac surgeon' → 'cardiac-surgeon'")
        print("3. ✅ Fixed ENT mappings: 'ent specialist' → 'ent-specialist'")
        print("4. ✅ Enhanced matching logic with 4 strategies")
        print("5. ✅ Updated main.py to use correct specialty names")
        print("6. ✅ Added comprehensive specialty mappings")
        
        print("\n📋 EXPECTED BEHAVIOR NOW:")
        print("1. Ask for doctor recommendations")
        print("2. Bot shows location prompt")
        print("3. Choose location preference")
        print("4. Doctor table appears with correct specialty")
        print("5. No more 'No matching specialty found' errors")
        print("6. All specialties work: general physician, surgeons, etc.")
        
    else:
        print("❌ SOME TESTS FAILED!")
        if not mapping_success:
            print("❌ Specialty mappings test failed")
        if not db_success:
            print("❌ Database specialties test failed")
        if not rec_success:
            print("❌ Doctor recommendations test failed")
        print("\n🔧 Please check the error messages above and fix the issues")
    
    print("=" * 70)

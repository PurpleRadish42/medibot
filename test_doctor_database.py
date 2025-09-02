#!/usr/bin/env python3
"""
Test script for doctor database functionality
Run this after setting up MySQL and migrating data
"""

import os
import sys
from doctor_recommender import DoctorRecommender

def test_database_functionality():
    """Test all database functionality"""
    print("🧪 Testing Doctor Database Functionality")
    print("=" * 50)
    
    # Test 1: Initialize recommender
    print("\n1️⃣ Testing Initialization...")
    recommender = DoctorRecommender(use_database=True)
    
    if recommender.use_database:
        print("✅ Database mode active")
    else:
        print("📂 CSV fallback mode (database not available)")
    
    # Test 2: Get statistics
    print("\n2️⃣ Testing Statistics...")
    stats = recommender.get_statistics()
    
    if "error" in stats:
        print(f"❌ Statistics error: {stats['error']}")
    else:
        print(f"✅ Data source: {stats['data_source']}")
        print(f"📊 Total doctors: {stats['total_doctors']}")
        print(f"🏥 Unique specialties: {stats['unique_specialties']}")
        print(f"🏙️ Unique cities: {stats['unique_cities']}")
        print(f"💰 Average consultation fee: ₹{stats['average_consultation_fee']}")
        
        print("\n🔝 Top Specialties:")
        for specialty, count in list(stats['top_specialties'].items())[:5]:
            print(f"   • {specialty}: {count} doctors")
    
    # Test 3: Specialty mapping
    print("\n3️⃣ Testing Specialty Mapping...")
    test_specialties = [
        "cardiologist",
        "eye specialist", 
        "general practitioner",
        "dermatologist"
    ]
    
    for specialty in test_specialties:
        matched = recommender.find_specialty_match(specialty)
        if matched:
            print(f"✅ '{specialty}' → '{matched}'")
        else:
            print(f"❌ No match for '{specialty}'")
    
    # Test 4: Doctor recommendations
    print("\n4️⃣ Testing Doctor Recommendations...")
    test_cases = [
        ("cardiologist", "Bangalore", 3),
        ("ophthalmologist", None, 5),
        ("general practitioner", "Mumbai", 2)
    ]
    
    for specialist, city, limit in test_cases:
        print(f"\n   🔍 Testing: {specialist}" + (f" in {city}" if city else "") + f" (limit: {limit})")
        
        doctors = recommender.recommend_doctors(specialist, city, limit)
        
        if doctors:
            print(f"   ✅ Found {len(doctors)} doctors:")
            for i, doctor in enumerate(doctors, 1):
                name = doctor.get('name', 'Unknown')
                specialty = doctor.get('specialty', 'Unknown')
                city_name = doctor.get('city', 'Unknown')
                rating = doctor.get('rating', 0)
                experience = doctor.get('experience', 0)
                fee = doctor.get('fee', 0)
                
                print(f"     {i}. Dr. {name}")
                print(f"        Specialty: {specialty}")
                print(f"        Location: {city_name}")
                print(f"        Rating: {rating}/100, Experience: {experience} years")
                print(f"        Consultation Fee: ₹{fee}")
        else:
            print(f"   ❌ No {specialist} found")
    
    # Test 5: Sorting options
    print("\n5️⃣ Testing Sorting Options...")
    sort_options = ["rating", "experience", "fee"]
    
    for sort_by in sort_options:
        print(f"\n   📊 Testing sort by {sort_by}:")
        doctors = recommender.recommend_doctors("cardiologist", None, 3, sort_by)
        
        if doctors:
            for i, doctor in enumerate(doctors, 1):
                name = doctor.get('name', 'Unknown')
                rating = doctor.get('rating', 0)
                experience = doctor.get('experience', 0)
                fee = doctor.get('fee', 0)
                
                print(f"     {i}. Dr. {name} (Rating: {rating}, Exp: {experience}y, Fee: ₹{fee})")
        else:
            print(f"     ❌ No results for {sort_by} sorting")
    
    print(f"\n✅ Database functionality test completed!")
    return True

def test_performance_comparison():
    """Compare database vs CSV performance"""
    print("\n🚀 Performance Comparison Test")
    print("=" * 30)
    
    import time
    
    # Test database mode
    print("\n🔹 Testing Database Mode...")
    db_recommender = DoctorRecommender(use_database=True)
    
    if db_recommender.use_database:
        start_time = time.time()
        db_results = db_recommender.recommend_doctors("cardiologist", "Bangalore", 10)
        db_time = time.time() - start_time
        print(f"   Database query time: {db_time:.4f} seconds")
        print(f"   Results: {len(db_results)} doctors")
    else:
        print("   ⚠️ Database not available")
    
    # Test CSV mode
    print("\n📂 Testing CSV Mode...")
    csv_recommender = DoctorRecommender(use_database=False)
    
    start_time = time.time()
    csv_results = csv_recommender.recommend_doctors("cardiologist", "Bangalore", 10)
    csv_time = time.time() - start_time
    print(f"   CSV processing time: {csv_time:.4f} seconds")
    print(f"   Results: {len(csv_results)} doctors")
    
    # Compare
    if db_recommender.use_database:
        speedup = csv_time / db_time if db_time > 0 else 0
        print(f"\n📈 Performance Summary:")
        print(f"   Database: {db_time:.4f}s")
        print(f"   CSV: {csv_time:.4f}s")
        if speedup > 1:
            print(f"   🚀 Database is {speedup:.1f}x faster")
        else:
            print(f"   📂 CSV is {1/speedup:.1f}x faster")

if __name__ == "__main__":
    try:
        test_database_functionality()
        test_performance_comparison()
        
        print(f"\n🎉 All tests completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
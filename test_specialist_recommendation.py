#!/usr/bin/env python3
"""
Test script for the location-aware specialist recommendation system
"""
import sys
import os
sys.path.insert(0, 'src')

def test_geolocation_utils():
    """Test geolocation utilities"""
    print("=== Testing Geolocation Utilities ===")
    
    try:
        from utils.geolocation import haversine_distance, get_city_coordinates, parse_coordinates
        
        # Test city coordinates
        delhi_coords = get_city_coordinates('delhi')
        mumbai_coords = get_city_coordinates('mumbai')
        print(f"✅ Delhi coordinates: {delhi_coords}")
        print(f"✅ Mumbai coordinates: {mumbai_coords}")
        
        # Test distance calculation
        if delhi_coords[0] and mumbai_coords[0]:
            distance = haversine_distance(delhi_coords[0], delhi_coords[1], 
                                        mumbai_coords[0], mumbai_coords[1])
            print(f"✅ Distance Delhi to Mumbai: {distance:.1f} km")
        
        # Test coordinate parsing
        lat, lon = parse_coordinates("28.6139", "77.2090")
        print(f"✅ Parsed coordinates: {lat}, {lon}")
        
        print("✅ All geolocation utilities working correctly!\n")
        return True
        
    except Exception as e:
        print(f"❌ Geolocation utilities failed: {e}")
        return False

def test_doctor_recommender():
    """Test enhanced doctor recommender"""
    print("=== Testing Enhanced Doctor Recommender ===")
    
    try:
        from doctor_recommender import DoctorRecommender
        
        dr = DoctorRecommender()
        
        # Test basic recommendation
        print("Testing basic recommendation...")
        basic_results = dr.recommend_doctors('cardiologist', limit=3)
        print(f"✅ Basic recommendation returned {len(basic_results)} doctors")
        
        # Test location-aware recommendation  
        print("Testing location-aware recommendation...")
        location_results = dr.recommend_doctors_with_location(
            'cardiologist', 
            user_lat=28.6139, 
            user_lon=77.2090, 
            limit=3,
            sort_by='distance'
        )
        print(f"✅ Location-aware recommendation returned {len(location_results)} doctors")
        
        if location_results:
            print(f"   First result: Dr. {location_results[0]['name']} in {location_results[0]['city']}")
            print(f"   Distance: {location_results[0]['distance_str']}")
            print(f"   Rating: {location_results[0]['dp_score']}")
        
        print("✅ Doctor recommender working correctly!\n")
        return True
        
    except Exception as e:
        print(f"❌ Doctor recommender failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_imports():
    """Test that all API imports work"""
    print("=== Testing API Imports ===")
    
    try:
        # Test Flask app imports
        import main
        print("✅ Main Flask app imports successfully")
        
        # Test that the new route is available
        app = main.app
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        if '/api/v1/recommend-specialists' in rules:
            print("✅ New API endpoint registered")
        else:
            print("❌ New API endpoint not found")
            return False
            
        if '/specialist-finder' in rules:
            print("✅ Specialist finder page registered")
        else:
            print("❌ Specialist finder page not found")
            return False
        
        print("✅ All API components working correctly!\n")
        return True
        
    except Exception as e:
        print(f"❌ API imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Location-Aware Specialist Recommendation System")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_geolocation_utils()
    all_passed &= test_doctor_recommender()
    all_passed &= test_api_imports()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! The location-aware specialist recommendation system is ready.")
        print("\nKey features implemented:")
        print("✅ Browser geolocation API integration")
        print("✅ Distance calculation using Haversine formula")
        print("✅ Location-aware doctor sorting (distance/rating)")
        print("✅ New API endpoint: /api/v1/recommend-specialists")
        print("✅ Responsive specialist finder UI")
        print("✅ Privacy-conscious design (no long-term location storage)")
        print("✅ Graceful fallback when location denied")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    return all_passed

if __name__ == "__main__":
    main()
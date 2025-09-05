"""
Debug and test the location-based doctor recommendations
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def test_location_feature():
    """Test location-based doctor recommendations"""
    print("🧪 Testing Location-Based Doctor Recommendations")
    print("=" * 60)
    
    # Initialize recommender
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        print(f"✅ Data loaded from: {recommender.data_source}")
        
        # Test data - some real Bangalore coordinates
        test_locations = [
            {"name": "Koramangala", "lat": 12.9352, "lng": 77.6245},
            {"name": "Whitefield", "lat": 12.9698, "lng": 77.7500},
            {"name": "Electronic City", "lat": 12.8456, "lng": 77.6603}
        ]
        
        for location in test_locations:
            print(f"\n🏠 Testing from {location['name']} ({location['lat']:.4f}, {location['lng']:.4f})")
            print("-" * 50)
            
            # Test rating-based sorting (default)
            print("\n⭐ Rating-based sorting:")
            doctors_rating = recommender.recommend_doctors(
                "cardiologist", 
                "Bangalore", 
                limit=3, 
                sort_by="rating",
                user_lat=location['lat'],
                user_lng=location['lng']
            )
            
            if doctors_rating:
                for i, doctor in enumerate(doctors_rating, 1):
                    print(f"  {i}. Dr. {doctor['name']} - {doctor['rating']} - {doctor['location']}")
            
            # Test location-based sorting
            print("\n📍 Location-based sorting:")
            doctors_location = recommender.recommend_doctors(
                "cardiologist", 
                "Bangalore", 
                limit=3, 
                sort_by="location",
                user_lat=location['lat'],
                user_lng=location['lng']
            )
            
            if doctors_location:
                for i, doctor in enumerate(doctors_location, 1):
                    # Calculate distance for display
                    doctor_lat = float(doctor.get('latitude', 0)) if doctor.get('latitude') else 0
                    doctor_lng = float(doctor.get('longitude', 0)) if doctor.get('longitude') else 0
                    
                    distance = recommender.calculate_distance(
                        location['lat'], location['lng'], 
                        doctor_lat, doctor_lng
                    )
                    
                    print(f"  {i}. Dr. {doctor['name']} - {distance:.2f}km - {doctor['location']} - {doctor['rating']}")
            
            # Test experience-based sorting
            print("\n🎓 Experience-based sorting:")
            doctors_experience = recommender.recommend_doctors(
                "cardiologist", 
                "Bangalore", 
                limit=3, 
                sort_by="experience",
                user_lat=location['lat'],
                user_lng=location['lng']
            )
            
            if doctors_experience:
                for i, doctor in enumerate(doctors_experience, 1):
                    print(f"  {i}. Dr. {doctor['name']} - {doctor['experience_years']} years - {doctor['rating']} - {doctor['location']}")
        
        # Test coordinate data quality
        print(f"\n🗺️ Coordinate Data Quality Analysis:")
        print("=" * 40)
        
        # Check how many doctors have valid coordinates
        valid_coords = 0
        total_doctors = len(recommender.doctors_df)
        
        for _, doctor in recommender.doctors_df.iterrows():
            lat = doctor.get('latitude')
            lng = doctor.get('longitude')
            if lat and lng and not (pd.isna(lat) or pd.isna(lng)):
                try:
                    float(lat)
                    float(lng)
                    valid_coords += 1
                except (ValueError, TypeError):
                    pass
        
        print(f"📊 Doctors with valid coordinates: {valid_coords}/{total_doctors} ({valid_coords/total_doctors*100:.1f}%)")
        
        if valid_coords < total_doctors * 0.8:  # Less than 80% have coordinates
            print("⚠️ Warning: Many doctors don't have valid coordinates. Location-based sorting may not work optimally.")
        else:
            print("✅ Good coordinate coverage for location-based sorting.")
            
    else:
        print("❌ Failed to load doctor data")

if __name__ == "__main__":
    import pandas as pd
    test_location_feature()

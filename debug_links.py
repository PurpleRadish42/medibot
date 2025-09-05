"""
Debug the Profile URL and Google Maps link data
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def debug_links():
    """Debug the Profile URL and Google Maps link data"""
    print("🔍 Debugging Profile and Maps Links")
    print("=" * 50)
    
    # Initialize recommender
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        print(f"✅ Data loaded from: {recommender.data_source}")
        
        # Get some cardiologist recommendations
        doctors = recommender.recommend_doctors("cardiologist", "Bangalore", limit=3)
        
        if doctors:
            print(f"✅ Found {len(doctors)} doctors")
            print("\n🔗 Link Data Analysis:")
            
            for i, doctor in enumerate(doctors, 1):
                print(f"\n{i}. Dr. {doctor['name']}")
                print(f"   Profile URL: {doctor['profile_url']}")
                print(f"   Profile URL Type: {type(doctor['profile_url'])}")
                print(f"   Profile URL Length: {len(str(doctor['profile_url']))}")
                print(f"   Profile URL Valid: {doctor['profile_url'] and doctor['profile_url'] != 'nan' and doctor['profile_url'] != ''}")
                
                print(f"   Google Map Link: {doctor['google_map_link']}")
                print(f"   Google Map Link Type: {type(doctor['google_map_link'])}")
                print(f"   Google Map Link Length: {len(str(doctor['google_map_link']))}")
                print(f"   Google Map Link Valid: {doctor['google_map_link'] and doctor['google_map_link'] != 'nan' and doctor['google_map_link'] != ''}")
                
        else:
            print("❌ No doctors found")
    else:
        print("❌ Failed to load doctor data")

if __name__ == "__main__":
    debug_links()

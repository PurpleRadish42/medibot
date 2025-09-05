"""
Test the new DoctorRecommender with database fallback functionality
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender
from src.database.connection import DatabaseConnection

def test_database_connection():
    """Test database connection"""
    print("🔄 Testing database connection...")
    db = DatabaseConnection()
    result = db.test_connection()
    
    print(f"Database: {result['database']}")
    print(f"Host: {result['host']}")
    print(f"Connected: {result['connected']}")
    
    if result['connected']:
        print(f"✅ Doctors in database: {result.get('doctors_count', 0)}")
    else:
        print(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
    
    return result['connected']

def test_doctor_recommender():
    """Test the DoctorRecommender with database fallback"""
    print("\n🏥 Testing DoctorRecommender...")
    print("=" * 50)
    
    # Initialize recommender
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        print(f"✅ Data loaded successfully from: {recommender.data_source}")
        
        # Get data source info
        info = recommender.get_data_source_info()
        print(f"📊 Total records: {info['total_records']}")
        
        if info['source'] == 'csv':
            print(f"📁 CSV path: {info['csv_path']}")
        elif info['source'] == 'database':
            print(f"🗄️ Database: {info['database_config']['host']}/{info['database_config']['database']}")
        
        # Test some recommendations
        test_cases = [
            ("cardiologist", "Bangalore"),
            ("ophthalmologist", "Mumbai"),
            ("general practitioner", None)
        ]
        
        print("\n🔍 Testing doctor recommendations...")
        for specialist, city in test_cases:
            print(f"\n➤ Searching for: {specialist}" + (f" in {city}" if city else ""))
            doctors = recommender.recommend_doctors(specialist, city, limit=3)
            
            if doctors:
                print(f"  ✅ Found {len(doctors)} doctors")
                for i, doctor in enumerate(doctors, 1):
                    print(f"    {i}. Dr. {doctor['name']} - {doctor['specialty']} - {doctor['city']}")
            else:
                print(f"  ❌ No {specialist} found")
        
        # Get statistics
        print("\n📊 Database Statistics:")
        stats = recommender.get_statistics()
        for key, value in stats.items():
            if key not in ['top_cities', 'top_specialties']:
                print(f"  • {key}: {value}")
        
    else:
        print("❌ Failed to load data from both database and CSV")

def main():
    """Main test function"""
    print("🧪 MediBot Database Fallback Test")
    print("=" * 50)
    
    # Test database connection first
    db_connected = test_database_connection()
    
    if not db_connected:
        print("\n⚠️ Database connection failed - CSV fallback will be used")
    
    # Test doctor recommender
    test_doctor_recommender()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()

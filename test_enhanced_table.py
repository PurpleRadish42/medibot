"""
Test the enhanced HTML table format with new columns
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def test_html_table():
    """Test the enhanced HTML table format"""
    print("🎨 Testing Enhanced HTML Table Format")
    print("=" * 50)
    
    # Initialize recommender
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        print(f"✅ Data loaded successfully from: {recommender.data_source}")
        
        # Test cardiologist recommendations
        print("\n🔍 Getting cardiologist recommendations...")
        doctors = recommender.recommend_doctors("cardiologist", "Bangalore", limit=3)
        
        if doctors:
            print(f"✅ Found {len(doctors)} doctors")
            
            # Print the data structure to see what we're working with
            print("\n📊 Doctor data structure:")
            for i, doctor in enumerate(doctors, 1):
                print(f"  {i}. Dr. {doctor['name']}")
                print(f"     - Experience: {doctor.get('experience_years', 'N/A')}")
                print(f"     - Fee: {doctor.get('consultation_fee', 'N/A')}")
                print(f"     - Rating: {doctor.get('rating', 'N/A')}")
                print(f"     - Location: {doctor['location']}")
            
            # Generate HTML table
            print("\n🎨 Generating HTML table...")
            html_table = recommender.format_doctor_recommendations(doctors, "Cardiologist")
            
            # Save HTML to file for inspection
            with open("test_table_output.html", "w", encoding="utf-8") as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Doctor Recommendations Test</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Enhanced Doctor Recommendations Table</h1>
        {html_table}
    </div>
</body>
</html>
                """)
            
            print("✅ HTML table saved to 'test_table_output.html'")
            print("🌐 You can open this file in a browser to see the enhanced table")
            
            # Show a preview of the table structure
            print("\n📋 Table includes the following columns:")
            print("  1. # (Number)")
            print("  2. Doctor Name")
            print("  3. Specialty")
            print("  4. Qualification")
            print("  5. Experience (Years)")
            print("  6. Consultation Fee (₹)")
            print("  7. Rating (Stars)")
            print("  8. Location")
            print("  9. Profile Link")
            print("  10. Maps Link")
            
        else:
            print("❌ No cardiologists found")
    else:
        print("❌ Failed to load data")

if __name__ == "__main__":
    test_html_table()

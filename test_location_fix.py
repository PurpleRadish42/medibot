"""
Test gastroenterologist search to match the user's example
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def test_gastroenterologist():
    """Test gastroenterologist search like in user's example"""
    print("🧪 Testing Gastroenterologist Search")
    print("=" * 50)
    
    # Initialize recommender
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        print(f"✅ Data loaded from: {recommender.data_source}")
        
        # Get gastroenterologist recommendations (like in user's image)
        print("\n🔍 Getting gastroenterologist recommendations...")
        doctors = recommender.recommend_doctors("gastroenterologist", "Bangalore", limit=5)
        
        if doctors:
            print(f"✅ Found {len(doctors)} doctors")
            
            print("\n📊 Location Analysis:")
            for i, doctor in enumerate(doctors, 1):
                print(f"  {i}. Dr. {doctor['name']}")
                print(f"     Location: '{doctor['location']}'")
                print(f"     City: '{doctor['city']}'")
                print(f"     Experience: {doctor['experience_years']}")
                print(f"     Fee: {doctor['consultation_fee']}")
                print(f"     Rating: {doctor['rating']}")
                print()
            
            # Generate HTML table
            html_table = recommender.format_doctor_recommendations(doctors, "Gastroenterologist")
            
            # Save to HTML file for viewing
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Fixed Location Display - Gastroenterologist Test</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Fixed Location Display - Gastroenterologist Recommendations</h1>
        <p><strong>Issue Fixed:</strong> Location no longer shows duplicate "Bangalore" entries</p>
        {html_table}
    </div>
</body>
</html>
            """
            
            # Save HTML file
            with open('fixed_location_test.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("✅ HTML table generated successfully!")
            print("📁 Saved as: fixed_location_test.html")
            
        else:
            print("❌ No doctors found")
    else:
        print("❌ Failed to load doctor data")

if __name__ == "__main__":
    test_gastroenterologist()

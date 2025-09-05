"""
Test the new enhanced HTML table format
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def test_html_table():
    """Test the enhanced HTML table format"""
    print("🧪 Testing Enhanced HTML Table Format")
    print("=" * 50)
    
    # Initialize recommender
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        print(f"✅ Data loaded from: {recommender.data_source}")
        
        # Get some cardiologist recommendations
        print("\n🔍 Getting cardiologist recommendations...")
        doctors = recommender.recommend_doctors("cardiologist", "Bangalore", limit=3)
        
        if doctors:
            print(f"✅ Found {len(doctors)} doctors")
            
            # Generate HTML table
            html_table = recommender.format_doctor_recommendations(doctors, "Cardiologist")
            
            # Save to HTML file for viewing
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Doctor Table Test</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
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
        <h1>🏥 Enhanced Doctor Recommendation Table</h1>
        <p><strong>New Features:</strong></p>
        <ul>
            <li>✅ Experience Years column</li>
            <li>✅ Consultation Fee column</li>
            <li>✅ Rating column (with stars)</li>
            <li>❌ Removed DP Score column</li>
            <li>🎨 Better styling and layout</li>
        </ul>
        {html_table}
    </div>
</body>
</html>
            """
            
            # Save HTML file
            with open('enhanced_table_test.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("✅ HTML table generated successfully!")
            print("📁 Saved as: enhanced_table_test.html")
            print("\n📊 Sample doctor data:")
            for i, doctor in enumerate(doctors, 1):
                print(f"  {i}. Dr. {doctor['name']}")
                print(f"     Experience: {doctor['experience_years']}")
                print(f"     Fee: {doctor['consultation_fee']}")
                print(f"     Rating: {doctor['rating']}")
                print(f"     Location: {doctor['city']}")
                print()
            
        else:
            print("❌ No doctors found")
    else:
        print("❌ Failed to load doctor data")

if __name__ == "__main__":
    test_html_table()

"""
Test the HTML table output directly
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doctor_recommender import DoctorRecommender

def test_html_output():
    """Test the HTML table format"""
    print("🧪 Testing HTML Table Output")
    print("=" * 50)
    
    # Initialize recommender
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        print(f"✅ Data loaded from: {recommender.data_source}")
        
        # Get some doctors
        doctors = recommender.recommend_doctors("cardiologist", "Bangalore", limit=2)
        
        if doctors:
            print(f"✅ Found {len(doctors)} doctors")
            
            # Print the doctor data structure
            print("\n📊 Doctor Data Structure:")
            for i, doctor in enumerate(doctors, 1):
                print(f"Doctor {i}:")
                for key, value in doctor.items():
                    print(f"  {key}: {value}")
                print()
            
            # Generate HTML table
            html_table = recommender.format_doctor_recommendations(doctors, "Cardiologist")
            
            # Save to file for inspection
            with open('test_table_output.html', 'w', encoding='utf-8') as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Doctor Table Test</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>Enhanced Doctor Table Test</h1>
    {html_table}
</body>
</html>
                """)
            
            print("✅ HTML table generated and saved to 'test_table_output.html'")
            print("🔍 You can open this file in a browser to see the updated table")
            
            # Print a portion of the HTML to verify structure
            print("\n📋 HTML Table Headers Preview:")
            lines = html_table.split('\n')
            for line in lines:
                if '<th style=' in line:
                    # Extract the header text
                    start = line.find('>') + 1
                    end = line.find('</th>')
                    if start > 0 and end > 0:
                        header_text = line[start:end]
                        print(f"  • {header_text}")
            
        else:
            print("❌ No doctors found")
    else:
        print("❌ Failed to load data")

if __name__ == "__main__":
    test_html_output()

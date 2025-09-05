#!/usr/bin/env python3
"""
Test script to verify medical image analyzer fixes
"""
import requests
import base64
import json

def test_bone_fracture_analysis():
    """Test that bone fracture images recommend orthopedists"""
    
    # Create a simple test image (1x1 pixel PNG)
    # In real usage, this would be a bone fracture X-ray
    test_image_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA60e6kgAAAABJRU5ErkJggg==')
    
    url = 'http://localhost:5000/api/v1/analyze-medical-image'
    
    files = {
        'image': ('test_fracture.png', test_image_data, 'image/png')
    }
    
    data = {
        'image_type': 'xray',
        'user_location': json.dumps({
            'latitude': 12.9716,
            'longitude': 77.5946,
            'city': 'Bangalore'
        })
    }
    
    print("🔬 Testing medical image analysis...")
    print("📸 Uploading test bone fracture image")
    
    try:
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful!")
            print(f"🏥 Recommended specialist: {result.get('specialist_type', 'Unknown')}")
            print(f"📊 Found {len(result.get('doctors', []))} doctors")
            
            # Check if we got orthopedists for bone fracture
            specialist = result.get('specialist_type', '')
            if 'orthopedist' in specialist.lower():
                print("✅ SUCCESS: Correctly recommended Orthopedist for bone fracture!")
            else:
                print(f"❌ FAILED: Expected Orthopedist, got {specialist}")
            
            # Check table data format
            doctors = result.get('doctors', [])
            if doctors:
                first_doctor = doctors[0]
                required_fields = ['dp_score', 'year_of_experience', 'consultation_fee', 'distance_km']
                missing_fields = [field for field in required_fields if field not in first_doctor]
                
                if not missing_fields:
                    print("✅ SUCCESS: Doctor data has all required fields for table!")
                else:
                    print(f"❌ FAILED: Missing fields in doctor data: {missing_fields}")
                
                print(f"📋 Sample doctor data: {first_doctor}")
            else:
                print("⚠️ No doctors returned")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bone_fracture_analysis()

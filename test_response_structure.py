#!/usr/bin/env python3
"""
Test the medical image analyzer API response structure
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.medical_image_analyzer import analyze_medical_image
from PIL import Image
import io
import json

def test_response_structure():
    """Test what data structure the medical image analyzer returns"""
    
    print("🧪 Testing medical image analyzer response structure...")
    
    # Create a simple test image
    test_image = Image.new('RGB', (300, 300), color='lightblue')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    test_data = img_bytes.getvalue()
    
    # Test analysis
    result = analyze_medical_image(test_data, "general")
    
    print("\n📊 API Response Structure:")
    print(f"✅ Success: {result.get('success')}")
    
    if result.get('success'):
        analysis = result.get('analysis', {})
        print(f"\n🔍 Analysis object keys: {list(analysis.keys())}")
        
        print(f"\n📝 Analysis details:")
        print(f"   Category: {analysis.get('category')}")
        print(f"   Specialist Type: {analysis.get('specialist_type')}")
        print(f"   Model Used: {analysis.get('model_used')}")
        
        doctors = analysis.get('doctors', [])
        print(f"\n👨‍⚕️ Doctors:")
        print(f"   Type: {type(doctors)}")
        print(f"   Length: {len(doctors) if doctors else 'None'}")
        
        if doctors and len(doctors) > 0:
            print(f"\n🔍 First doctor structure:")
            first_doctor = doctors[0]
            print(f"   Type: {type(first_doctor)}")
            print(f"   Keys: {list(first_doctor.keys()) if isinstance(first_doctor, dict) else 'Not a dict'}")
            
            print(f"\n📋 First doctor data:")
            for key, value in first_doctor.items():
                print(f"   {key}: {value} ({type(value).__name__})")
        else:
            print("   ❌ No doctors in response!")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    test_response_structure()

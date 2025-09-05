#!/usr/bin/env python3
"""
Quick test to verify OpenAI API integration with the updated model
"""

import os
import io
from PIL import Image
from pathlib import Path
import sys

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

def quick_test():
    """Quick test of the medical image analyzer"""
    print("🧪 Quick Medical Image Analyzer Test")
    print("=" * 40)
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:15]}...")
    
    try:
        # Import the analyzer
        from src.ai.medical_image_analyzer import MedicalImageAnalyzer
        
        analyzer = MedicalImageAnalyzer()
        print("✅ Medical image analyzer initialized")
        
        # Create a simple test image
        test_image = Image.new('RGB', (200, 200), color='lightcoral')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        test_data = img_bytes.getvalue()
        
        print(f"✅ Test image created ({len(test_data)} bytes)")
        
        # Test image validation
        validation_result = analyzer.validate_image(test_data)
        if validation_result['valid']:
            print("✅ Image validation passed")
        else:
            print(f"❌ Image validation failed: {validation_result['error']}")
            return False
        
        # Test category detection
        category = analyzer.detect_image_category(validation_result['image'], "skin")
        print(f"✅ Category detected: {category}")
        
        print("\n🤖 Testing OpenAI API connection...")
        
        # Test a simple analysis (this will make an actual API call)
        result = analyzer.analyze_medical_image(test_data, "skin", "Bangalore")
        
        if result['success']:
            print("✅ OpenAI API call successful!")
            print(f"📊 Analysis category: {result['analysis']['category']}")
            print(f"👨‍⚕️ Specialist: {result['analysis']['specialist_type']}")
            print(f"🤖 Model: {result['analysis']['model_used']}")
            
            # Show a snippet of the AI response
            ai_text = result['analysis']['ai_interpretation']
            snippet = ai_text[:150] + "..." if len(ai_text) > 150 else ai_text
            print(f"📝 AI Response preview: {snippet}")
            
            return True
        else:
            print(f"❌ Analysis failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    print("\n" + "=" * 40)
    if success:
        print("🎉 QUICK TEST PASSED!")
        print("✅ Medical Image Analyzer is ready!")
        print("🌐 Access at: http://localhost:5000/medical-image-analyzer")
    else:
        print("❌ Quick test failed")
        print("Please check the error messages above")

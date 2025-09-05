#!/usr/bin/env python3
"""
Test script for Enhanced Medical AI System
Tests the new medical AI capabilities including VLM, specialized models, and lightweight fallback
"""

import os
import sys
import json
import time
from PIL import Image
import numpy as np
import io

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_lightweight_medical_ai():
    """Test the lightweight medical AI system"""
    print("🧪 Testing Lightweight Medical AI System...")
    
    try:
        from src.ai.medical_ai_lite import analyze_with_lightweight_medical_ai
        
        # Create a simple test image (red patch - could indicate skin condition)
        test_image = np.zeros((224, 224, 3), dtype=np.uint8)
        test_image[50:150, 50:150, 0] = 255  # Red square
        test_image[50:150, 50:150, 1] = 100  # Some green
        test_image[50:150, 50:150, 2] = 100  # Some blue
        
        # Convert to bytes
        pil_image = Image.fromarray(test_image)
        img_byte_array = io.BytesIO()
        pil_image.save(img_byte_array, format='PNG')
        image_bytes = img_byte_array.getvalue()
        
        # Test lightweight analysis
        result = analyze_with_lightweight_medical_ai(
            image_bytes, 
            'skin', 
            'red patch, itchy, slightly raised'
        )
        
        print("✅ Lightweight AI Analysis Results:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Condition: {result.get('predicted_condition', 'None')}")
        print(f"   Confidence: {result.get('confidence', 0):.1f}%")
        print(f"   Severity: {result.get('severity', 'Unknown')}")
        print(f"   Recommendations: {len(result.get('recommendations', []))} found")
        
        if result.get('computer_vision_analysis'):
            cv_analysis = result['computer_vision_analysis']
            print(f"   CV Features: {list(cv_analysis.get('visual_features', {}).keys())}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Lightweight AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vlm_models():
    """Test Vision-Language Models"""
    print("\n🧪 Testing Vision-Language Models...")
    
    try:
        from src.ai.medical_vlm_models import analyze_with_medical_vlm
        
        # Create test image
        test_image = np.zeros((224, 224, 3), dtype=np.uint8)
        test_image[60:160, 60:160, 0] = 200  # Reddish area
        test_image[60:160, 60:160, 1] = 150  
        test_image[60:160, 60:160, 2] = 120  
        
        pil_image = Image.fromarray(test_image)
        img_byte_array = io.BytesIO()
        pil_image.save(img_byte_array, format='PNG')
        image_bytes = img_byte_array.getvalue()
        
        result = analyze_with_medical_vlm(
            image_bytes, 
            'dermatology', 
            'red patch with some scaling', 
            'skin'
        )
        
        print("✅ VLM Analysis Results:")
        print(f"   Success: {result.get('success', False)}")
        if result.get('analysis'):
            analysis = result['analysis']
            print(f"   Description: {analysis.get('image_description', 'N/A')[:100]}...")
            print(f"   Conditions found: {len(analysis.get('conditions', []))}")
            print(f"   Overall confidence: {analysis.get('overall_confidence', 0):.1f}%")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ VLM test failed: {e}")
        return False

def test_specialized_models():
    """Test specialized medical models"""
    print("\n🧪 Testing Specialized Medical Models...")
    
    try:
        from src.ai.specialized_medical_models import analyze_with_specialized_medical_model
        
        # Create test image
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        pil_image = Image.fromarray(test_image)
        img_byte_array = io.BytesIO()
        pil_image.save(img_byte_array, format='PNG')
        image_bytes = img_byte_array.getvalue()
        
        # Test skin analysis (should use DermNet)
        result = analyze_with_specialized_medical_model(
            image_bytes, 
            'skin', 
            'irregular mole, changing color'
        )
        
        print("✅ Specialized Model Analysis Results:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Selected model: {result.get('selected_model', 'None')}")
        print(f"   Model name: {result.get('model_name', 'None')}")
        print(f"   Predictions: {len(result.get('predictions', []))}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Specialized models test failed: {e}")
        return False

def test_integration():
    """Test the integrated system by calling the main analysis pipeline"""
    print("\n🧪 Testing Integrated Medical Analysis Pipeline...")
    
    try:
        # Import the combination function from main.py
        sys.path.append('.')
        from main import _combine_medical_analysis_results
        
        # Mock analysis results
        mock_results = {
            'lightweight_ai': {
                'success': True,
                'predicted_condition': 'Eczema',
                'confidence': 75,
                'severity': 'moderate',
                'primary_recommendation': 'Apply moisturizer',
                'computer_vision_analysis': {
                    'visual_features': {'redness': 0.8, 'texture': 0.6},
                    'color_analysis': {'dominant_color': 'red'},
                    'texture_analysis': {'roughness': 0.7}
                },
                'medical_rules_analysis': {
                    'matching_conditions': ['eczema', 'dermatitis'],
                    'confidence': 80
                }
            },
            'routing': {
                'success': True,
                'image_type': 'skin',
                'confidence': 85
            }
        }
        
        # Test combination
        combined_result = _combine_medical_analysis_results(
            mock_results, 
            'skin', 
            'red, itchy patch'
        )
        
        print("✅ Integration Test Results:")
        print(f"   Analysis type: {combined_result.get('analysis_type', 'Unknown')}")
        print(f"   Methods used: {combined_result.get('analysis_methods', [])}")
        print(f"   Conditions found: {len(combined_result.get('conditions', []))}")
        print(f"   Overall confidence: {combined_result.get('overall_confidence', 0):.1f}%")
        print(f"   Specialist needed: {combined_result.get('specialist_needed', 'Unknown')}")
        
        return len(combined_result.get('conditions', [])) > 0
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Medical AI System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Lightweight Medical AI", test_lightweight_medical_ai),
        ("Vision-Language Models", test_vlm_models),
        ("Specialized Medical Models", test_specialized_models),
        ("Integration Pipeline", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} test...")
        start_time = time.time()
        
        try:
            success = test_func()
            duration = time.time() - start_time
            results[test_name] = {'success': success, 'duration': duration}
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} ({duration:.2f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            results[test_name] = {'success': False, 'duration': duration, 'error': str(e)}
            print(f"   ❌ FAILED ({duration:.2f}s): {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = result['duration']
        print(f"{status} {test_name:<25} ({duration:.2f}s)")
        
        if not result['success'] and 'error' in result:
            print(f"      Error: {result['error']}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced Medical AI system is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("💡 Note: Some failures may be due to missing dependencies.")
        print("   The lightweight AI should work even without advanced models.")

if __name__ == '__main__':
    main()

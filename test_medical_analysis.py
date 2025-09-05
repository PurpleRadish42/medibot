# test_medical_analysis.py
"""
Test script for enhanced medical image analysis system
"""
import io
from PIL import Image
from src.ai.advanced_medical_analyzer import analyze_medical_image, TORCH_AVAILABLE
from src.ai.medical_image_router import analyze_medical_image_comprehensive

def test_medical_analyzer():
    """Test the medical image analysis system"""
    print("🔬 Testing Enhanced Medical Image Analysis System")
    print("=" * 60)
    
    # Check system status
    print(f"✅ PyTorch Available: {TORCH_AVAILABLE}")
    
    try:
        import cv2
        print(f"✅ OpenCV Available: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV Not Available")
    
    try:
        import transformers
        print(f"✅ Transformers Available: {transformers.__version__}")
    except ImportError:
        print("❌ Transformers Not Available")
    
    print("=" * 60)
    
    # Create a test image (simulating a skin photo)
    print("📸 Creating test image...")
    test_image = Image.new('RGB', (300, 300), color=(220, 180, 140))  # Skin-like color
    
    # Save to bytes
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    test_data = img_bytes.getvalue()
    
    print(f"   Test image size: {len(test_data)} bytes")
    
    # Test basic advanced analyzer
    print("\n🔬 Testing Advanced Medical Analyzer...")
    try:
        result = analyze_medical_image(test_data, analysis_type='both')
        
        if result['success']:
            print("✅ Advanced analysis successful!")
            print(f"   Image quality: {result.get('image_quality', 'N/A')}")
            print(f"   Models loaded: {result.get('model_info', {}).get('models_loaded', [])}")
            
            if 'cancer_analysis' in result:
                cancer_conditions = result['cancer_analysis'].get('conditions', [])
                print(f"   Cancer analysis: {len(cancer_conditions)} conditions detected")
                
            if 'general_analysis' in result:
                general_conditions = result['general_analysis'].get('conditions', [])
                print(f"   General analysis: {len(general_conditions)} conditions detected")
        else:
            print(f"❌ Advanced analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Advanced analyzer error: {e}")
    
    # Test medical image router
    print("\n🎯 Testing Medical Image Router...")
    try:
        result = analyze_medical_image_comprehensive(
            image_data=test_data,
            context="skin condition on arm",
            user_city="Bangalore"
        )
        
        if result['success']:
            print("✅ Image routing successful!")
            print(f"   Detected image type: {result.get('image_type', 'Unknown')}")
            print(f"   Analysis type: {result.get('analysis', {}).get('analysis_type', 'Unknown')}")
            
            conditions = result.get('analysis', {}).get('conditions', [])
            print(f"   Conditions detected: {len(conditions)}")
            
            for i, condition in enumerate(conditions[:3]):  # Show top 3
                name = condition.get('name', 'Unknown')
                confidence = condition.get('confidence', 0)
                print(f"     {i+1}. {name} ({confidence}% confidence)")
                
        else:
            print(f"❌ Image routing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Image router error: {e}")
    
    print("\n" + "=" * 60)
    print("🏥 Medical Image Analysis System Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_medical_analyzer()

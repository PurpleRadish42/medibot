# test_image_detection.py
"""
Test the improved image type detection
"""
import io
import numpy as np
from PIL import Image
from src.ai.medical_image_router import medical_image_router

def test_image_detection():
    """Test image type detection with various scenarios"""
    print("🔍 Testing Improved Image Type Detection")
    print("=" * 50)
    
    # Test 1: Skin-colored image (simulating face/skin photo)
    print("\n1️⃣ Testing skin-colored image...")
    skin_image = Image.new('RGB', (400, 300), color=(200, 150, 120))  # Skin tone
    img_bytes = io.BytesIO()
    skin_image.save(img_bytes, format='JPEG')
    
    detected_type = medical_image_router.detect_image_type(img_bytes.getvalue())
    print(f"   Detected type: {detected_type} (Expected: skin)")
    
    # Test 2: Skin image with context
    print("\n2️⃣ Testing with skin context...")
    detected_type = medical_image_router.detect_image_type(
        img_bytes.getvalue(), 
        context="face photo with acne"
    )
    print(f"   Detected type: {detected_type} (Expected: skin)")
    
    # Test 3: Grayscale image (simulating X-ray)
    print("\n3️⃣ Testing grayscale image...")
    # Create a high-contrast grayscale image
    xray_array = np.zeros((400, 400), dtype=np.uint8)
    xray_array[100:300, 100:300] = 200  # Bright center (bones)
    xray_array[150:250, 150:250] = 50   # Dark areas (tissue)
    xray_image = Image.fromarray(xray_array, mode='L').convert('RGB')
    
    img_bytes = io.BytesIO()
    xray_image.save(img_bytes, format='JPEG')
    
    detected_type = medical_image_router.detect_image_type(img_bytes.getvalue())
    print(f"   Detected type: {detected_type} (Expected: skin or xray)")
    
    # Test 4: X-ray with context
    print("\n4️⃣ Testing with X-ray context...")
    detected_type = medical_image_router.detect_image_type(
        img_bytes.getvalue(), 
        context="chest x-ray showing lungs"
    )
    print(f"   Detected type: {detected_type} (Expected: xray)")
    
    # Test 5: Colorful image (definitely not X-ray)
    print("\n5️⃣ Testing colorful image...")
    colorful_image = Image.new('RGB', (300, 300), color=(255, 100, 50))  # Bright orange
    img_bytes = io.BytesIO()
    colorful_image.save(img_bytes, format='JPEG')
    
    detected_type = medical_image_router.detect_image_type(img_bytes.getvalue())
    print(f"   Detected type: {detected_type} (Expected: skin)")
    
    # Test 6: Face context (should always be skin)
    print("\n6️⃣ Testing face context...")
    detected_type = medical_image_router.detect_image_type(
        img_bytes.getvalue(), 
        context="my face"
    )
    print(f"   Detected type: {detected_type} (Expected: skin)")
    
    print("\n" + "=" * 50)
    print("✅ Image detection test complete!")

if __name__ == "__main__":
    test_image_detection()

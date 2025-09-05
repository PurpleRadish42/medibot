#!/usr/bin/env python3
"""
Quick test of image type detection
"""

from src.ai.medical_image_router import MedicalImageRouter

router = MedicalImageRouter()
dummy_image = b"fake_image_data"

# Test fracture detection
result = router.detect_image_type(dummy_image, "X-ray showing broken hand")
print(f"Fracture test: '{result}'")

# Test normal photo detection  
result2 = router.detect_image_type(dummy_image, "normal selfie photo")
print(f"Normal photo test: '{result2}'")

# Test empty context
result3 = router.detect_image_type(dummy_image, "")
print(f"Empty context test: '{result3}'")

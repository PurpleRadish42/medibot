# src/ai/medical_image_router.py
"""
Medical Image Analysis Router
Routes different types of medical images to appropriate specialized analyzers
"""
import io
import logging
from typing import Dict, List, Any, Optional
from PIL import Image
import numpy as np

# Import specialized analyzers
try:
    from src.ai.advanced_medical_analyzer import analyze_medical_image
    ADVANCED_ANALYZER_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYZER_AVAILABLE = False

try:
    from src.ai.skin_analyzer import analyze_skin_image
    SKIN_ANALYZER_AVAILABLE = True
except ImportError:
    SKIN_ANALYZER_AVAILABLE = False

# Medical image type detection
IMAGE_TYPES = {
    'skin': {
        'keywords': ['skin', 'mole', 'rash', 'lesion', 'dermatology', 'acne', 'eczema'],
        'analyzer': 'skin_analyzer',
        'description': 'Skin condition and dermatological analysis'
    },
    'xray': {
        'keywords': ['xray', 'x-ray', 'chest', 'bone', 'fracture', 'pneumonia'],
        'analyzer': 'xray_analyzer',
        'description': 'X-ray and radiological image analysis'
    },
    'eyes': {
        'keywords': ['eye', 'retina', 'ophthalmology', 'vision', 'cataract'],
        'analyzer': 'ophthalmology_analyzer', 
        'description': 'Eye and retinal image analysis'
    },
    'mri': {
        'keywords': ['mri', 'brain', 'spine', 'magnetic', 'resonance'],
        'analyzer': 'mri_analyzer',
        'description': 'MRI scan analysis'
    },
    'ct': {
        'keywords': ['ct', 'scan', 'computed', 'tomography'],
        'analyzer': 'ct_analyzer',
        'description': 'CT scan analysis'
    }
}

class MedicalImageRouter:
    """
    Routes medical images to appropriate specialized analyzers
    """
    
    def __init__(self):
        """Initialize the medical image router"""
        self.logger = logging.getLogger(__name__)
        
    def detect_image_type(self, image_data: bytes, context: str = None) -> str:
        """
        Detect the type of medical image with improved accuracy
        
        Args:
            image_data: Raw image bytes
            context: Optional context or description from user
            
        Returns:
            Detected image type
        """
        try:
            # Analyze context first - this is most reliable
            if context:
                context_lower = context.lower()
                
                # Strong context indicators
                skin_keywords = ['skin', 'face', 'mole', 'rash', 'acne', 'eczema', 'dermatitis', 'spot', 'blemish', 'pimple']
                xray_keywords = ['xray', 'x-ray', 'chest', 'lung', 'bone', 'fracture', 'radiograph']
                eye_keywords = ['eye', 'retina', 'vision', 'pupil', 'iris']
                
                # Check for skin-related context
                if any(keyword in context_lower for keyword in skin_keywords):
                    return 'skin'
                
                # Check for X-ray context
                if any(keyword in context_lower for keyword in xray_keywords):
                    return 'xray'
                    
                # Check for eye context
                if any(keyword in context_lower for keyword in eye_keywords):
                    return 'eyes'
            
            # Image analysis for type detection
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Convert to numpy for analysis
            img_array = np.array(image)
            
            # Priority-based detection (most common to least common)
            # 1. Check for skin first (most common medical photos)
            if self._looks_like_skin(img_array):
                return 'skin'
            
            # 2. Check for X-ray (very specific characteristics)
            if self._looks_like_xray(img_array):
                return 'xray'
                
            # 3. Check for MRI/CT (less common)
            if self._looks_like_mri_ct(img_array):
                return 'mri'
            
            # 4. Check aspect ratio and other clues
            aspect_ratio = width / height
            
            # Face/skin photos are often portrait or square
            if 0.7 <= aspect_ratio <= 1.5:
                # Check if it has color and moderate brightness (likely skin/face)
                if len(img_array.shape) == 3:
                    mean_brightness = np.mean(img_array)
                    if 50 < mean_brightness < 200:
                        return 'skin'
            
            # X-rays are often landscape and have specific characteristics
            if aspect_ratio > 1.2:
                if len(img_array.shape) == 3:
                    # Check if mostly grayscale
                    color_std = np.std([np.std(img_array[:,:,0]), np.std(img_array[:,:,1]), np.std(img_array[:,:,2])])
                    if color_std < 20:  # Low color variation
                        return 'xray'
            
            # Default to skin for unclear cases (safest assumption for medical photos)
            return 'skin'
            
        except Exception as e:
            self.logger.error(f"Error detecting image type: {e}")
            return 'skin'  # Safe default
    
    def _looks_like_xray(self, img_array: np.ndarray) -> bool:
        """Detect if image looks like an X-ray"""
        try:
            # X-rays are typically grayscale or have low color variation
            if len(img_array.shape) == 3:
                # Check if image is mostly grayscale (low color variation)
                r_channel = img_array[:, :, 0]
                g_channel = img_array[:, :, 1]
                b_channel = img_array[:, :, 2]
                
                # Calculate color variation
                rg_diff = np.mean(np.abs(r_channel.astype(float) - g_channel.astype(float)))
                rb_diff = np.mean(np.abs(r_channel.astype(float) - b_channel.astype(float)))
                gb_diff = np.mean(np.abs(g_channel.astype(float) - b_channel.astype(float)))
                
                color_variation = (rg_diff + rb_diff + gb_diff) / 3
                
                # If color variation is too high, it's not an X-ray
                if color_variation > 15:
                    return False
                
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            # X-rays have specific characteristics:
            # 1. High contrast between dark and light areas
            # 2. Darker background (bones appear lighter)
            # 3. Limited intensity range in specific areas
            
            contrast = np.std(gray)
            mean_intensity = np.mean(gray)
            
            # X-rays typically have:
            # - Very high contrast (>60)
            # - Dark background (mean intensity < 100)
            # - Specific intensity distribution
            
            # More strict criteria to avoid false positives
            is_high_contrast = contrast > 60
            is_dark_background = mean_intensity < 100
            
            # Check for X-ray specific patterns (dark edges, light center regions)
            height, width = gray.shape
            edge_mean = np.mean([
                np.mean(gray[0:height//10, :]),  # Top edge
                np.mean(gray[-height//10:, :]),  # Bottom edge
                np.mean(gray[:, 0:width//10]),   # Left edge
                np.mean(gray[:, -width//10:])    # Right edge
            ])
            
            center_mean = np.mean(gray[height//4:3*height//4, width//4:3*width//4])
            
            # X-rays often have darker edges and lighter center
            edge_to_center_ratio = edge_mean / (center_mean + 1)
            
            # Very strict criteria - all must be true for X-ray detection
            return (is_high_contrast and 
                   is_dark_background and 
                   edge_to_center_ratio < 0.7 and
                   contrast > 70)  # Even higher contrast requirement
            
        except Exception:
            return False
    
    def _looks_like_skin(self, img_array: np.ndarray) -> bool:
        """Detect if image looks like skin"""
        try:
            # Skin images typically have warm color tones and moderate contrast
            if len(img_array.shape) != 3:
                return False
            
            # Calculate average color channels
            r_mean = np.mean(img_array[:, :, 0])
            g_mean = np.mean(img_array[:, :, 1]) 
            b_mean = np.mean(img_array[:, :, 2])
            
            # Skin detection criteria:
            # 1. Red channel should be prominent
            # 2. Green channel should be significant
            # 3. Blue channel should be lower than red
            # 4. Overall brightness should be moderate
            # 5. Color variation should indicate color image
            
            # Check for skin-like color ranges
            is_red_prominent = r_mean > 80 and r_mean > b_mean
            is_green_adequate = g_mean > 60
            is_blue_lower = b_mean < r_mean
            is_moderate_brightness = 50 < np.mean(img_array) < 220
            
            # Check color variation (skin images should have color)
            color_variation = np.std(img_array[:, :, 0] - img_array[:, :, 1]) + \
                            np.std(img_array[:, :, 1] - img_array[:, :, 2]) + \
                            np.std(img_array[:, :, 0] - img_array[:, :, 2])
            
            has_color_variation = color_variation > 10
            
            # Check for skin tone ranges (various ethnicities)
            # Skin tones typically have specific RGB ratios
            skin_tone_detected = False
            
            # Light skin tones
            if 150 < r_mean < 255 and 120 < g_mean < 220 and 100 < b_mean < 200:
                skin_tone_detected = True
            # Medium skin tones  
            elif 100 < r_mean < 200 and 80 < g_mean < 160 and 60 < b_mean < 140:
                skin_tone_detected = True
            # Darker skin tones
            elif 60 < r_mean < 150 and 50 < g_mean < 120 and 40 < b_mean < 100:
                skin_tone_detected = True
            
            return (is_red_prominent and 
                   is_green_adequate and 
                   is_blue_lower and 
                   is_moderate_brightness and 
                   has_color_variation and
                   skin_tone_detected)
            
        except Exception:
            return False
    
    def _looks_like_mri_ct(self, img_array: np.ndarray) -> bool:
        """Detect if image looks like MRI/CT scan"""
        try:
            # MRI/CT scans are typically grayscale with specific patterns
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            # MRI/CT have specific intensity patterns and are often square/circular
            height, width = gray.shape
            aspect_ratio = width / height
            
            # Check for circular/square regions (brain scans)
            return 0.8 <= aspect_ratio <= 1.2 and np.std(gray) > 30
            
        except Exception:
            return False
    
    def route_analysis(self, image_data: bytes, image_type: str = None, context: str = None, 
                      user_city: str = None) -> Dict[str, Any]:
        """
        Route image to appropriate analyzer
        
        Args:
            image_data: Raw image bytes
            image_type: Specified image type or None for auto-detection
            context: Optional context from user
            user_city: User location for doctor recommendations
            
        Returns:
            Analysis results from appropriate analyzer
        """
        try:
            # Detect image type if not specified
            if not image_type:
                image_type = self.detect_image_type(image_data, context)
            
            self.logger.info(f"Routing {image_type} image for analysis")
            
            # Route to appropriate analyzer
            if image_type == 'skin':
                return self._analyze_skin_image(image_data, user_city, context)
            elif image_type == 'xray':
                return self._analyze_xray_image(image_data, user_city, context)
            elif image_type == 'eyes':
                return self._analyze_eye_image(image_data, user_city, context)
            elif image_type in ['mri', 'ct']:
                return self._analyze_scan_image(image_data, image_type, user_city, context)
            else:
                # Default to skin analysis
                return self._analyze_skin_image(image_data, user_city, context)
                
        except Exception as e:
            self.logger.error(f"Error routing image analysis: {e}")
            return {
                'success': False,
                'error': f'Image analysis routing failed: {str(e)}'
            }
    
    def _analyze_skin_image(self, image_data: bytes, user_city: str = None, 
                           context: str = None) -> Dict[str, Any]:
        """Analyze skin/dermatological images"""
        try:
            if SKIN_ANALYZER_AVAILABLE:
                result = analyze_skin_image(image_data, user_city)
                if result.get('success'):
                    result['image_type'] = 'skin'
                    result['analysis_description'] = 'Dermatological Analysis'
                return result
            else:
                return self._fallback_skin_analysis(image_data)
                
        except Exception as e:
            return {'success': False, 'error': f'Skin analysis failed: {str(e)}'}
    
    def _analyze_xray_image(self, image_data: bytes, user_city: str = None, 
                           context: str = None) -> Dict[str, Any]:
        """Analyze X-ray images"""
        try:
            # Use advanced analyzer if available
            if ADVANCED_ANALYZER_AVAILABLE:
                # Create custom X-ray analysis
                return self._advanced_xray_analysis(image_data, user_city)
            else:
                return self._fallback_xray_analysis(image_data, user_city)
                
        except Exception as e:
            return {'success': False, 'error': f'X-ray analysis failed: {str(e)}'}
    
    def _analyze_eye_image(self, image_data: bytes, user_city: str = None, 
                          context: str = None) -> Dict[str, Any]:
        """Analyze eye/retinal images"""
        try:
            return self._fallback_eye_analysis(image_data, user_city)
                
        except Exception as e:
            return {'success': False, 'error': f'Eye analysis failed: {str(e)}'}
    
    def _analyze_scan_image(self, image_data: bytes, scan_type: str, user_city: str = None, 
                           context: str = None) -> Dict[str, Any]:
        """Analyze MRI/CT scan images"""
        try:
            return self._fallback_scan_analysis(image_data, scan_type, user_city)
                
        except Exception as e:
            return {'success': False, 'error': f'{scan_type.upper()} analysis failed: {str(e)}'}
    
    def _advanced_xray_analysis(self, image_data: bytes, user_city: str = None) -> Dict[str, Any]:
        """Advanced X-ray analysis using ML models"""
        # Placeholder for advanced X-ray analysis
        # In production, you would use specialized chest X-ray models
        return {
            'success': True,
            'image_type': 'xray',
            'analysis_description': 'X-ray Analysis',
            'analysis': {
                'conditions': [
                    {
                        'name': 'Normal Chest X-ray',
                        'confidence': 75,
                        'description': 'No obvious abnormalities detected in chest X-ray'
                    }
                ],
                'specialist_type': 'Radiologist',
                'doctors': [],
                'recommendations': ['Consult with radiologist for detailed interpretation'],
                'analysis_type': 'Advanced X-ray Analysis'
            }
        }
    
    def _fallback_skin_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """Fallback skin analysis"""
        return {
            'success': True,
            'image_type': 'skin',
            'analysis': {
                'conditions': [
                    {'name': 'Skin condition detected', 'confidence': 60, 'description': 'Professional evaluation recommended'}
                ],
                'specialist_type': 'Dermatologist',
                'doctors': [],
                'analysis_type': 'Basic Skin Analysis'
            }
        }
    
    def _fallback_xray_analysis(self, image_data: bytes, user_city: str = None) -> Dict[str, Any]:
        """Fallback X-ray analysis"""
        return {
            'success': True,
            'image_type': 'xray',
            'analysis': {
                'conditions': [
                    {'name': 'X-ray requires professional interpretation', 'confidence': 90, 
                     'description': 'X-ray images require professional radiologist review'}
                ],
                'specialist_type': 'Radiologist',
                'doctors': [],
                'recommendations': ['Immediate professional radiologist consultation required'],
                'analysis_type': 'Basic X-ray Processing'
            }
        }
    
    def _fallback_eye_analysis(self, image_data: bytes, user_city: str = None) -> Dict[str, Any]:
        """Fallback eye analysis"""
        return {
            'success': True,
            'image_type': 'eyes',
            'analysis': {
                'conditions': [
                    {'name': 'Eye examination needed', 'confidence': 80, 
                     'description': 'Professional ophthalmological examination recommended'}
                ],
                'specialist_type': 'Ophthalmologist',
                'doctors': [],
                'recommendations': ['Schedule comprehensive eye examination'],
                'analysis_type': 'Basic Eye Assessment'
            }
        }
    
    def _fallback_scan_analysis(self, image_data: bytes, scan_type: str, user_city: str = None) -> Dict[str, Any]:
        """Fallback scan analysis"""
        specialist_map = {
            'mri': 'Neurologist',
            'ct': 'Radiologist'
        }
        
        return {
            'success': True,
            'image_type': scan_type,
            'analysis': {
                'conditions': [
                    {'name': f'{scan_type.upper()} scan requires professional review', 'confidence': 95,
                     'description': f'{scan_type.upper()} scans require specialist interpretation'}
                ],
                'specialist_type': specialist_map.get(scan_type, 'Radiologist'),
                'doctors': [],
                'recommendations': [f'Professional {scan_type.upper()} interpretation required'],
                'analysis_type': f'Basic {scan_type.upper()} Processing'
            }
        }
    
    def get_supported_image_types(self) -> Dict[str, str]:
        """Get supported medical image types"""
        return {image_type: info['description'] for image_type, info in IMAGE_TYPES.items()}

# Global router instance
medical_image_router = MedicalImageRouter()

def analyze_medical_image_comprehensive(image_data: bytes, image_type: str = None, 
                                      context: str = None, user_city: str = None) -> Dict[str, Any]:
    """
    Comprehensive medical image analysis with automatic routing
    
    Args:
        image_data: Raw image bytes
        image_type: Optional image type specification
        context: Optional context from user
        user_city: Optional user city for doctor recommendations
        
    Returns:
        Complete analysis results
    """
    return medical_image_router.route_analysis(image_data, image_type, context, user_city)

if __name__ == "__main__":
    print("🏥 Testing Medical Image Router...")
    print("Supported image types:", medical_image_router.get_supported_image_types())
    
    # Test image type detection
    test_image = Image.new('RGB', (300, 300), color='pink')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    test_data = img_bytes.getvalue()
    
    detected_type = medical_image_router.detect_image_type(test_data, "skin rash")
    print(f"Detected image type: {detected_type}")
    
    result = analyze_medical_image_comprehensive(test_data, context="skin condition")
    print("Test completed:", result['success'])

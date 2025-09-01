# src/ai/skin_analyzer.py
"""
Skin Condition Image Analyzer
AI-powered analysis of skin conditions from images
"""
import io
import base64
import logging
from typing import Dict, List, Any, Optional
from PIL import Image
import random

# Import the medical recommender for doctor suggestions
try:
    from src.llm.recommender import MedicalRecommender
    MEDICAL_RECOMMENDER_AVAILABLE = True
except ImportError:
    MEDICAL_RECOMMENDER_AVAILABLE = False
    print("Warning: MedicalRecommender not available for skin analyzer")

class SkinConditionAnalyzer:
    """
    AI-powered skin condition analyzer
    Currently using a mock model for demonstration - can be replaced with real CV model
    """
    
    def __init__(self):
        """Initialize the skin analyzer"""
        self.logger = logging.getLogger(__name__)
        
        # Mock skin conditions database for demonstration
        self.skin_conditions = [
            {
                "name": "Eczema",
                "probability_range": (60, 85),
                "description": "Inflammatory skin condition causing itchy, red, swollen skin",
                "specialist": "Dermatologist"
            },
            {
                "name": "Psoriasis", 
                "probability_range": (40, 75),
                "description": "Autoimmune condition causing scaly, inflamed skin patches",
                "specialist": "Dermatologist"
            },
            {
                "name": "Melanoma",
                "probability_range": (15, 40),
                "description": "Serious form of skin cancer",
                "specialist": "Dermatologist"
            },
            {
                "name": "Acne",
                "probability_range": (50, 80),
                "description": "Common skin condition causing pimples and blemishes",
                "specialist": "Dermatologist"
            },
            {
                "name": "Dermatitis",
                "probability_range": (45, 70),
                "description": "General term for skin inflammation",
                "specialist": "Dermatologist"
            },
            {
                "name": "Basal Cell Carcinoma",
                "probability_range": (20, 50),
                "description": "Most common form of skin cancer",
                "specialist": "Dermatologist"
            },
            {
                "name": "Seborrheic Keratosis",
                "probability_range": (30, 60),
                "description": "Non-cancerous skin growth",
                "specialist": "Dermatologist"
            }
        ]
        
        # Initialize medical recommender if available
        self.medical_recommender = None
        if MEDICAL_RECOMMENDER_AVAILABLE:
            try:
                self.medical_recommender = MedicalRecommender()
            except Exception as e:
                self.logger.warning(f"Failed to initialize MedicalRecommender: {e}")
    
    def validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Validate uploaded image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dict with validation result and processed image
        """
        try:
            # Check file size (max 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                return {
                    "valid": False,
                    "error": "Image file too large. Maximum size is 10MB."
                }
            
            # Try to open and validate image
            image = Image.open(io.BytesIO(image_data))
            
            # Check image format
            if image.format not in ['JPEG', 'JPG', 'PNG']:
                return {
                    "valid": False,
                    "error": "Unsupported image format. Please use JPEG or PNG."
                }
            
            # Check image dimensions
            width, height = image.size
            if width < 100 or height < 100:
                return {
                    "valid": False,
                    "error": "Image too small. Minimum size is 100x100 pixels."
                }
            
            if width > 4000 or height > 4000:
                return {
                    "valid": False,
                    "error": "Image too large. Maximum size is 4000x4000 pixels."
                }
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return {
                "valid": True,
                "image": image,
                "dimensions": (width, height),
                "format": image.format
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid image file: {str(e)}"
            }
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for analysis
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Resize image to standard size for analysis
        target_size = (224, 224)  # Standard CNN input size
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        return image
    
    def analyze_mock_cv_model(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Mock computer vision model for skin condition analysis
        In production, this would be replaced with a real CNN model
        
        Args:
            image: Preprocessed PIL Image
            
        Returns:
            List of potential conditions with confidence scores
        """
        # Mock analysis - randomly select 2-4 conditions and assign probabilities
        selected_conditions = random.sample(self.skin_conditions, k=random.randint(2, 4))
        
        results = []
        for condition in selected_conditions:
            min_prob, max_prob = condition["probability_range"]
            confidence = random.randint(min_prob, max_prob)
            
            results.append({
                "name": condition["name"],
                "confidence": confidence,
                "description": condition["description"],
                "specialist": condition["specialist"]
            })
        
        # Sort by confidence score (highest first)
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results
    
    def get_doctor_recommendations(self, specialist_type: str, user_city: str = None) -> List[Dict[str, Any]]:
        """
        Get doctor recommendations for the specialist type
        
        Args:
            specialist_type: Type of specialist needed
            user_city: Optional user city for location-based recommendations
            
        Returns:
            List of recommended doctors
        """
        if not self.medical_recommender:
            return []
        
        try:
            # Use the existing doctor recommendation system
            doctor_recommendations = self.medical_recommender.get_doctor_recommendations(
                specialist_type, user_city
            )
            
            # Parse the recommendations (they come as formatted text)
            # This is a simplified parser - in production you might want more robust parsing
            doctors = []
            if "📍 DOCTOR RECOMMENDATIONS" in doctor_recommendations:
                lines = doctor_recommendations.split('\n')
                for line in lines:
                    if "Dr." in line and "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 3:
                            name = parts[0].strip()
                            city = parts[1].strip() if len(parts) > 1 else "Unknown"
                            specialty = parts[2].strip() if len(parts) > 2 else specialist_type
                            rating = parts[3].strip() if len(parts) > 3 else "N/A"
                            
                            doctors.append({
                                "name": name,
                                "city": city,
                                "specialty": specialty,
                                "rating": rating
                            })
            
            return doctors[:5]  # Return top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting doctor recommendations: {e}")
            return []
    
    def analyze_skin_condition(self, image_data: bytes, user_city: str = None) -> Dict[str, Any]:
        """
        Main method to analyze skin condition from image
        
        Args:
            image_data: Raw image bytes
            user_city: Optional user city for doctor recommendations
            
        Returns:
            Analysis results with conditions, specialist recommendations, and doctors
        """
        try:
            # Validate image
            validation_result = self.validate_image(image_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            image = validation_result["image"]
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Analyze with mock CV model
            conditions = self.analyze_mock_cv_model(processed_image)
            
            # Get top specialist recommendation
            top_condition = conditions[0] if conditions else None
            specialist_type = top_condition["specialist"] if top_condition else "Dermatologist"
            
            # Get doctor recommendations
            doctors = self.get_doctor_recommendations(specialist_type, user_city)
            
            return {
                "success": True,
                "analysis": {
                    "conditions": [
                        {
                            "name": condition["name"],
                            "confidence": condition["confidence"],
                            "description": condition["description"]
                        }
                        for condition in conditions
                    ],
                    "specialist_type": specialist_type,
                    "doctors": doctors,
                    "image_info": {
                        "dimensions": validation_result["dimensions"],
                        "format": validation_result["format"]
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing skin condition: {e}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }

# Global analyzer instance
skin_analyzer = SkinConditionAnalyzer()

def analyze_skin_image(image_data: bytes, user_city: str = None) -> Dict[str, Any]:
    """
    Convenience function to analyze skin condition
    
    Args:
        image_data: Raw image bytes
        user_city: Optional user city
        
    Returns:
        Analysis results
    """
    return skin_analyzer.analyze_skin_condition(image_data, user_city)

# Test the analyzer
if __name__ == "__main__":
    print("🧪 Testing Skin Condition Analyzer...")
    
    # Create a simple test image
    test_image = Image.new('RGB', (300, 300), color='red')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    test_data = img_bytes.getvalue()
    
    # Test analysis
    result = analyze_skin_image(test_data)
    print("Test result:", result)
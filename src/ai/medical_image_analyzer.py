# src/ai/medical_image_analyzer.py
"""
Medical Image Analyzer using OpenAI Vision API
AI-powered analysis of medical images including skin conditions, X-rays, and other medical imaging
"""
import io
import base64
import logging
import os
from typing import Dict, List, Any, Optional
from PIL import Image
import openai
from openai import OpenAI

# Import the medical recommender for doctor suggestions
try:
    from src.llm.recommender import MedicalRecommender
    MEDICAL_RECOMMENDER_AVAILABLE = True
except ImportError:
    MEDICAL_RECOMMENDER_AVAILABLE = False
    print("Warning: MedicalRecommender not available for medical image analyzer")

class MedicalImageAnalyzer:
    """
    AI-powered medical image analyzer using OpenAI's Vision API
    Supports various types of medical images including skin conditions, X-rays, and general medical photography
    """
    
    def __init__(self):
        """Initialize the medical image analyzer"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Medical image categories and their specific analysis prompts
        self.medical_categories = {
            "skin": {
                "name": "Dermatological Analysis",
                "specialist": "Dermatologist",
                "prompt_template": self._get_dermatology_prompt()
            },
            "xray": {
                "name": "Radiological Analysis", 
                "specialist": "Radiologist",
                "prompt_template": self._get_radiology_prompt()
            },
            "eye": {
                "name": "Ophthalmological Analysis",
                "specialist": "Ophthalmologist", 
                "prompt_template": self._get_ophthalmology_prompt()
            },
            "dental": {
                "name": "Dental Analysis",
                "specialist": "Dentist",
                "prompt_template": self._get_dental_prompt()
            },
            "wound": {
                "name": "Wound Assessment",
                "specialist": "General Practitioner",
                "prompt_template": self._get_wound_assessment_prompt()
            },
            "general": {
                "name": "General Medical Analysis",
                "specialist": "General Practitioner",
                "prompt_template": self._get_general_medical_prompt()
            }
        }
        
        # Initialize medical recommender if available
        self.medical_recommender = None
        if MEDICAL_RECOMMENDER_AVAILABLE:
            try:
                self.medical_recommender = MedicalRecommender()
            except Exception as e:
                self.logger.warning(f"Failed to initialize MedicalRecommender: {e}")
    
    def _get_dermatology_prompt(self) -> str:
        """Get specialized prompt for dermatological analysis"""
        return """You are an expert dermatologist AI assistant. Analyze this medical image focusing on skin conditions.

Please provide a detailed analysis including:

1. **Visual Observations**: Describe what you see in the image (color, texture, pattern, size, location)

2. **Potential Conditions**: List 2-4 most likely dermatological conditions based on visual features, ranked by likelihood:
   - Condition name
   - Confidence level (Low/Medium/High)
   - Key identifying features
   - Brief description

3. **Severity Assessment**: Rate the apparent severity (Mild/Moderate/Severe/Urgent)

4. **Recommendations**: 
   - Whether immediate medical attention is needed
   - Suggested next steps
   - Home care advice (if appropriate)
   - When to see a specialist

5. **Important Notes**: Any red flags or concerning features

Remember: This is for educational purposes only and does not replace professional medical diagnosis. Always recommend consulting with a qualified dermatologist for proper diagnosis and treatment.

Format your response in clear sections with appropriate medical terminology but explain complex terms."""

    def _get_radiology_prompt(self) -> str:
        """Get specialized prompt for radiological analysis"""
        return """You are an expert radiologist AI assistant. Analyze this medical imaging study (X-ray, CT, MRI, etc.).

Please provide a detailed analysis including:

1. **Image Quality**: Assess the technical quality and positioning

2. **Anatomical Structures**: Identify and describe visible anatomical structures

3. **Findings**: 
   - Normal findings
   - Abnormal findings (if any)
   - Areas of concern

4. **Differential Diagnosis**: List potential conditions based on imaging findings

5. **Severity Assessment**: Rate any abnormalities found

6. **Specialist Recommendation**: Based on your findings, recommend the most appropriate specialist:
   - For bone fractures, joint injuries, musculoskeletal problems → Orthopedist
   - For lung/chest issues → Pulmonologist  
   - For heart conditions → Cardiologist
   - For brain/neurological findings → Neurologist
   - For general interpretation → Radiologist

7. **Recommendations**:
   - Need for additional imaging
   - Clinical correlation needed
   - Follow-up recommendations

8. **Limitations**: Note any limitations in the analysis

IMPORTANT: This is for educational purposes only. Radiological interpretation requires extensive training and should always be performed by qualified radiologists. Emphasize the need for professional interpretation."""

    def _get_ophthalmology_prompt(self) -> str:
        """Get specialized prompt for eye/ophthalmological analysis"""
        return """You are an expert ophthalmologist AI assistant. Analyze this eye-related medical image.

Please provide a detailed analysis including:

1. **Visual Assessment**: Describe the visible structures (eyelids, conjunctiva, cornea, iris, pupil, etc.)

2. **Abnormal Findings**: Identify any visible abnormalities:
   - Redness or inflammation
   - Discharge or tearing
   - Structural abnormalities
   - Pupil abnormalities

3. **Potential Conditions**: List likely eye conditions based on visual features

4. **Urgency Level**: Assess if this requires immediate attention

5. **Recommendations**:
   - Need for urgent ophthalmological evaluation
   - Suggested next steps
   - When to seek immediate care

6. **Red Flags**: Identify any signs requiring immediate medical attention

Remember: Eye conditions can be serious and vision-threatening. Always emphasize the importance of professional evaluation by an ophthalmologist."""

    def _get_dental_prompt(self) -> str:
        """Get specialized prompt for dental analysis"""
        return """You are an expert dental AI assistant. Analyze this dental/oral health image.

Please provide a detailed analysis including:

1. **Oral Structures**: Describe visible teeth, gums, and oral tissues

2. **Dental Findings**:
   - Tooth condition and alignment
   - Gum health and color
   - Signs of decay or damage
   - Oral hygiene assessment

3. **Potential Issues**: Identify any visible dental or oral health concerns

4. **Recommendations**:
   - Need for dental evaluation
   - Oral hygiene advice
   - Urgency of treatment

5. **Prevention**: General oral health maintenance advice

Note: This analysis is for educational purposes. Professional dental examination is essential for proper diagnosis and treatment planning."""

    def _get_wound_assessment_prompt(self) -> str:
        """Get specialized prompt for wound assessment"""
        return """You are an expert in wound care assessment. Analyze this wound or injury image.

Please provide a detailed analysis including:

1. **Wound Description**: 
   - Size and depth assessment
   - Wound edges and surrounding tissue
   - Signs of infection
   - Healing stage

2. **Severity Assessment**: Rate the wound severity and healing progress

3. **Infection Signs**: Look for signs of infection (redness, swelling, discharge, heat)

4. **Healing Assessment**: Evaluate current healing stage and progress

5. **Recommendations**:
   - Need for medical attention
   - Wound care instructions
   - Signs to watch for
   - When to seek immediate help

6. **Red Flags**: Identify any concerning features requiring immediate medical attention

Important: Wound care can be complex. Serious wounds, signs of infection, or non-healing wounds require professional medical evaluation."""

    def _get_general_medical_prompt(self) -> str:
        """Get general medical analysis prompt"""
        return """You are an expert medical AI assistant. Analyze this medical image comprehensively.

Please provide a detailed analysis including:

1. **Image Description**: Describe what you observe in the medical image

2. **Medical Assessment**:
   - Visible abnormalities or concerns
   - Normal vs abnormal findings
   - Relevant anatomical observations

3. **Potential Conditions**: List possible medical conditions based on visual evidence

4. **Severity Assessment**: Evaluate the apparent severity of any findings

5. **Recommendations**:
   - Need for medical evaluation
   - Urgency level
   - Suggested next steps
   - Specialist referral if needed

6. **Important Disclaimers**: Emphasize limitations of image-based analysis

Remember: This is for educational and informational purposes only. Medical images require professional interpretation by qualified healthcare providers. Always recommend appropriate medical consultation."""

    def validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Validate uploaded medical image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dict with validation result and processed image
        """
        try:
            # Check file size (max 20MB for medical images)
            if len(image_data) > 20 * 1024 * 1024:
                return {
                    "valid": False,
                    "error": "Image file too large. Maximum size is 20MB."
                }
            
            # Try to open and validate image
            image = Image.open(io.BytesIO(image_data))
            
            # Check image format
            if image.format not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
                return {
                    "valid": False,
                    "error": "Unsupported image format. Please use JPEG, PNG, or WEBP."
                }
            
            # Check image dimensions
            width, height = image.size
            if width < 50 or height < 50:
                return {
                    "valid": False,
                    "error": "Image too small. Minimum size is 50x50 pixels."
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
    
    def detect_image_category(self, image: Image.Image, user_hint: str = None) -> str:
        """
        Detect the category of medical image to use appropriate analysis prompt
        
        Args:
            image: PIL Image object
            user_hint: Optional user hint about image type
            
        Returns:
            Category key for specialized analysis
        """
        # If user provides a hint, try to match it
        if user_hint:
            hint_lower = user_hint.lower()
            if any(word in hint_lower for word in ['skin', 'rash', 'mole', 'acne', 'dermatitis']):
                return "skin"
            elif any(word in hint_lower for word in ['xray', 'x-ray', 'ct', 'mri', 'scan']):
                return "xray"
            elif any(word in hint_lower for word in ['eye', 'vision', 'pupil', 'ophth']):
                return "eye"
            elif any(word in hint_lower for word in ['dental', 'tooth', 'teeth', 'gum', 'oral']):
                return "dental"
            elif any(word in hint_lower for word in ['wound', 'cut', 'injury', 'burn']):
                return "wound"
        
        # Default to general medical analysis
        return "general"
    
    def encode_image_for_api(self, image: Image.Image) -> str:
        """
        Encode image for OpenAI API
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded image string
        """
        # Resize image if too large to reduce API costs
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85)
        img_buffer.seek(0)
        
        return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    def extract_specialist_from_analysis(self, analysis_text: str, default_specialist: str) -> str:
        """
        Extract specialist recommendation from AI analysis text
        
        Args:
            analysis_text: The AI's analysis text
            default_specialist: Default specialist from category mapping
            
        Returns:
            Recommended specialist type
        """
        analysis_lower = analysis_text.lower()
        
        # Look for specific specialist mentions in the analysis
        specialist_keywords = {
            'orthopedist': ['orthopedist', 'orthopedic', 'bone fracture', 'broken bone', 'joint injury', 'musculoskeletal'],
            'cardiologist': ['cardiologist', 'heart', 'cardiac', 'cardiovascular'],
            'pulmonologist': ['pulmonologist', 'lung', 'respiratory', 'chest', 'breathing'],
            'neurologist': ['neurologist', 'brain', 'neurological', 'head injury', 'concussion'],
            'dermatologist': ['dermatologist', 'skin', 'rash', 'lesion', 'mole'],
            'ophthalmologist': ['ophthalmologist', 'eye', 'vision', 'retina', 'pupil'],
            'dentist': ['dentist', 'dental', 'tooth', 'teeth', 'oral'],
            'gastroenterologist': ['gastroenterologist', 'abdominal', 'stomach', 'intestinal'],
            'urologist': ['urologist', 'kidney', 'bladder', 'urinary'],
        }
        
        # Count keyword matches for each specialist
        specialist_scores = {}
        for specialist, keywords in specialist_keywords.items():
            score = sum(1 for keyword in keywords if keyword in analysis_lower)
            if score > 0:
                specialist_scores[specialist] = score
        
        # Return the specialist with the highest score
        if specialist_scores:
            recommended_specialist = max(specialist_scores, key=specialist_scores.get)
            print(f"🧠 AI Analysis detected specialist: {recommended_specialist} (score: {specialist_scores[recommended_specialist]})")
            return recommended_specialist.title()
        
        print(f"🧠 AI Analysis: No specific specialist detected, using default: {default_specialist}")
        return default_specialist

    def analyze_with_openai_vision(self, image: Image.Image, category: str) -> Dict[str, Any]:
        """
        Analyze medical image using OpenAI Vision API
        
        Args:
            image: PIL Image object
            category: Medical image category
            
        Returns:
            Analysis results from OpenAI
        """
        try:
            # Get the appropriate prompt for the medical category
            category_info = self.medical_categories.get(category, self.medical_categories["general"])
            prompt = category_info["prompt_template"]
            
            # Encode image for API
            base64_image = self.encode_image_for_api(image)
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Updated to current vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more consistent medical analysis
            )
            
            analysis_text = response.choices[0].message.content
            default_specialist = category_info["specialist"]
            
            # Extract specialist recommendation from analysis
            recommended_specialist = self.extract_specialist_from_analysis(analysis_text, default_specialist)
            
            return {
                "success": True,
                "analysis_text": analysis_text,
                "category": category_info["name"],
                "specialist_type": recommended_specialist,
                "model_used": "gpt-4o"
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI Vision API error: {e}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }
    
    def get_doctor_recommendations(self, specialist_type: str, user_city: str = None, sort_by: str = "rating", user_location: dict = None) -> List[Dict[str, Any]]:
        """
        Get doctor recommendations for the specialist type with sorting options
        
        Args:
            specialist_type: Type of specialist needed
            user_city: Optional user city for location-based recommendations
            sort_by: Sorting preference (rating, experience, location)
            
        Returns:
            List of recommended doctors
        """
        if not self.medical_recommender:
            return []
        
        try:
            # Map specialist types to database-friendly names
            specialist_map = {
                'Dermatologist': 'dermatologist',
                'Radiologist': 'radiologist',
                'Ophthalmologist': 'ophthalmologist', 
                'Dentist': 'dentist',
                'General Practitioner': 'general-physician',
                'Orthopedist': 'orthopedist',
                'Cardiologist': 'cardiologist',
                'Neurologist': 'neurologist',
                'Pulmonologist': 'pulmonologist',
                'Gastroenterologist': 'gastroenterologist',
                'Urologist': 'urologist',
                'Gynecologist': 'gynecologist',
                'Pediatrician': 'pediatrician',
                'Psychiatrist': 'psychiatrist',
                'Endocrinologist': 'endocrinologist',
                'Rheumatologist': 'rheumatologist'
            }
            
            db_specialist = specialist_map.get(specialist_type, 'general-physician')
            print(f"🔍 Getting doctors for specialist: {specialist_type} -> {db_specialist}")
            
            # Get doctor recommendations directly from the doctor_recommender
            user_lat = None
            user_lng = None
            if user_location:
                user_lat = user_location.get('latitude')
                user_lng = user_location.get('longitude')
            
            doctor_recommendations = self.medical_recommender.doctor_recommender.recommend_doctors(
                specialist_type=db_specialist,
                city=user_city,
                limit=5,
                sort_by=sort_by,
                user_lat=user_lat,
                user_lng=user_lng
            )
            
            print(f"📋 Raw doctor recommendations received: {len(doctor_recommendations)} doctors")
            
            # Return the doctors directly (they're already in the correct format)
            if doctor_recommendations:
                print(f"✅ Found {len(doctor_recommendations)} real doctors")
                return doctor_recommendations
            else:
                print("⚠️ No doctors found, creating sample doctors")
                sample_doctors = [
                    {
                        "name": f"Dr. Sample {specialist_type} 1",
                        "city": user_city or "Bangalore",
                        "specialty": specialist_type,
                        "dp_score": 4.5,
                        "year_of_experience": 10,
                        "consultation_fee": 500,
                        "distance_km": 999999,
                        "profile_url": "",
                        "google_map_link": ""
                    },
                    {
                        "name": f"Dr. Sample {specialist_type} 2", 
                        "city": user_city or "Mumbai",
                        "specialty": specialist_type,
                        "dp_score": 4.2,
                        "year_of_experience": 8,
                        "consultation_fee": 400,
                        "distance_km": 999999,
                        "profile_url": "",
                        "google_map_link": ""
                    },
                    {
                        "name": f"Dr. Sample {specialist_type} 3",
                        "city": user_city or "Delhi",
                        "specialty": specialist_type,
                        "dp_score": 4.7,
                        "year_of_experience": 12,
                        "consultation_fee": 600,
                        "distance_km": 999999,
                        "profile_url": "",
                        "google_map_link": ""
                    }
                ]
                return sample_doctors
            
        except Exception as e:
            self.logger.error(f"Error getting doctor recommendations: {e}")
            return []
    
    def analyze_medical_image(self, image_data: bytes, image_type: str = None, user_city: str = None, user_location: dict = None) -> Dict[str, Any]:
        """
        Main method to analyze medical image using OpenAI Vision API
        
        Args:
            image_data: Raw image bytes
            image_type: Optional hint about image type (skin, xray, eye, dental, wound, general)
            user_city: Optional user city for doctor recommendations
            user_location: Optional user location dict with latitude/longitude
            
        Returns:
            Analysis results with AI interpretation, specialist recommendations, and doctors
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
            
            # Detect image category
            category = self.detect_image_category(image, image_type)
            
            # Analyze with OpenAI Vision API
            ai_analysis = self.analyze_with_openai_vision(image, category)
            
            if not ai_analysis["success"]:
                return ai_analysis
            
            # Get doctor recommendations with default sorting and location
            specialist_type = ai_analysis["specialist_type"]
            doctors = self.get_doctor_recommendations(specialist_type, user_city, "rating", user_location)
            
            # **FIXED: Use the same method as chat system - format doctors as HTML**
            doctors_html = ""
            if doctors and self.medical_recommender and hasattr(self.medical_recommender, 'doctor_recommender'):
                try:
                    # Use the exact same method that works in chat system
                    doctors_html = self.medical_recommender.doctor_recommender.format_doctor_recommendations(doctors, specialist_type)
                    print(f"✅ Generated HTML table for {len(doctors)} doctors")
                except Exception as e:
                    print(f"⚠️ Failed to format doctors as HTML: {e}")
                    doctors_html = f"<p>Found {len(doctors)} {specialist_type.lower()}s but failed to format table.</p>"
            else:
                doctors_html = f"<p>No {specialist_type.lower()}s found in your area.</p>"
            
            return {
                "success": True,
                "analysis": {
                    "ai_interpretation": ai_analysis["analysis_text"],
                    "category": ai_analysis["category"],
                    "specialist_type": specialist_type,
                    "doctors": doctors,  # Keep raw data for compatibility
                    "doctors_html": doctors_html,  # **NEW: Pre-formatted HTML table**
                    "model_used": ai_analysis["model_used"],
                    "image_info": {
                        "dimensions": validation_result["dimensions"],
                        "format": validation_result["format"],
                        "category_detected": category
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing medical image: {e}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }

# Global analyzer instance
medical_image_analyzer = MedicalImageAnalyzer()

def analyze_medical_image(image_data: bytes, image_type: str = None, user_city: str = None, user_location: dict = None) -> Dict[str, Any]:
    """
    Convenience function to analyze medical image
    
    Args:
        image_data: Raw image bytes
        image_type: Optional image type hint
        user_city: Optional user city
        user_location: Optional user location dict with latitude/longitude
        
    Returns:
        Analysis results
    """
    return medical_image_analyzer.analyze_medical_image(image_data, image_type, user_city, user_location)

# Test the analyzer
if __name__ == "__main__":
    print("🧪 Testing Medical Image Analyzer...")
    
    # Test with OpenAI API if available
    try:
        # Create a simple test image
        test_image = Image.new('RGB', (300, 300), color='lightblue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        test_data = img_bytes.getvalue()
        
        # Test analysis
        result = analyze_medical_image(test_data, "general")
        print("Test result:", result.get("success", False))
        
    except Exception as e:
        print(f"Test failed: {e}")

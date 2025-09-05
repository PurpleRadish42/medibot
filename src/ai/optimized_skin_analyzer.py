# src/ai/optimized_skin_analyzer.py
"""
Optimized Skin Condition Image Analyzer
Fast, accurate analysis with <10 second response time
"""
import io
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import colorsys
import math

# Import the medical recommender for doctor suggestions
try:
    from src.llm.recommender import MedicalRecommender
    MEDICAL_RECOMMENDER_AVAILABLE = True
except ImportError:
    MEDICAL_RECOMMENDER_AVAILABLE = False
    print("Warning: MedicalRecommender not available for optimized skin analyzer")

class OptimizedSkinAnalyzer:
    """
    Optimized skin condition analyzer focused on speed and accuracy
    Uses computer vision techniques and heuristics instead of heavy ML models
    """
    
    def __init__(self):
        """Initialize the optimized analyzer"""
        self.logger = logging.getLogger(__name__)
        
        # Cache for analysis results
        self.analysis_cache = {}
        self.cache_max_size = 100
        
        # Skin condition knowledge base with visual characteristics
        self.condition_patterns = {
            "Melanoma": {
                "color_ranges": [(30, 60, 60), (80, 120, 100)],  # Dark brown/black
                "texture_score": 0.8,
                "asymmetry_threshold": 0.6,
                "border_irregularity": 0.7,
                "base_probability": 20,
                "specialist": "Dermatologist",
                "urgency": "HIGH",
                "description": "Serious form of skin cancer requiring immediate attention"
            },
            "Basal Cell Carcinoma": {
                "color_ranges": [(120, 180, 150), (180, 220, 200)],  # Pink/red/pearly
                "texture_score": 0.5,
                "raised_appearance": 0.6,
                "base_probability": 25,
                "specialist": "Dermatologist", 
                "urgency": "MODERATE",
                "description": "Most common form of skin cancer, usually treatable"
            },
            "Eczema": {
                "color_ranges": [(150, 80, 80), (220, 120, 120)],  # Red/inflamed
                "texture_score": 0.8,
                "pattern_type": "patches",
                "base_probability": 45,
                "specialist": "Dermatologist",
                "urgency": "LOW",
                "description": "Inflammatory skin condition causing itchy, red patches"
            },
            "Psoriasis": {
                "color_ranges": [(180, 180, 180), (220, 220, 220)],  # Silver/white scales
                "texture_score": 0.9,
                "scale_pattern": True,
                "base_probability": 35,
                "specialist": "Dermatologist",
                "urgency": "LOW", 
                "description": "Autoimmune condition causing scaly skin patches"
            },
            "Acne": {
                "color_ranges": [(180, 100, 100), (250, 180, 180)],  # Red bumps/inflammation
                "texture_score": 0.4,
                "bump_pattern": True,
                "base_probability": 50,
                "specialist": "Dermatologist",
                "urgency": "LOW",
                "description": "Common skin condition causing pimples and blemishes"
            },
            "Seborrheic Keratosis": {
                "color_ranges": [(100, 80, 60), (160, 120, 90)],  # Brown/tan waxy
                "texture_score": 0.6,
                "raised_appearance": 0.8,
                "base_probability": 30,
                "specialist": "Dermatologist",
                "urgency": "LOW",
                "description": "Non-cancerous skin growth, typically brown or black"
            },
            "Dermatitis": {
                "color_ranges": [(160, 100, 100), (200, 140, 140)],  # Red/inflamed variable
                "texture_score": 0.7,
                "pattern_type": "irregular",
                "base_probability": 40,
                "specialist": "Dermatologist",
                "urgency": "LOW",
                "description": "General skin inflammation with various causes"
            }
        }
        
        # Initialize medical recommender if available
        self.medical_recommender = None
        if MEDICAL_RECOMMENDER_AVAILABLE:
            try:
                self.medical_recommender = MedicalRecommender()
            except Exception as e:
                self.logger.warning(f"Failed to initialize MedicalRecommender: {e}")
    
    def validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Fast image validation with enhanced checks
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
            if image.format not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
                return {
                    "valid": False,
                    "error": "Unsupported image format. Please use JPEG, PNG, or WEBP."
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
            
            # Calculate image hash for caching
            image_hash = hashlib.md5(image_data).hexdigest()
            
            return {
                "valid": True,
                "image": image,
                "dimensions": (width, height),
                "format": image.format,
                "hash": image_hash
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid image file: {str(e)}"
            }
    
    def extract_color_features(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract color-based features for skin analysis
        """
        try:
            # Resize for faster processing
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            pixels = list(image.getdata())
            
            # Color analysis
            colors = {'red': [], 'green': [], 'blue': []}
            hsv_values = []
            
            for r, g, b in pixels:
                colors['red'].append(r)
                colors['green'].append(g) 
                colors['blue'].append(b)
                
                # Convert to HSV
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                hsv_values.append((h*360, s*100, v*100))
            
            # Calculate statistics
            avg_red = sum(colors['red']) / len(colors['red'])
            avg_green = sum(colors['green']) / len(colors['green'])
            avg_blue = sum(colors['blue']) / len(colors['blue'])
            
            # Calculate color variance (texture indicator)
            red_variance = sum((r - avg_red) ** 2 for r in colors['red']) / len(colors['red'])
            color_variance = (red_variance + 
                            sum((g - avg_green) ** 2 for g in colors['green']) / len(colors['green']) +
                            sum((b - avg_blue) ** 2 for b in colors['blue']) / len(colors['blue'])) / 3
            
            # Dominant colors
            color_ranges = self._get_dominant_color_ranges(hsv_values)
            
            # Color uniformity (inversely related to texture)
            uniformity = 1.0 / (1.0 + color_variance / 1000.0)
            
            return {
                "avg_rgb": (avg_red, avg_green, avg_blue),
                "color_variance": color_variance,
                "uniformity": uniformity,
                "dominant_ranges": color_ranges,
                "texture_score": min(color_variance / 2000.0, 1.0)  # Normalized texture score
            }
            
        except Exception as e:
            self.logger.error(f"Color feature extraction error: {e}")
            return {
                "avg_rgb": (128, 128, 128),
                "color_variance": 1000,
                "uniformity": 0.5,
                "dominant_ranges": [],
                "texture_score": 0.5
            }
    
    def _get_dominant_color_ranges(self, hsv_values: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """
        Get dominant color ranges from HSV values
        """
        try:
            # Simple clustering by hue ranges
            hue_buckets = {}
            for h, s, v in hsv_values:
                bucket = int(h // 30) * 30  # 30-degree buckets
                if bucket not in hue_buckets:
                    hue_buckets[bucket] = []
                hue_buckets[bucket].append((h, s, v))
            
            # Get top 3 dominant ranges
            dominant = sorted(hue_buckets.items(), key=lambda x: len(x[1]), reverse=True)[:3]
            
            ranges = []
            for bucket, values in dominant:
                if len(values) > len(hsv_values) * 0.1:  # At least 10% of pixels
                    avg_h = sum(h for h, s, v in values) / len(values)
                    avg_s = sum(s for h, s, v in values) / len(values)
                    avg_v = sum(v for h, s, v in values) / len(values)
                    ranges.append((avg_h, avg_s, avg_v))
            
            return ranges
            
        except Exception:
            return []
    
    def extract_shape_features(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract shape and symmetry features
        """
        try:
            # Convert to grayscale for edge detection
            gray = image.convert('L')
            
            # Simple edge detection using filter
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edge_pixels = list(edges.getdata())
            
            # Calculate edge density (border irregularity indicator)
            edge_density = sum(1 for p in edge_pixels if p > 50) / len(edge_pixels)
            
            # Asymmetry check - compare left/right halves
            width, height = gray.size
            left_half = gray.crop((0, 0, width//2, height))
            right_half = gray.crop((width//2, 0, width, height))
            right_half = right_half.transpose(Image.FLIP_LEFT_RIGHT)  # Mirror
            
            # Resize to same size for comparison
            left_pixels = list(left_half.getdata())
            right_pixels = list(right_half.resize(left_half.size).getdata())
            
            # Calculate asymmetry score
            asymmetry = sum(abs(l - r) for l, r in zip(left_pixels, right_pixels)) / (len(left_pixels) * 255)
            
            return {
                "edge_density": edge_density,
                "asymmetry_score": asymmetry,
                "border_irregularity": edge_density * 2,  # Weighted edge density
                "shape_score": 1.0 - asymmetry  # Higher score = more symmetric
            }
            
        except Exception as e:
            self.logger.error(f"Shape feature extraction error: {e}")
            return {
                "edge_density": 0.3,
                "asymmetry_score": 0.3,
                "border_irregularity": 0.3,
                "shape_score": 0.7
            }
    
    def analyze_condition_probability(self, color_features: Dict, shape_features: Dict) -> List[Dict[str, Any]]:
        """
        Analyze skin condition probabilities based on extracted features
        """
        results = []
        
        for condition_name, pattern in self.condition_patterns.items():
            probability = pattern["base_probability"]
            confidence_factors = []
            
            # Color matching
            color_match = self._match_color_pattern(color_features, pattern)
            probability += color_match * 20
            confidence_factors.append(f"Color match: {color_match:.1f}")
            
            # Texture analysis
            texture_match = self._match_texture_pattern(color_features, shape_features, pattern)
            probability += texture_match * 15
            confidence_factors.append(f"Texture: {texture_match:.1f}")
            
            # Shape analysis
            shape_match = self._match_shape_pattern(shape_features, pattern)
            probability += shape_match * 10
            confidence_factors.append(f"Shape: {shape_match:.1f}")
            
            # Border analysis for cancer screening
            if "asymmetry_threshold" in pattern or "border_irregularity" in pattern:
                border_score = self._assess_cancer_risk(shape_features, pattern)
                probability += border_score * 25
                confidence_factors.append(f"Risk factors: {border_score:.1f}")
            
            # Normalize probability
            probability = max(10, min(95, probability))
            
            results.append({
                "name": condition_name,
                "confidence": round(probability, 1),
                "description": pattern["description"],
                "specialist": pattern["specialist"],
                "urgency": pattern["urgency"],
                "confidence_factors": confidence_factors
            })
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Return top 5 results
        return results[:5]
    
    def _match_color_pattern(self, color_features: Dict, pattern: Dict) -> float:
        """
        Enhanced color matching with better RGB range handling
        """
        try:
            if "color_ranges" not in pattern:
                return 0.5
            
            avg_rgb = color_features["avg_rgb"]
            color_ranges = pattern["color_ranges"]
            
            best_match = 0.0
            
            # Check each color range
            for r_range, g_range, b_range in [color_ranges[0], color_ranges[1] if len(color_ranges) > 1 else color_ranges[0]]:
                # Calculate distance from expected color
                r_dist = abs(avg_rgb[0] - r_range) / 255.0
                g_dist = abs(avg_rgb[1] - g_range) / 255.0  
                b_dist = abs(avg_rgb[2] - b_range) / 255.0
                
                # Euclidean distance in RGB space
                color_distance = (r_dist**2 + g_dist**2 + b_dist**2)**0.5
                match_score = max(0, 1.0 - color_distance)
                
                best_match = max(best_match, match_score)
            
            return best_match
            
        except Exception:
            return 0.5
    
    def _match_texture_pattern(self, color_features: Dict, shape_features: Dict, pattern: Dict) -> float:
        """
        Match texture features against condition pattern
        """
        try:
            expected_texture = pattern.get("texture_score", 0.5)
            actual_texture = color_features.get("texture_score", 0.5)
            
            # Calculate how close the texture matches
            texture_diff = abs(expected_texture - actual_texture)
            texture_match = max(0, 1.0 - texture_diff * 2)
            
            return texture_match
            
        except Exception:
            return 0.5
    
    def _match_shape_pattern(self, shape_features: Dict, pattern: Dict) -> float:
        """
        Match shape features against condition pattern
        """
        try:
            shape_score = 0.5
            
            # Check for raised appearance
            if "raised_appearance" in pattern:
                edge_density = shape_features.get("edge_density", 0.3)
                expected_raised = pattern["raised_appearance"]
                raised_match = 1.0 - abs(edge_density - expected_raised)
                shape_score = max(shape_score, raised_match)
            
            # Check for bump patterns (acne)
            if pattern.get("bump_pattern", False):
                edge_density = shape_features.get("edge_density", 0.3)
                if edge_density > 0.4:
                    shape_score = 0.8
            
            # Check for scale patterns (psoriasis)
            if pattern.get("scale_pattern", False):
                texture_variance = shape_features.get("border_irregularity", 0.3)
                if texture_variance > 0.5:
                    shape_score = 0.7
            
            return shape_score
            
        except Exception:
            return 0.5
    
    def _assess_cancer_risk(self, shape_features: Dict, pattern: Dict) -> float:
        """
        Assess cancer risk based on ABCDE criteria simulation
        """
        try:
            risk_score = 0.0
            
            # Asymmetry (A)
            if "asymmetry_threshold" in pattern:
                asymmetry = shape_features.get("asymmetry_score", 0.3)
                threshold = pattern["asymmetry_threshold"]
                if asymmetry > threshold:
                    risk_score += 0.3
            
            # Border irregularity (B)
            if "border_irregularity" in pattern:
                border_irreg = shape_features.get("border_irregularity", 0.3)
                threshold = pattern["border_irregularity"]
                if border_irreg > threshold:
                    risk_score += 0.4
            
            return min(1.0, risk_score)
            
        except Exception:
            return 0.2
    
    def get_doctor_recommendations(self, specialist_type: str, user_city: str = None) -> List[Dict[str, Any]]:
        """
        Get doctor recommendations for the specialist type
        """
        if not self.medical_recommender:
            return []
        
        try:
            # Use the existing doctor recommendation system
            doctor_recommendations = self.medical_recommender.get_doctor_recommendations(
                specialist_type, user_city or "Bangalore"  # Default city
            )
            
            # Parse the recommendations (they come as formatted text)
            doctors = []
            if "📍 DOCTOR RECOMMENDATIONS" in doctor_recommendations:
                lines = doctor_recommendations.split('\n')
                for line in lines:
                    if "Dr." in line and "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 3:
                            name = parts[0].strip()
                            city = parts[1].strip() if len(parts) > 1 else user_city or "Bangalore"
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
        Optimized main analysis method with caching and fast processing
        """
        try:
            start_time = time.time()
            
            # Validate image
            validation_result = self.validate_image(image_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            image = validation_result["image"]
            image_hash = validation_result["hash"]
            
            # Check cache first
            if image_hash in self.analysis_cache:
                cached_result = self.analysis_cache[image_hash].copy()
                cached_result["analysis"]["cache_hit"] = True
                cached_result["analysis"]["processing_time"] = time.time() - start_time
                return cached_result
            
            # Preprocess image for analysis
            processed_image = self._preprocess_image(image)
            
            # Extract features
            color_features = self.extract_color_features(processed_image)
            shape_features = self.extract_shape_features(processed_image)
            
            # Analyze conditions
            conditions = self.analyze_condition_probability(color_features, shape_features)
            
            # Get top specialist recommendation
            top_condition = conditions[0] if conditions else None
            specialist_type = top_condition["specialist"] if top_condition else "Dermatologist"
            
            # Get doctor recommendations
            doctors = self.get_doctor_recommendations(specialist_type, user_city)
            
            processing_time = time.time() - start_time
            
            result = {
                "success": True,
                "analysis": {
                    "conditions": [
                        {
                            "name": condition["name"],
                            "confidence": condition["confidence"],
                            "description": condition["description"],
                            "urgency": condition["urgency"]
                        }
                        for condition in conditions
                    ],
                    "specialist_type": specialist_type,
                    "doctors": doctors,
                    "image_info": {
                        "dimensions": validation_result["dimensions"],
                        "format": validation_result["format"]
                    },
                    "analysis_features": {
                        "color_variance": round(color_features["color_variance"], 2),
                        "texture_score": round(color_features["texture_score"], 2),
                        "asymmetry_score": round(shape_features["asymmetry_score"], 2),
                        "edge_density": round(shape_features["edge_density"], 2)
                    },
                    "analysis_type": "Optimized Analysis",
                    "processing_time": round(processing_time, 2),
                    "cache_hit": False,
                    "accuracy_note": "Fast analysis using computer vision techniques and medical heuristics"
                }
            }
            
            # Cache result
            self._cache_result(image_hash, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Optimized analysis failed: {e}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Fast image preprocessing for analysis
        """
        try:
            # Resize to optimal size for fast processing
            target_size = (256, 256)
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Enhance image quality for better analysis
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Slight contrast boost
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)  # Slight sharpness boost
            
            return image
            
        except Exception as e:
            self.logger.error(f"Preprocessing error: {e}")
            return image
    
    def _cache_result(self, image_hash: str, result: Dict[str, Any]):
        """
        Cache analysis result for faster subsequent requests
        """
        try:
            # Remove oldest entries if cache is full
            if len(self.analysis_cache) >= self.cache_max_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = list(self.analysis_cache.keys())[0]
                del self.analysis_cache[oldest_key]
            
            # Cache the result
            self.analysis_cache[image_hash] = result.copy()
            
        except Exception as e:
            self.logger.error(f"Caching error: {e}")

# Global optimized analyzer instance
optimized_skin_analyzer = OptimizedSkinAnalyzer()

def analyze_skin_image_optimized(image_data: bytes, user_city: str = None) -> Dict[str, Any]:
    """
    Convenience function for optimized skin condition analysis
    
    Args:
        image_data: Raw image bytes
        user_city: Optional user city
        
    Returns:
        Analysis results with <10 second processing time
    """
    return optimized_skin_analyzer.analyze_skin_condition(image_data, user_city)

# Test the optimized analyzer
if __name__ == "__main__":
    print("🚀 Testing Optimized Skin Condition Analyzer...")
    
    # Create a simple test image
    test_image = Image.new('RGB', (300, 300), color='red')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    test_data = img_bytes.getvalue()
    
    # Test analysis
    start = time.time()
    result = analyze_skin_image_optimized(test_data)
    end = time.time()
    
    print(f"⏱️ Analysis completed in {end - start:.2f} seconds")
    print(f"✅ Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"📊 Conditions found: {len(result['analysis']['conditions'])}")
        print(f"🎯 Analysis type: {result['analysis']['analysis_type']}")
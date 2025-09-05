# src/ai/medical_specialist_models.py
"""
Specialized Medical Models Integration
Advanced AI models for specific medical domains
"""
import logging
import base64
from typing import Dict, List, Any, Optional, Tuple
import json
import io

# Core imports
import numpy as np
from PIL import Image
import cv2

# Try to import advanced medical libraries
try:
    import torch
    import torchvision.transforms as transforms
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        AutoImageProcessor, AutoModelForImageClassification,
        pipeline, CLIPProcessor, CLIPModel
    )
    ADVANCED_MODELS_AVAILABLE = True
    print("✅ Advanced medical models available")
except ImportError as e:
    ADVANCED_MODELS_AVAILABLE = False
    print(f"⚠️ Advanced models not available: {e}")

# Medical model configurations
MEDICAL_MODEL_CONFIGS = {
    'dermatology': {
        'model_name': 'microsoft/DinoV2',
        'description': 'Skin condition analysis',
        'specialties': ['melanoma', 'eczema', 'psoriasis', 'acne'],
        'confidence_threshold': 0.7
    },
    'radiology': {
        'model_name': 'microsoft/resnet-50',
        'description': 'X-ray and CT scan analysis',
        'specialties': ['pneumonia', 'fractures', 'tumors'],
        'confidence_threshold': 0.8
    },
    'ophthalmology': {
        'model_name': 'google/vit-base-patch16-224',
        'description': 'Eye condition analysis',
        'specialties': ['diabetic_retinopathy', 'glaucoma', 'cataracts'],
        'confidence_threshold': 0.75
    },
    'pathology': {
        'model_name': 'microsoft/swin-tiny-patch4-window7-224',
        'description': 'Tissue and cell analysis',
        'specialties': ['cancer_detection', 'tissue_classification'],
        'confidence_threshold': 0.85
    }
}

class MedicalSpecialistModel:
    """
    Individual specialist medical model wrapper
    """
    
    def __init__(self, specialty: str, config: Dict[str, Any]):
        """
        Initialize specialist model
        
        Args:
            specialty: Medical specialty (dermatology, radiology, etc.)
            config: Model configuration
        """
        self.specialty = specialty
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.pipeline = None
        
        if ADVANCED_MODELS_AVAILABLE:
            self._load_model()
        else:
            self.logger.warning(f"Advanced models not available for {specialty}")
    
    def _load_model(self):
        """Load the specialized model"""
        try:
            model_name = self.config['model_name']
            self.logger.info(f"Loading {self.specialty} model: {model_name}")
            
            # Try to load as image classification model first
            try:
                self.processor = AutoImageProcessor.from_pretrained(model_name)
                self.model = AutoModelForImageClassification.from_pretrained(model_name)
                self.logger.info(f"✅ Loaded {self.specialty} image model")
                return
            except Exception:
                pass
            
            # Try to load as general vision model
            try:
                if 'vit' in model_name.lower() or 'dino' in model_name.lower():
                    self.processor = AutoImageProcessor.from_pretrained(model_name)
                    self.model = AutoModel.from_pretrained(model_name)
                    self.logger.info(f"✅ Loaded {self.specialty} vision model")
                    return
            except Exception:
                pass
            
            # Try to load as pipeline
            try:
                self.pipeline = pipeline(
                    "image-classification",
                    model=model_name,
                    return_all_scores=True
                )
                self.logger.info(f"✅ Loaded {self.specialty} pipeline")
                return
            except Exception:
                pass
            
            # Use fallback model
            self._load_fallback_model()
            
        except Exception as e:
            self.logger.error(f"Failed to load {self.specialty} model: {e}")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load fallback model for the specialty"""
        try:
            # Use general medical classification
            fallback_models = {
                'dermatology': 'microsoft/resnet-50',
                'radiology': 'microsoft/resnet-50',
                'ophthalmology': 'google/vit-base-patch16-224',
                'pathology': 'microsoft/resnet-50'
            }
            
            fallback_name = fallback_models.get(self.specialty, 'microsoft/resnet-50')
            
            try:
                self.pipeline = pipeline(
                    "image-classification",
                    model=fallback_name,
                    return_all_scores=True
                )
                self.logger.info(f"✅ Loaded fallback model for {self.specialty}")
            except Exception:
                # Use basic rule-based analysis
                self.logger.warning(f"Using rule-based analysis for {self.specialty}")
                
        except Exception as e:
            self.logger.error(f"Fallback model loading failed for {self.specialty}: {e}")
    
    def analyze_image(self, image_data: bytes, image_type: str = None) -> Dict[str, Any]:
        """
        Analyze image using specialist model
        
        Args:
            image_data: Raw image bytes
            image_type: Type of medical image
            
        Returns:
            Analysis results
        """
        try:
            # Preprocess image
            image = self._preprocess_image(image_data)
            if image is None:
                return {'error': 'Failed to preprocess image'}
            
            # Use model if available
            if self.pipeline is not None:
                return self._analyze_with_pipeline(image)
            elif self.model is not None and self.processor is not None:
                return self._analyze_with_model(image)
            else:
                return self._analyze_with_rules(image)
                
        except Exception as e:
            self.logger.error(f"{self.specialty} analysis error: {e}")
            return {
                'error': f'{self.specialty} analysis failed: {str(e)}',
                'fallback_analysis': self._basic_analysis(image_type)
            }
    
    def _preprocess_image(self, image_data: bytes) -> Optional[Image.Image]:
        """Preprocess image for analysis"""
        try:
            # Convert bytes to PIL Image
            if isinstance(image_data, str):
                # Handle base64 encoded images
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                image_data = base64.b64decode(image_data)
            
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Image preprocessing error: {e}")
            return None
    
    def _analyze_with_pipeline(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze using Hugging Face pipeline"""
        try:
            results = self.pipeline(image)
            
            # Convert to standard format
            conditions = []
            for result in results[:5]:  # Top 5 predictions
                confidence = result['score'] * 100
                if confidence > (self.config['confidence_threshold'] * 100):
                    conditions.append({
                        'name': result['label'],
                        'confidence': confidence,
                        'specialty': self.specialty
                    })
            
            return {
                'success': True,
                'conditions': conditions,
                'model_type': 'pipeline',
                'specialty': self.specialty
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline analysis error: {e}")
            return {'error': f'Pipeline analysis failed: {str(e)}'}
    
    def _analyze_with_model(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze using direct model inference"""
        try:
            # Preprocess with processor
            inputs = self.processor(image, return_tensors="pt")
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Process outputs based on model type
            if hasattr(outputs, 'logits'):
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                top_probs, top_indices = torch.topk(probabilities, k=5)
                
                conditions = []
                for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0])):
                    confidence = prob.item() * 100
                    if confidence > (self.config['confidence_threshold'] * 100):
                        conditions.append({
                            'name': f'{self.specialty}_condition_{idx.item()}',
                            'confidence': confidence,
                            'specialty': self.specialty
                        })
                
                return {
                    'success': True,
                    'conditions': conditions,
                    'model_type': 'direct',
                    'specialty': self.specialty
                }
            else:
                # Feature extraction model
                return {
                    'success': True,
                    'features_extracted': True,
                    'feature_shape': str(outputs.last_hidden_state.shape),
                    'specialty': self.specialty
                }
                
        except Exception as e:
            self.logger.error(f"Model inference error: {e}")
            return {'error': f'Model inference failed: {str(e)}'}
    
    def _analyze_with_rules(self, image: Image.Image) -> Dict[str, Any]:
        """Rule-based analysis for fallback"""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Basic image analysis
            height, width = img_array.shape[:2]
            mean_intensity = np.mean(img_array)
            
            # Specialty-specific rules
            conditions = []
            
            if self.specialty == 'dermatology':
                conditions = self._dermatology_rules(img_array)
            elif self.specialty == 'radiology':
                conditions = self._radiology_rules(img_array)
            elif self.specialty == 'ophthalmology':
                conditions = self._ophthalmology_rules(img_array)
            elif self.specialty == 'pathology':
                conditions = self._pathology_rules(img_array)
            
            return {
                'success': True,
                'conditions': conditions,
                'model_type': 'rule_based',
                'specialty': self.specialty,
                'image_stats': {
                    'dimensions': f'{width}x{height}',
                    'mean_intensity': float(mean_intensity)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Rule-based analysis error: {e}")
            return {'error': f'Rule-based analysis failed: {str(e)}'}
    
    def _dermatology_rules(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Dermatology-specific rule-based analysis"""
        conditions = []
        
        # Color analysis for skin conditions
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Detect skin tones
        skin_lower = np.array([0, 20, 70])
        skin_upper = np.array([20, 255, 255])
        skin_mask = cv2.inRange(hsv, skin_lower, skin_upper)
        skin_percentage = (np.sum(skin_mask > 0) / skin_mask.size) * 100
        
        if skin_percentage > 30:
            # Analyze for potential skin conditions
            
            # Check for dark spots (potential melanoma indicators)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            dark_threshold = np.mean(gray) - 2 * np.std(gray)
            dark_areas = np.sum(gray < dark_threshold) / gray.size * 100
            
            if dark_areas > 5:
                conditions.append({
                    'name': 'Dark lesion detected',
                    'confidence': min(80, dark_areas * 10),
                    'recommendation': 'Consider dermatological evaluation',
                    'specialty': 'dermatology'
                })
            
            # Check for redness (inflammation/eczema)
            red_channel = img_array[:, :, 0]
            red_mean = np.mean(red_channel)
            if red_mean > 150:
                conditions.append({
                    'name': 'Inflammatory condition possible',
                    'confidence': min(70, (red_mean - 150) * 2),
                    'recommendation': 'Monitor for changes',
                    'specialty': 'dermatology'
                })
        
        return conditions
    
    def _radiology_rules(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Radiology-specific rule-based analysis"""
        conditions = []
        
        # Check if image looks like X-ray (high contrast, specific patterns)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        contrast = np.std(gray)
        
        if contrast > 50:  # High contrast typical of X-rays
            # Look for potential abnormalities
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size * 100
            
            if edge_density > 10:
                conditions.append({
                    'name': 'Structural findings detected',
                    'confidence': min(75, edge_density * 5),
                    'recommendation': 'Radiologist review recommended',
                    'specialty': 'radiology'
                })
        
        return conditions
    
    def _ophthalmology_rules(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Ophthalmology-specific rule-based analysis"""
        conditions = []
        
        # Look for circular patterns (eyes)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
            param1=100, param2=30, minRadius=20, maxRadius=200
        )
        
        if circles is not None:
            conditions.append({
                'name': 'Eye structure detected',
                'confidence': 70,
                'recommendation': 'Eye examination by specialist',
                'specialty': 'ophthalmology'
            })
        
        return conditions
    
    def _pathology_rules(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Pathology-specific rule-based analysis"""
        conditions = []
        
        # Basic tissue analysis
        # Look for cellular structures or patterns
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detect potential cellular structures
        kernel = np.ones((3, 3), np.uint8)
        morphology = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        
        structural_complexity = np.std(morphology)
        if structural_complexity > 40:
            conditions.append({
                'name': 'Tissue structure analysis',
                'confidence': min(65, structural_complexity),
                'recommendation': 'Pathologist evaluation needed',
                'specialty': 'pathology'
            })
        
        return conditions
    
    def _basic_analysis(self, image_type: str = None) -> Dict[str, Any]:
        """Basic fallback analysis"""
        return {
            'specialty': self.specialty,
            'recommendation': f'Consult {self.specialty} specialist',
            'analysis_type': 'basic',
            'confidence': 50
        }

class MedicalSpecialistModelManager:
    """
    Manager for all medical specialist models
    """
    
    def __init__(self):
        """Initialize the model manager"""
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self._load_all_models()
    
    def _load_all_models(self):
        """Load all specialist models"""
        for specialty, config in MEDICAL_MODEL_CONFIGS.items():
            try:
                self.models[specialty] = MedicalSpecialistModel(specialty, config)
                self.logger.info(f"✅ Loaded {specialty} specialist model")
            except Exception as e:
                self.logger.error(f"Failed to load {specialty} model: {e}")
    
    def analyze_with_specialist(self, image_data: bytes, specialty: str, 
                              image_type: str = None) -> Dict[str, Any]:
        """
        Analyze image with specific specialist model
        
        Args:
            image_data: Raw image bytes
            specialty: Medical specialty
            image_type: Type of medical image
            
        Returns:
            Specialist analysis results
        """
        if specialty not in self.models:
            return {
                'error': f'Specialist model {specialty} not available',
                'available_specialties': list(self.models.keys())
            }
        
        try:
            model = self.models[specialty]
            result = model.analyze_image(image_data, image_type)
            
            # Add specialist context
            result['specialist_analysis'] = True
            result['model_config'] = MEDICAL_MODEL_CONFIGS[specialty]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Specialist analysis error for {specialty}: {e}")
            return {
                'error': f'Specialist analysis failed: {str(e)}',
                'specialty': specialty
            }
    
    def get_best_specialist(self, image_type: str, symptoms: str = "") -> str:
        """
        Recommend best specialist based on image type and symptoms
        
        Args:
            image_type: Type of medical image
            symptoms: Patient symptoms
            
        Returns:
            Recommended specialist
        """
        image_type_lower = image_type.lower() if image_type else ""
        symptoms_lower = symptoms.lower() if symptoms else ""
        
        # Map image types to specialties
        if any(term in image_type_lower for term in ['skin', 'mole', 'rash']):
            return 'dermatology'
        elif any(term in image_type_lower for term in ['xray', 'x-ray', 'chest', 'lung']):
            return 'radiology'
        elif any(term in image_type_lower for term in ['eye', 'retina', 'fundus']):
            return 'ophthalmology'
        elif any(term in image_type_lower for term in ['tissue', 'biopsy', 'microscopy']):
            return 'pathology'
        
        # Map symptoms to specialties
        if any(term in symptoms_lower for term in ['skin', 'mole', 'rash', 'eczema']):
            return 'dermatology'
        elif any(term in symptoms_lower for term in ['chest', 'lung', 'breathing']):
            return 'radiology'
        elif any(term in symptoms_lower for term in ['eye', 'vision', 'blind']):
            return 'ophthalmology'
        
        # Default to dermatology for general image analysis
        return 'dermatology'
    
    def get_available_specialties(self) -> List[str]:
        """Get list of available medical specialties"""
        return list(self.models.keys())

# Global manager instance
specialist_manager = MedicalSpecialistModelManager()

def analyze_with_medical_specialist(image_data: bytes, specialty: str = None, 
                                  image_type: str = None, symptoms: str = "") -> Dict[str, Any]:
    """
    Convenience function for specialist medical analysis
    
    Args:
        image_data: Raw image bytes
        specialty: Specific medical specialty (optional)
        image_type: Type of medical image
        symptoms: Patient symptoms
        
    Returns:
        Specialist analysis results
    """
    if specialty is None:
        specialty = specialist_manager.get_best_specialist(image_type, symptoms)
    
    return specialist_manager.analyze_with_specialist(image_data, specialty, image_type)

if __name__ == "__main__":
    print("🏥 Testing Medical Specialist Models...")
    
    # Test model loading
    available = specialist_manager.get_available_specialties()
    print(f"Available specialties: {available}")
    
    # Test specialist recommendation
    recommended = specialist_manager.get_best_specialist("skin lesion", "dark mole")
    print(f"Recommended specialist: {recommended}")

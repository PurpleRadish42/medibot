# src/ai/medical_ai_lite.py
"""
Lightweight Medical AI System
Simplified version that works without heavy dependencies
"""
import logging
import base64
import io
import json
from typing import Dict, List, Any, Optional
import numpy as np
from PIL import Image
import cv2

# Try to import advanced libraries, fall back gracefully
try:
    import torch
    TORCH_AVAILABLE = True
    print("✅ PyTorch available for medical AI")
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available, using lightweight mode")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    print("✅ Transformers available for medical AI")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available, using rule-based analysis")

# Medical knowledge base for lightweight analysis
MEDICAL_CONDITIONS_DB = {
    'skin_conditions': {
        'melanoma': {
            'description': 'Malignant skin cancer requiring urgent attention',
            'keywords': ['dark', 'irregular', 'asymmetric', 'changing', 'large'],
            'urgency': 'URGENT',
            'specialist': 'Dermatologist',
            'confidence_factors': ['color_variation', 'irregular_border', 'size']
        },
        'basal_cell_carcinoma': {
            'description': 'Most common skin cancer, usually non-melanoma',
            'keywords': ['bump', 'growth', 'pearly', 'translucent'],
            'urgency': 'MODERATE',
            'specialist': 'Dermatologist',
            'confidence_factors': ['raised_appearance', 'smooth_surface']
        },
        'eczema': {
            'description': 'Inflammatory skin condition',
            'keywords': ['red', 'inflamed', 'itchy', 'dry', 'patches'],
            'urgency': 'LOW',
            'specialist': 'Dermatologist',
            'confidence_factors': ['redness', 'inflammation']
        },
        'psoriasis': {
            'description': 'Autoimmune skin condition',
            'keywords': ['scaly', 'patches', 'silvery', 'thick', 'plaques'],
            'urgency': 'MODERATE',
            'specialist': 'Dermatologist',
            'confidence_factors': ['scaling', 'defined_borders']
        },
        'acne': {
            'description': 'Common skin condition affecting hair follicles',
            'keywords': ['pimple', 'blackhead', 'whitehead', 'comedone'],
            'urgency': 'LOW',
            'specialist': 'Dermatologist',
            'confidence_factors': ['multiple_lesions', 'face_location']
        }
    },
    'chest_conditions': {
        'pneumonia': {
            'description': 'Lung infection requiring medical attention',
            'keywords': ['consolidation', 'opacity', 'infiltrate'],
            'urgency': 'URGENT',
            'specialist': 'Pulmonologist',
            'confidence_factors': ['lung_opacity', 'bilateral_involvement']
        },
        'normal_chest': {
            'description': 'No apparent abnormalities',
            'keywords': ['clear', 'normal', 'no_findings'],
            'urgency': 'LOW',
            'specialist': 'General Practitioner',
            'confidence_factors': ['clear_lung_fields', 'normal_heart']
        }
    }
}

class LightweightMedicalAI:
    """
    Lightweight medical AI that works without heavy dependencies
    """
    
    def __init__(self):
        """Initialize the lightweight medical AI"""
        self.logger = logging.getLogger(__name__)
        self.available_models = []
        
        # Try to load available models
        if TRANSFORMERS_AVAILABLE:
            self._load_transformers_models()
        
        self.logger.info(f"Lightweight Medical AI initialized with {len(self.available_models)} models")
    
    def _load_transformers_models(self):
        """Load available transformer models"""
        try:
            # Try to load image classification pipeline
            self.image_classifier = pipeline("image-classification", 
                                           model="microsoft/resnet-50")
            self.available_models.append('image_classification')
            self.logger.info("✅ Image classification model loaded")
        except Exception as e:
            self.logger.warning(f"Failed to load image classifier: {e}")
        
        try:
            # Try to load text classification for symptoms
            self.text_classifier = pipeline("text-classification")
            self.available_models.append('text_classification')
            self.logger.info("✅ Text classification model loaded")
        except Exception as e:
            self.logger.warning(f"Failed to load text classifier: {e}")
    
    def analyze_medical_image_lite(self, image_data: bytes, image_type: str = 'skin', 
                                  symptoms: str = '') -> Dict[str, Any]:
        """
        Lightweight medical image analysis
        
        Args:
            image_data: Raw image bytes
            image_type: Type of medical image
            symptoms: Patient symptoms
            
        Returns:
            Analysis results
        """
        try:
            # Preprocess image
            image = self._preprocess_image(image_data)
            if image is None:
                return {'error': 'Failed to preprocess image'}
            
            analysis_results = {
                'analysis_type': 'Lightweight Medical AI Analysis',
                'image_type': image_type,
                'analysis_methods': [],
                'conditions': [],
                'recommendations': [],
                'confidence_scores': {},
                'model_insights': {}
            }
            
            # 1. Computer vision analysis
            cv_results = self._analyze_with_computer_vision(image, image_type)
            if cv_results:
                analysis_results['analysis_methods'].append('computer_vision')
                analysis_results['conditions'].extend(cv_results.get('conditions', []))
                analysis_results['confidence_scores']['computer_vision'] = 70
            
            # 2. Transformer model analysis (if available)
            if 'image_classification' in self.available_models:
                transformer_results = self._analyze_with_transformers(image)
                if transformer_results:
                    analysis_results['analysis_methods'].append('transformer_model')
                    analysis_results['conditions'].extend(transformer_results.get('conditions', []))
                    analysis_results['confidence_scores']['transformer_model'] = 75
            
            # 3. Symptom analysis
            if symptoms:
                symptom_results = self._analyze_symptoms_lite(symptoms, image_type)
                if symptom_results:
                    analysis_results['analysis_methods'].append('symptom_analysis')
                    analysis_results['conditions'].extend(symptom_results.get('conditions', []))
                    analysis_results['confidence_scores']['symptom_analysis'] = 65
            
            # 4. Rule-based medical analysis
            rule_results = self._analyze_with_medical_rules(image_type, symptoms)
            if rule_results:
                analysis_results['analysis_methods'].append('medical_rules')
                analysis_results['conditions'].extend(rule_results.get('conditions', []))
                analysis_results['confidence_scores']['medical_rules'] = 60
            
            # Combine and rank results
            analysis_results = self._combine_lite_results(analysis_results)
            
            return {
                'success': True,
                'analysis': analysis_results,
                'lightweight_mode': True,
                'available_models': self.available_models
            }
            
        except Exception as e:
            self.logger.error(f"Lightweight medical analysis error: {e}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'fallback_analysis': self._basic_fallback_analysis(image_type, symptoms)
            }
    
    def _preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """Preprocess image for analysis"""
        try:
            # Convert to PIL Image
            if isinstance(image_data, str):
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                image_data = base64.b64decode(image_data)
            
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Resize if too large
            max_size = 512
            if max(image_array.shape[:2]) > max_size:
                height, width = image_array.shape[:2]
                if height > width:
                    new_height = max_size
                    new_width = int(width * max_size / height)
                else:
                    new_width = max_size
                    new_height = int(height * max_size / width)
                
                image_array = cv2.resize(image_array, (new_width, new_height))
            
            return image_array
            
        except Exception as e:
            self.logger.error(f"Image preprocessing error: {e}")
            return None
    
    def _analyze_with_computer_vision(self, image: np.ndarray, image_type: str) -> Dict[str, Any]:
        """Computer vision-based analysis"""
        try:
            conditions = []
            
            # Basic color analysis
            hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            if image_type == 'skin':
                # Analyze skin conditions
                
                # Check for dark areas (potential melanoma)
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                dark_threshold = np.mean(gray) - 1.5 * np.std(gray)
                dark_percentage = (np.sum(gray < dark_threshold) / gray.size) * 100
                
                if dark_percentage > 8:
                    conditions.append({
                        'name': 'Dark lesion detected',
                        'confidence': min(85, dark_percentage * 8),
                        'source': 'computer_vision',
                        'description': 'Dark areas detected that may require evaluation'
                    })
                
                # Check for redness (inflammation)
                red_channel = image[:, :, 0]
                red_mean = np.mean(red_channel)
                if red_mean > 140:
                    conditions.append({
                        'name': 'Inflammatory condition possible',
                        'confidence': min(75, (red_mean - 140) * 2),
                        'source': 'computer_vision',
                        'description': 'Redness suggesting inflammatory condition'
                    })
                
                # Check for irregular borders
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size * 100
                if edge_density > 15:
                    conditions.append({
                        'name': 'Irregular borders detected',
                        'confidence': min(70, edge_density * 3),
                        'source': 'computer_vision',
                        'description': 'Irregular border patterns detected'
                    })
            
            elif image_type in ['chest', 'xray']:
                # Analyze chest X-rays
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                
                # Check for opacity/consolidation
                mean_intensity = np.mean(gray)
                std_intensity = np.std(gray)
                
                if std_intensity > 50:  # High variation might indicate pathology
                    conditions.append({
                        'name': 'Possible consolidation',
                        'confidence': min(70, std_intensity),
                        'source': 'computer_vision',
                        'description': 'Density variations suggesting possible pathology'
                    })
            
            return {
                'success': True,
                'conditions': conditions,
                'method': 'computer_vision'
            }
            
        except Exception as e:
            self.logger.error(f"Computer vision analysis error: {e}")
            return {}
    
    def _analyze_with_transformers(self, image: np.ndarray) -> Dict[str, Any]:
        """Analysis using transformer models"""
        try:
            if not hasattr(self, 'image_classifier'):
                return {}
            
            # Convert numpy array back to PIL for transformer
            pil_image = Image.fromarray(image)
            
            # Get predictions
            predictions = self.image_classifier(pil_image)
            
            conditions = []
            for pred in predictions[:3]:  # Top 3 predictions
                # Map generic predictions to medical conditions
                confidence = pred['score'] * 100
                label = pred['label'].lower()
                
                # Simple mapping to medical terms
                if any(term in label for term in ['dark', 'spot', 'lesion']):
                    conditions.append({
                        'name': 'Possible lesion',
                        'confidence': confidence,
                        'source': 'transformer_model',
                        'description': f'AI model detected: {pred["label"]}'
                    })
                elif confidence > 30:  # Include other high-confidence predictions
                    conditions.append({
                        'name': f'Visual finding: {pred["label"]}',
                        'confidence': confidence,
                        'source': 'transformer_model',
                        'description': f'AI classification: {pred["label"]}'
                    })
            
            return {
                'success': True,
                'conditions': conditions,
                'method': 'transformer_model'
            }
            
        except Exception as e:
            self.logger.error(f"Transformer analysis error: {e}")
            return {}
    
    def _analyze_symptoms_lite(self, symptoms: str, image_type: str) -> Dict[str, Any]:
        """Lightweight symptom analysis"""
        try:
            symptoms_lower = symptoms.lower()
            conditions = []
            
            # Get relevant medical database
            if image_type == 'skin':
                medical_db = MEDICAL_CONDITIONS_DB['skin_conditions']
            elif image_type in ['chest', 'xray']:
                medical_db = MEDICAL_CONDITIONS_DB['chest_conditions']
            else:
                medical_db = MEDICAL_CONDITIONS_DB['skin_conditions']  # Default
            
            # Analyze symptoms against known conditions
            for condition_name, condition_info in medical_db.items():
                keyword_matches = 0
                total_keywords = len(condition_info['keywords'])
                
                for keyword in condition_info['keywords']:
                    if keyword in symptoms_lower:
                        keyword_matches += 1
                
                if keyword_matches > 0:
                    confidence = min(90, (keyword_matches / total_keywords) * 100 + 30)
                    conditions.append({
                        'name': condition_name.replace('_', ' ').title(),
                        'confidence': confidence,
                        'source': 'symptom_analysis',
                        'description': condition_info['description'],
                        'urgency': condition_info['urgency'],
                        'specialist': condition_info['specialist']
                    })
            
            return {
                'success': True,
                'conditions': sorted(conditions, key=lambda x: x['confidence'], reverse=True),
                'method': 'symptom_analysis'
            }
            
        except Exception as e:
            self.logger.error(f"Symptom analysis error: {e}")
            return {}
    
    def _analyze_with_medical_rules(self, image_type: str, symptoms: str) -> Dict[str, Any]:
        """Rule-based medical analysis"""
        try:
            conditions = []
            
            # Basic rule-based analysis
            if image_type == 'skin':
                if any(word in symptoms.lower() for word in ['mole', 'spot', 'lesion']):
                    conditions.append({
                        'name': 'Skin lesion evaluation needed',
                        'confidence': 60,
                        'source': 'medical_rules',
                        'description': 'Skin lesion mentioned in symptoms'
                    })
                
                if any(word in symptoms.lower() for word in ['changing', 'growing', 'irregular']):
                    conditions.append({
                        'name': 'Concerning skin changes',
                        'confidence': 75,
                        'source': 'medical_rules',
                        'description': 'Described changes warrant medical evaluation'
                    })
            
            elif image_type in ['chest', 'xray']:
                if any(word in symptoms.lower() for word in ['cough', 'fever', 'breathing']):
                    conditions.append({
                        'name': 'Respiratory symptoms present',
                        'confidence': 70,
                        'source': 'medical_rules',
                        'description': 'Respiratory symptoms warrant chest evaluation'
                    })
            
            return {
                'success': True,
                'conditions': conditions,
                'method': 'medical_rules'
            }
            
        except Exception as e:
            self.logger.error(f"Medical rules analysis error: {e}")
            return {}
    
    def _combine_lite_results(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine lightweight analysis results"""
        try:
            # Remove duplicate conditions
            unique_conditions = {}
            for condition in analysis_results['conditions']:
                name = condition.get('name', 'Unknown').lower()
                confidence = condition.get('confidence', 0)
                
                if name not in unique_conditions or confidence > unique_conditions[name].get('confidence', 0):
                    unique_conditions[name] = condition
            
            analysis_results['conditions'] = sorted(
                list(unique_conditions.values()),
                key=lambda x: x.get('confidence', 0),
                reverse=True
            )[:5]  # Top 5 conditions
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_lite_recommendations(
                analysis_results['conditions'],
                analysis_results.get('image_type', 'unknown')
            )
            
            # Calculate overall confidence
            confidence_values = list(analysis_results['confidence_scores'].values())
            analysis_results['overall_confidence'] = sum(confidence_values) / len(confidence_values) if confidence_values else 50
            
            # Generate summary
            analysis_results['summary'] = self._generate_lite_summary(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error combining lite results: {e}")
            return analysis_results
    
    def _generate_lite_recommendations(self, conditions: List[Dict], image_type: str) -> List[str]:
        """Generate recommendations for lightweight analysis"""
        recommendations = []
        
        if conditions:
            top_condition = conditions[0]
            confidence = top_condition.get('confidence', 0)
            urgency = top_condition.get('urgency', 'MODERATE')
            
            # Urgency-based recommendations
            if urgency == 'URGENT' or confidence > 80:
                recommendations.append('🚨 Medical evaluation recommended promptly')
            elif urgency == 'MODERATE' or confidence > 60:
                recommendations.append('📅 Schedule medical consultation')
            else:
                recommendations.append('📋 Consider medical evaluation')
            
            # Specialist recommendation
            specialist = top_condition.get('specialist', 'Healthcare Provider')
            recommendations.append(f'👨‍⚕️ Consult {specialist}')
            
            # Condition-specific
            if confidence > 70:
                recommendations.append(f'🎯 Analysis suggests: {top_condition.get("name", "Unknown")}')
        
        # General recommendations
        recommendations.extend([
            '📸 Document any changes',
            '📝 Note symptoms and timeline',
            '⚠️ Monitor for worsening'
        ])
        
        return recommendations[:6]
    
    def _generate_lite_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate summary for lightweight analysis"""
        try:
            image_type = analysis.get('image_type', 'unknown')
            methods = analysis.get('analysis_methods', [])
            conditions = analysis.get('conditions', [])
            confidence = analysis.get('overall_confidence', 50)
            
            summary_parts = []
            
            # Analysis overview
            summary_parts.append(f"Lightweight AI analysis of {image_type} image using {len(methods)} methods.")
            
            # Key findings
            if conditions:
                top_condition = conditions[0]
                summary_parts.append(f"Primary finding: {top_condition.get('name', 'Unknown')} "
                                   f"(confidence: {top_condition.get('confidence', 0):.0f}%).")
            else:
                summary_parts.append("No specific conditions identified.")
            
            # Confidence note
            if confidence > 70:
                summary_parts.append("Good confidence in lightweight analysis results.")
            else:
                summary_parts.append("Professional medical evaluation recommended for confirmation.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            return "Lightweight medical AI analysis completed. Professional evaluation recommended."
    
    def _basic_fallback_analysis(self, image_type: str, symptoms: str) -> Dict[str, Any]:
        """Basic fallback when all analysis methods fail"""
        return {
            'analysis_type': 'Basic Fallback Analysis',
            'image_type': image_type,
            'conditions': [],
            'recommendations': [
                'Technical analysis unavailable',
                'Consult healthcare provider',
                'Professional evaluation recommended'
            ],
            'summary': 'Basic analysis mode - professional medical evaluation recommended.'
        }

# Global lightweight analyzer instance
lightweight_medical_ai = LightweightMedicalAI()

def analyze_with_lightweight_medical_ai(image_data: bytes, image_type: str = 'skin', 
                                      symptoms: str = '') -> Dict[str, Any]:
    """
    Convenience function for lightweight medical AI analysis
    
    Args:
        image_data: Raw image bytes
        image_type: Type of medical image
        symptoms: Patient symptoms
        
    Returns:
        Lightweight analysis results
    """
    return lightweight_medical_ai.analyze_medical_image_lite(image_data, image_type, symptoms)

if __name__ == "__main__":
    print("🏥 Testing Lightweight Medical AI...")
    
    # Test initialization
    available_models = lightweight_medical_ai.available_models
    print(f"Available models: {available_models}")
    
    # Test symptom analysis
    test_symptoms = "I have a dark mole that has been changing shape"
    result = lightweight_medical_ai._analyze_symptoms_lite(test_symptoms, 'skin')
    print(f"Symptom analysis found {len(result.get('conditions', []))} conditions")

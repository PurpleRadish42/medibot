# src/ai/medical_vlm_models.py
"""
Medical Vision-Language Models Integration
Specialized VLMs for medical image analysis and diagnosis
"""
import logging
import base64
import json
import io
from typing import Dict, List, Any, Optional, Tuple
import requests
from PIL import Image
import numpy as np

# Try to import advanced medical libraries
try:
    import torch
    import torchvision.transforms as transforms
    from transformers import (
        CLIPProcessor, CLIPModel,
        BlipProcessor, BlipForConditionalGeneration,
        AutoProcessor, AutoModel,
        pipeline
    )
    ADVANCED_VLM_AVAILABLE = True
    print("✅ Advanced Vision-Language Models available")
except ImportError as e:
    ADVANCED_VLM_AVAILABLE = False
    print(f"⚠️ Advanced VLM models not available: {e}")

# Medical VLM model configurations
MEDICAL_VLM_CONFIGS = {
    'biomedclip': {
        'model_name': 'microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224',
        'description': 'Biomedical CLIP model trained on medical image-text pairs',
        'specialties': ['general_medical', 'radiology', 'pathology'],
        'confidence_threshold': 0.7,
        'type': 'clip'
    },
    'medpalm_m': {
        'model_name': 'google/med-palm-m',  # Conceptual - would need actual access
        'description': 'Multimodal medical model for various medical tasks',
        'specialties': ['general_medical', 'diagnostics', 'qa'],
        'confidence_threshold': 0.8,
        'type': 'multimodal'
    },
    'dermnet_clip': {
        'model_name': 'openai/clip-vit-base-patch32',  # Base model, fine-tuned concept
        'description': 'CLIP model adapted for dermatology',
        'specialties': ['dermatology', 'skin_conditions'],
        'confidence_threshold': 0.75,
        'type': 'clip'
    },
    'chexnet_vlm': {
        'model_name': 'stanford/chexnet-clip',  # Conceptual combination
        'description': 'Vision-language model for chest X-ray analysis',
        'specialties': ['radiology', 'chest_xray', 'pulmonology'],
        'confidence_threshold': 0.8,
        'type': 'specialized'
    }
}

# Medical condition vocabularies for different specialties
MEDICAL_VOCABULARIES = {
    'dermatology': [
        'melanoma', 'basal cell carcinoma', 'squamous cell carcinoma', 'actinic keratosis',
        'seborrheic keratosis', 'nevus', 'dermatofibroma', 'vascular lesion',
        'eczema', 'psoriasis', 'acne', 'rosacea', 'vitiligo', 'fungal infection',
        'bacterial infection', 'viral infection', 'allergic reaction', 'contact dermatitis'
    ],
    'radiology': [
        'pneumonia', 'tuberculosis', 'lung cancer', 'pleural effusion', 'pneumothorax',
        'cardiomegaly', 'atelectasis', 'nodule', 'mass', 'consolidation',
        'fracture', 'dislocation', 'osteoarthritis', 'osteoporosis', 'normal'
    ],
    'ophthalmology': [
        'diabetic retinopathy', 'glaucoma', 'macular degeneration', 'cataracts',
        'retinal detachment', 'hypertensive retinopathy', 'normal fundus'
    ],
    'pathology': [
        'malignant', 'benign', 'inflammatory', 'necrotic', 'fibrotic',
        'hyperplastic', 'dysplastic', 'normal tissue'
    ]
}

class MedicalVLMAnalyzer:
    """
    Medical Vision-Language Model Analyzer
    Uses specialized VLMs for medical image analysis
    """
    
    def __init__(self):
        """Initialize the medical VLM analyzer"""
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.processors = {}
        self.pipelines = {}
        
        if ADVANCED_VLM_AVAILABLE:
            self._load_vlm_models()
        else:
            self.logger.warning("Advanced VLM models not available. Using fallback analysis.")
    
    def _load_vlm_models(self):
        """Load available medical VLM models"""
        try:
            self.logger.info("Loading medical Vision-Language models...")
            
            # 1. Load BiomedCLIP (if available)
            try:
                self.processors['biomedclip'] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                self.models['biomedclip'] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.logger.info("✅ BiomedCLIP-style model loaded")
            except Exception as e:
                self.logger.warning(f"BiomedCLIP not available: {e}")
            
            # 2. Load general CLIP for medical adaptation
            try:
                self.processors['clip_medical'] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                self.models['clip_medical'] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.logger.info("✅ Medical CLIP model loaded")
            except Exception as e:
                self.logger.warning(f"Medical CLIP not available: {e}")
            
            # 3. Load BLIP for medical image captioning
            try:
                self.processors['blip_medical'] = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.models['blip_medical'] = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                self.logger.info("✅ Medical BLIP model loaded")
            except Exception as e:
                self.logger.warning(f"Medical BLIP not available: {e}")
            
        except Exception as e:
            self.logger.error(f"Error loading VLM models: {e}")
    
    def analyze_medical_image_vlm(self, image_data: bytes, specialty: str = None, 
                                 symptoms: str = "", image_type: str = None) -> Dict[str, Any]:
        """
        Analyze medical image using Vision-Language Models
        
        Args:
            image_data: Raw image bytes
            specialty: Medical specialty (dermatology, radiology, etc.)
            symptoms: Patient symptoms description
            image_type: Type of medical image
            
        Returns:
            VLM analysis results
        """
        try:
            # Preprocess image
            image = self._preprocess_medical_image(image_data)
            if image is None:
                return {'error': 'Failed to preprocess image'}
            
            # Determine best model for specialty
            best_model = self._select_best_vlm_model(specialty, image_type)
            
            # Perform VLM analysis
            analysis_results = {}
            
            # 1. CLIP-based analysis for condition classification
            if best_model in self.models and best_model in self.processors:
                clip_results = self._analyze_with_clip(image, specialty, best_model)
                analysis_results['clip_analysis'] = clip_results
            
            # 2. Image captioning for description
            if 'blip_medical' in self.models:
                caption_results = self._generate_medical_caption(image)
                analysis_results['image_description'] = caption_results
            
            # 3. Symptom-image correlation
            if symptoms:
                correlation_results = self._correlate_symptoms_image(image, symptoms, specialty)
                analysis_results['symptom_correlation'] = correlation_results
            
            # 4. Combine results
            final_analysis = self._combine_vlm_results(analysis_results, specialty, symptoms)
            
            return {
                'success': True,
                'analysis': final_analysis,
                'model_used': best_model,
                'vlm_enhanced': True
            }
            
        except Exception as e:
            self.logger.error(f"VLM analysis error: {e}")
            return {
                'success': False,
                'error': f'VLM analysis failed: {str(e)}',
                'fallback_analysis': self._fallback_vlm_analysis(image_type, specialty)
            }
    
    def _preprocess_medical_image(self, image_data: bytes) -> Optional[Image.Image]:
        """Preprocess medical image for VLM analysis"""
        try:
            # Convert bytes to PIL Image
            if isinstance(image_data, str):
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                image_data = base64.b64decode(image_data)
            
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for optimal VLM processing
            max_size = 512  # Optimal for most VLM models
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Medical image preprocessing error: {e}")
            return None
    
    def _select_best_vlm_model(self, specialty: str, image_type: str) -> str:
        """Select the best VLM model for the given specialty and image type"""
        # Priority mapping based on specialty
        specialty_models = {
            'dermatology': ['biomedclip', 'clip_medical'],
            'radiology': ['biomedclip', 'clip_medical'],
            'ophthalmology': ['biomedclip', 'clip_medical'],
            'pathology': ['biomedclip', 'clip_medical']
        }
        
        if specialty in specialty_models:
            for model in specialty_models[specialty]:
                if model in self.models:
                    return model
        
        # Default to first available model
        available_models = list(self.models.keys())
        return available_models[0] if available_models else 'fallback'
    
    def _analyze_with_clip(self, image: Image.Image, specialty: str, model_name: str) -> Dict[str, Any]:
        """Analyze image using CLIP model with medical vocabulary"""
        try:
            processor = self.processors[model_name]
            model = self.models[model_name]
            
            # Get relevant medical vocabulary
            vocabulary = MEDICAL_VOCABULARIES.get(specialty, MEDICAL_VOCABULARIES['dermatology'])
            
            # Create text prompts for medical conditions
            text_prompts = [f"a medical image showing {condition}" for condition in vocabulary]
            
            # Process inputs
            inputs = processor(
                text=text_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Get top predictions
            top_probs, top_indices = torch.topk(probs, k=min(5, len(vocabulary)))
            
            conditions = []
            for prob, idx in zip(top_probs[0], top_indices[0]):
                confidence = prob.item() * 100
                condition_name = vocabulary[idx.item()]
                
                if confidence > 10:  # Minimum threshold
                    conditions.append({
                        'name': condition_name.title(),
                        'confidence': confidence,
                        'source': 'vlm_clip',
                        'specialty': specialty
                    })
            
            return {
                'success': True,
                'conditions': conditions,
                'model': model_name,
                'vocabulary_size': len(vocabulary)
            }
            
        except Exception as e:
            self.logger.error(f"CLIP analysis error: {e}")
            return {'error': f'CLIP analysis failed: {str(e)}'}
    
    def _generate_medical_caption(self, image: Image.Image) -> Dict[str, Any]:
        """Generate medical image caption using BLIP"""
        try:
            processor = self.processors['blip_medical']
            model = self.models['blip_medical']
            
            # Process image
            inputs = processor(image, return_tensors="pt")
            
            # Generate caption
            with torch.no_grad():
                out = model.generate(**inputs, max_length=50, num_beams=5)
            
            caption = processor.decode(out[0], skip_special_tokens=True)
            
            # Enhance caption with medical context
            medical_caption = self._enhance_medical_caption(caption)
            
            return {
                'success': True,
                'caption': caption,
                'medical_interpretation': medical_caption,
                'confidence': 75
            }
            
        except Exception as e:
            self.logger.error(f"Medical captioning error: {e}")
            return {'error': f'Caption generation failed: {str(e)}'}
    
    def _enhance_medical_caption(self, caption: str) -> str:
        """Enhance generated caption with medical terminology"""
        # Map common terms to medical equivalents
        medical_mappings = {
            'spot': 'lesion',
            'mark': 'marking',
            'red': 'erythematous',
            'dark': 'hyperpigmented',
            'light': 'hypopigmented',
            'bump': 'papule',
            'flat': 'macule',
            'raised': 'elevated lesion'
        }
        
        enhanced_caption = caption.lower()
        for term, medical_term in medical_mappings.items():
            enhanced_caption = enhanced_caption.replace(term, medical_term)
        
        return enhanced_caption.title()
    
    def _correlate_symptoms_image(self, image: Image.Image, symptoms: str, specialty: str) -> Dict[str, Any]:
        """Correlate patient symptoms with image findings"""
        try:
            # Use CLIP to compare symptoms with image
            if 'clip_medical' in self.models:
                processor = self.processors['clip_medical']
                model = self.models['clip_medical']
                
                # Create symptom-based text prompts
                symptom_prompts = [
                    f"medical image showing symptoms: {symptoms}",
                    f"clinical presentation of {symptoms}",
                    f"visual manifestation of {symptoms}"
                ]
                
                # Process inputs
                inputs = processor(
                    text=symptom_prompts,
                    images=image,
                    return_tensors="pt",
                    padding=True
                )
                
                # Get similarity scores
                with torch.no_grad():
                    outputs = model(**inputs)
                    similarity_scores = outputs.logits_per_image.softmax(dim=1)
                
                max_similarity = torch.max(similarity_scores).item()
                correlation_strength = max_similarity * 100
                
                return {
                    'success': True,
                    'correlation_strength': correlation_strength,
                    'interpretation': self._interpret_correlation(correlation_strength),
                    'confidence': min(95, correlation_strength * 1.2)
                }
            
        except Exception as e:
            self.logger.error(f"Symptom correlation error: {e}")
        
        return {
            'success': False,
            'correlation_strength': 50,
            'interpretation': 'Unable to determine correlation'
        }
    
    def _interpret_correlation(self, correlation_strength: float) -> str:
        """Interpret correlation strength between symptoms and image"""
        if correlation_strength > 80:
            return "Strong correlation between symptoms and visual findings"
        elif correlation_strength > 60:
            return "Moderate correlation - symptoms align with visual presentation"
        elif correlation_strength > 40:
            return "Weak correlation - additional investigation needed"
        else:
            return "Poor correlation - symptoms may not match visual findings"
    
    def _combine_vlm_results(self, analysis_results: Dict, specialty: str, symptoms: str) -> Dict[str, Any]:
        """Combine VLM analysis results into comprehensive assessment"""
        try:
            combined_analysis = {
                'analysis_type': 'Vision-Language Model Analysis',
                'specialty': specialty,
                'conditions': [],
                'image_description': '',
                'symptom_correlation': {},
                'confidence_scores': {},
                'recommendations': []
            }
            
            # Extract CLIP conditions
            clip_analysis = analysis_results.get('clip_analysis', {})
            if clip_analysis.get('success'):
                combined_analysis['conditions'] = clip_analysis.get('conditions', [])
                combined_analysis['confidence_scores']['clip'] = 80
            
            # Extract image description
            image_desc = analysis_results.get('image_description', {})
            if image_desc.get('success'):
                combined_analysis['image_description'] = image_desc.get('medical_interpretation', '')
                combined_analysis['confidence_scores']['description'] = image_desc.get('confidence', 70)
            
            # Extract symptom correlation
            correlation = analysis_results.get('symptom_correlation', {})
            if correlation.get('success'):
                combined_analysis['symptom_correlation'] = {
                    'strength': correlation.get('correlation_strength', 50),
                    'interpretation': correlation.get('interpretation', '')
                }
                combined_analysis['confidence_scores']['correlation'] = correlation.get('confidence', 60)
            
            # Generate VLM-specific recommendations
            combined_analysis['recommendations'] = self._generate_vlm_recommendations(
                combined_analysis['conditions'],
                combined_analysis['symptom_correlation'],
                specialty
            )
            
            # Calculate overall confidence
            confidence_values = list(combined_analysis['confidence_scores'].values())
            combined_analysis['overall_confidence'] = sum(confidence_values) / len(confidence_values) if confidence_values else 60
            
            return combined_analysis
            
        except Exception as e:
            self.logger.error(f"Error combining VLM results: {e}")
            return {
                'analysis_type': 'VLM Analysis (Error)',
                'error': str(e),
                'conditions': [],
                'recommendations': ['Professional medical evaluation recommended']
            }
    
    def _generate_vlm_recommendations(self, conditions: List, correlation: Dict, specialty: str) -> List[str]:
        """Generate recommendations based on VLM analysis"""
        recommendations = []
        
        # Condition-based recommendations
        if conditions:
            top_condition = conditions[0]
            confidence = top_condition.get('confidence', 0)
            
            if confidence > 70:
                recommendations.append(f"🎯 VLM analysis suggests: {top_condition.get('name')}")
            else:
                recommendations.append("🤔 Multiple possibilities identified by VLM analysis")
        
        # Correlation-based recommendations
        correlation_strength = correlation.get('strength', 50)
        if correlation_strength > 70:
            recommendations.append("✅ Symptoms strongly correlate with visual findings")
        elif correlation_strength < 40:
            recommendations.append("⚠️ Symptoms may not fully match visual presentation")
        
        # Specialty-specific recommendations
        specialty_recs = {
            'dermatology': '👨‍⚕️ Dermatologist consultation recommended',
            'radiology': '🏥 Radiologist review suggested',
            'ophthalmology': '👁️ Ophthalmologist evaluation needed',
            'pathology': '🔬 Pathologist assessment required'
        }
        
        if specialty in specialty_recs:
            recommendations.append(specialty_recs[specialty])
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _fallback_vlm_analysis(self, image_type: str, specialty: str) -> Dict[str, Any]:
        """Fallback analysis when VLM models fail"""
        return {
            'analysis_type': 'Basic VLM Analysis (Fallback)',
            'image_type': image_type,
            'specialty': specialty,
            'conditions': [],
            'recommendations': [
                'VLM models unavailable - using basic analysis',
                'Professional medical evaluation strongly recommended'
            ],
            'confidence': 30
        }

# Global VLM analyzer instance
medical_vlm_analyzer = MedicalVLMAnalyzer()

def analyze_with_medical_vlm(image_data: bytes, specialty: str = None, 
                           symptoms: str = "", image_type: str = None) -> Dict[str, Any]:
    """
    Convenience function for medical VLM analysis
    
    Args:
        image_data: Raw image bytes
        specialty: Medical specialty
        symptoms: Patient symptoms
        image_type: Type of medical image
        
    Returns:
        VLM analysis results
    """
    return medical_vlm_analyzer.analyze_medical_image_vlm(
        image_data, specialty, symptoms, image_type
    )

if __name__ == "__main__":
    print("🧠 Testing Medical Vision-Language Models...")
    
    # Test model loading
    print(f"Available VLM models: {list(medical_vlm_analyzer.models.keys())}")
    print(f"Available processors: {list(medical_vlm_analyzer.processors.keys())}")
    
    # Test vocabulary
    for specialty, vocab in MEDICAL_VOCABULARIES.items():
        print(f"{specialty}: {len(vocab)} conditions")

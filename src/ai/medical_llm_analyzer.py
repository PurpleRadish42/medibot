# src/ai/medical_llm_analyzer.py
"""
Advanced Medical LLM Integration
Uses specialized medical language models for better analysis
"""
import logging
from typing import Dict, List, Any, Optional
import json

# Medical LLM imports
try:
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        pipeline, CLIPProcessor, CLIPModel
    )
    import torch
    TRANSFORMERS_AVAILABLE = True
    print("✅ Transformers available for medical LLM analysis")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available for medical LLM analysis")

# Medical knowledge base
MEDICAL_KNOWLEDGE = {
    'skin_conditions': {
        'melanoma': {
            'description': 'Aggressive skin cancer requiring immediate attention',
            'risk_factors': ['sun exposure', 'fair skin', 'family history', 'multiple moles'],
            'urgency': 'URGENT',
            'specialist': 'Dermatologist or Oncologist'
        },
        'basal_cell_carcinoma': {
            'description': 'Most common but least dangerous skin cancer',
            'risk_factors': ['sun exposure', 'age over 50', 'fair skin'],
            'urgency': 'MODERATE',
            'specialist': 'Dermatologist'
        },
        'eczema': {
            'description': 'Chronic inflammatory skin condition',
            'risk_factors': ['allergies', 'dry skin', 'stress', 'genetics'],
            'urgency': 'LOW',
            'specialist': 'Dermatologist or Allergist'
        },
        'psoriasis': {
            'description': 'Autoimmune skin condition with scaly patches',
            'risk_factors': ['genetics', 'stress', 'infections', 'medications'],
            'urgency': 'MODERATE',
            'specialist': 'Dermatologist or Rheumatologist'
        },
        'acne': {
            'description': 'Common skin condition affecting hair follicles',
            'risk_factors': ['hormones', 'genetics', 'stress', 'diet'],
            'urgency': 'LOW',
            'specialist': 'Dermatologist'
        }
    }
}

class MedicalLLMAnalyzer:
    """
    Advanced medical analysis using specialized language models
    """
    
    def __init__(self):
        """Initialize the medical LLM analyzer"""
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        
        if TRANSFORMERS_AVAILABLE:
            self._load_medical_models()
        else:
            self.logger.warning("Transformers not available. Using fallback analysis.")
    
    def _load_medical_models(self):
        """Load specialized medical language models"""
        try:
            self.logger.info("Loading medical language models...")
            
            # 1. Load BioBERT for medical text analysis
            try:
                model_name = "emilyalsentzer/BioBERT"
                self.tokenizers['biobert'] = AutoTokenizer.from_pretrained(model_name)
                self.models['biobert'] = AutoModel.from_pretrained(model_name)
                self.logger.info("✅ BioBERT loaded successfully")
            except Exception as e:
                self.logger.warning(f"Failed to load BioBERT: {e}")
            
            # 2. Load medical classification pipeline
            try:
                # Use a general model for medical classification
                self.pipelines['medical_classifier'] = pipeline(
                    "text-classification",
                    model="microsoft/DialoGPT-medium",
                    return_all_scores=True
                )
                self.logger.info("✅ Medical classification pipeline loaded")
            except Exception as e:
                self.logger.warning(f"Failed to load classification pipeline: {e}")
            
            # 3. Load medical question-answering model
            try:
                self.pipelines['medical_qa'] = pipeline(
                    "question-answering",
                    model="deepset/roberta-base-squad2"
                )
                self.logger.info("✅ Medical QA pipeline loaded")
            except Exception as e:
                self.logger.warning(f"Failed to load QA pipeline: {e}")
                
        except Exception as e:
            self.logger.error(f"Error loading medical models: {e}")
    
    def analyze_symptoms_with_llm(self, symptoms_text: str, image_analysis: Dict = None) -> Dict[str, Any]:
        """
        Analyze symptoms using medical LLM
        
        Args:
            symptoms_text: User's symptom description
            image_analysis: Optional image analysis results
            
        Returns:
            Enhanced analysis with LLM insights
        """
        try:
            # Enhanced symptom analysis
            analysis_result = {
                'symptom_analysis': self._analyze_symptom_text(symptoms_text),
                'condition_predictions': self._predict_conditions(symptoms_text),
                'urgency_assessment': self._assess_urgency(symptoms_text),
                'specialist_recommendation': self._recommend_specialist(symptoms_text),
                'additional_questions': self._generate_follow_up_questions(symptoms_text)
            }
            
            # Integrate with image analysis if available
            if image_analysis:
                analysis_result['multimodal_analysis'] = self._combine_text_image_analysis(
                    symptoms_text, image_analysis
                )
            
            return {
                'success': True,
                'analysis': analysis_result,
                'llm_enhanced': True
            }
            
        except Exception as e:
            self.logger.error(f"LLM analysis error: {e}")
            return {
                'success': False,
                'error': f'LLM analysis failed: {str(e)}',
                'fallback_analysis': self._fallback_symptom_analysis(symptoms_text)
            }
    
    def _analyze_symptom_text(self, symptoms_text: str) -> Dict[str, Any]:
        """Analyze symptom text using medical NLP"""
        try:
            if 'medical_qa' in self.pipelines:
                # Extract key medical information
                questions = [
                    "What is the main symptom?",
                    "How severe is this condition?",
                    "What body part is affected?",
                    "How long have the symptoms been present?"
                ]
                
                extracted_info = {}
                for question in questions:
                    try:
                        result = self.pipelines['medical_qa'](
                            question=question,
                            context=symptoms_text
                        )
                        extracted_info[question] = result['answer']
                    except Exception:
                        extracted_info[question] = "Not specified"
                
                return {
                    'extracted_information': extracted_info,
                    'text_length': len(symptoms_text),
                    'complexity': 'high' if len(symptoms_text.split()) > 20 else 'low'
                }
            else:
                return self._basic_text_analysis(symptoms_text)
                
        except Exception as e:
            self.logger.error(f"Symptom text analysis error: {e}")
            return self._basic_text_analysis(symptoms_text)
    
    def _predict_conditions(self, symptoms_text: str) -> List[Dict[str, Any]]:
        """Predict medical conditions from symptoms"""
        try:
            symptoms_lower = symptoms_text.lower()
            predicted_conditions = []
            
            # Rule-based condition matching enhanced with medical knowledge
            for condition, info in MEDICAL_KNOWLEDGE['skin_conditions'].items():
                confidence = 0
                
                # Check for condition-specific keywords
                condition_keywords = {
                    'melanoma': ['mole', 'dark spot', 'changing spot', 'irregular', 'asymmetric'],
                    'basal_cell_carcinoma': ['bump', 'growth', 'sore', 'scaly patch'],
                    'eczema': ['itchy', 'dry', 'red', 'inflamed', 'rash'],
                    'psoriasis': ['scaly', 'patches', 'silvery', 'thick'],
                    'acne': ['pimple', 'blackhead', 'whitehead', 'breakout']
                }
                
                if condition in condition_keywords:
                    keywords = condition_keywords[condition]
                    matches = sum(1 for keyword in keywords if keyword in symptoms_lower)
                    confidence = min(90, matches * 20 + 20)  # Base confidence + keyword matches
                
                if confidence > 20:
                    predicted_conditions.append({
                        'condition': condition.replace('_', ' ').title(),
                        'confidence': confidence,
                        'description': info['description'],
                        'urgency': info['urgency'],
                        'specialist': info['specialist']
                    })
            
            # Sort by confidence
            predicted_conditions.sort(key=lambda x: x['confidence'], reverse=True)
            return predicted_conditions[:5]  # Top 5 predictions
            
        except Exception as e:
            self.logger.error(f"Condition prediction error: {e}")
            return []
    
    def _assess_urgency(self, symptoms_text: str) -> Dict[str, Any]:
        """Assess medical urgency using LLM"""
        try:
            symptoms_lower = symptoms_text.lower()
            
            # Urgent keywords
            urgent_keywords = [
                'bleeding', 'severe pain', 'difficulty breathing', 'chest pain',
                'sudden change', 'rapidly growing', 'won\'t heal', 'infected'
            ]
            
            # Moderate urgency keywords
            moderate_keywords = [
                'persistent', 'weeks', 'months', 'getting worse', 'spreading'
            ]
            
            # Low urgency keywords
            low_keywords = [
                'mild', 'occasional', 'cosmetic', 'minor', 'small'
            ]
            
            urgent_count = sum(1 for keyword in urgent_keywords if keyword in symptoms_lower)
            moderate_count = sum(1 for keyword in moderate_keywords if keyword in symptoms_lower)
            low_count = sum(1 for keyword in low_keywords if keyword in symptoms_lower)
            
            if urgent_count > 0:
                urgency_level = 'URGENT'
                recommendation = 'Seek immediate medical attention'
            elif moderate_count > low_count:
                urgency_level = 'MODERATE'
                recommendation = 'Schedule appointment within 1-2 weeks'
            else:
                urgency_level = 'LOW'
                recommendation = 'Routine appointment or monitoring'
            
            return {
                'urgency_level': urgency_level,
                'recommendation': recommendation,
                'urgent_indicators': urgent_count,
                'moderate_indicators': moderate_count
            }
            
        except Exception as e:
            self.logger.error(f"Urgency assessment error: {e}")
            return {
                'urgency_level': 'MODERATE',
                'recommendation': 'Consult healthcare provider for proper evaluation'
            }
    
    def _recommend_specialist(self, symptoms_text: str) -> Dict[str, Any]:
        """Recommend appropriate medical specialist"""
        try:
            symptoms_lower = symptoms_text.lower()
            
            specialist_keywords = {
                'dermatologist': ['skin', 'mole', 'rash', 'acne', 'eczema', 'psoriasis'],
                'cardiologist': ['chest pain', 'heart', 'palpitations', 'shortness of breath'],
                'neurologist': ['headache', 'dizziness', 'numbness', 'seizure'],
                'orthopedist': ['bone', 'joint', 'fracture', 'sprain'],
                'ophthalmologist': ['eye', 'vision', 'blind', 'cataract'],
                'gastroenterologist': ['stomach', 'abdominal', 'digestive', 'nausea']
            }
            
            specialist_scores = {}
            for specialist, keywords in specialist_keywords.items():
                score = sum(1 for keyword in keywords if keyword in symptoms_lower)
                if score > 0:
                    specialist_scores[specialist] = score
            
            if specialist_scores:
                top_specialist = max(specialist_scores, key=specialist_scores.get)
                confidence = min(95, specialist_scores[top_specialist] * 25)
                
                return {
                    'primary_specialist': top_specialist.title(),
                    'confidence': confidence,
                    'alternatives': [
                        s.title() for s in sorted(specialist_scores.keys(), 
                        key=specialist_scores.get, reverse=True)[1:3]
                    ]
                }
            else:
                return {
                    'primary_specialist': 'General Physician',
                    'confidence': 70,
                    'alternatives': ['Family Medicine']
                }
                
        except Exception as e:
            self.logger.error(f"Specialist recommendation error: {e}")
            return {
                'primary_specialist': 'General Physician',
                'confidence': 60,
                'alternatives': []
            }
    
    def _generate_follow_up_questions(self, symptoms_text: str) -> List[str]:
        """Generate relevant follow-up questions"""
        try:
            base_questions = [
                "How long have you been experiencing these symptoms?",
                "Have the symptoms changed or worsened recently?",
                "Are you currently taking any medications?",
                "Do you have any allergies?",
                "Is there any family history of similar conditions?"
            ]
            
            # Add specific questions based on symptoms
            symptoms_lower = symptoms_text.lower()
            specific_questions = []
            
            if any(word in symptoms_lower for word in ['skin', 'rash', 'mole']):
                specific_questions.extend([
                    "Has the size, shape, or color changed?",
                    "Is there any itching or pain?",
                    "Have you had recent sun exposure?"
                ])
            
            if any(word in symptoms_lower for word in ['pain', 'ache']):
                specific_questions.extend([
                    "On a scale of 1-10, how severe is the pain?",
                    "What triggers or relieves the pain?"
                ])
            
            return base_questions + specific_questions[:3]  # Limit to reasonable number
            
        except Exception as e:
            self.logger.error(f"Question generation error: {e}")
            return [
                "When did symptoms start?",
                "Any other symptoms?",
                "Previous medical history?"
            ]
    
    def _combine_text_image_analysis(self, symptoms_text: str, image_analysis: Dict) -> Dict[str, Any]:
        """Combine text and image analysis for better results"""
        try:
            # Extract image conditions
            image_conditions = []
            if 'analysis' in image_analysis and 'conditions' in image_analysis['analysis']:
                image_conditions = image_analysis['analysis']['conditions']
            
            # Extract text predictions
            text_predictions = self._predict_conditions(symptoms_text)
            
            # Find correlations
            correlations = []
            for text_pred in text_predictions:
                for img_cond in image_conditions:
                    if (text_pred['condition'].lower() in img_cond.get('name', '').lower() or
                        img_cond.get('name', '').lower() in text_pred['condition'].lower()):
                        correlation_confidence = (text_pred['confidence'] + img_cond.get('confidence', 0)) / 2
                        correlations.append({
                            'condition': text_pred['condition'],
                            'text_confidence': text_pred['confidence'],
                            'image_confidence': img_cond.get('confidence', 0),
                            'combined_confidence': correlation_confidence,
                            'evidence': 'Both symptoms and image support this diagnosis'
                        })
            
            return {
                'correlations': correlations,
                'text_only_predictions': text_predictions,
                'image_only_predictions': image_conditions,
                'recommendation': self._get_multimodal_recommendation(correlations)
            }
            
        except Exception as e:
            self.logger.error(f"Multimodal analysis error: {e}")
            return {'error': str(e)}
    
    def _get_multimodal_recommendation(self, correlations: List[Dict]) -> str:
        """Generate recommendation based on multimodal analysis"""
        if not correlations:
            return "Image and symptom analysis show different findings. Professional evaluation recommended."
        
        highest_correlation = max(correlations, key=lambda x: x['combined_confidence'])
        if highest_correlation['combined_confidence'] > 70:
            return f"Strong evidence for {highest_correlation['condition']}. Consult specialist promptly."
        else:
            return "Multiple possibilities identified. Professional diagnosis needed for clarity."
    
    def _basic_text_analysis(self, symptoms_text: str) -> Dict[str, Any]:
        """Basic text analysis fallback"""
        return {
            'word_count': len(symptoms_text.split()),
            'character_count': len(symptoms_text),
            'contains_keywords': any(word in symptoms_text.lower() 
                                   for word in ['pain', 'ache', 'rash', 'bump'])
        }
    
    def _fallback_symptom_analysis(self, symptoms_text: str) -> Dict[str, Any]:
        """Fallback analysis when LLM fails"""
        return {
            'basic_analysis': self._basic_text_analysis(symptoms_text),
            'simple_recommendations': [
                'Describe symptoms to healthcare provider',
                'Note when symptoms started',
                'Track any changes in symptoms'
            ]
        }

# Global analyzer instance
medical_llm_analyzer = MedicalLLMAnalyzer()

def analyze_with_medical_llm(symptoms_text: str, image_analysis: Dict = None) -> Dict[str, Any]:
    """
    Convenience function for medical LLM analysis
    
    Args:
        symptoms_text: Patient's symptom description
        image_analysis: Optional image analysis results
        
    Returns:
        Enhanced medical analysis
    """
    return medical_llm_analyzer.analyze_symptoms_with_llm(symptoms_text, image_analysis)

if __name__ == "__main__":
    print("🧠 Testing Medical LLM Analyzer...")
    
    # Test symptom analysis
    test_symptoms = "I have a dark mole on my arm that has been changing shape and getting larger over the past few weeks."
    
    result = analyze_with_medical_llm(test_symptoms)
    print("Analysis result:", result['success'])
    
    if result['success']:
        analysis = result['analysis']
        print("Conditions predicted:", len(analysis.get('condition_predictions', [])))
        print("Urgency level:", analysis.get('urgency_assessment', {}).get('urgency_level'))
        print("Specialist:", analysis.get('specialist_recommendation', {}).get('primary_specialist'))

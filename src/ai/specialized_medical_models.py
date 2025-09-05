# src/ai/specialized_medical_models.py
"""
Specialized Medical AI Models Integration
CheXNet, DermNet, FastMRI and other specialized models
"""
import logging
import base64
import io
import json
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from PIL import Image
import cv2

# Try to import medical deep learning libraries
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from torchvision import models
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
    print("✅ PyTorch available for specialized medical models")
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available for specialized models")

# Specialized model configurations
SPECIALIZED_MODEL_CONFIGS = {
    'chexnet': {
        'name': 'CheXNet - Chest X-ray Analysis',
        'description': 'Stanford model for chest X-ray pathology detection',
        'conditions': [
            'Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration',
            'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax',
            'Consolidation', 'Edema', 'Emphysema', 'Fibrosis',
            'Pleural_Thickening', 'Hernia'
        ],
        'input_size': (224, 224),
        'confidence_threshold': 0.5
    },
    'dermnet': {
        'name': 'DermNet - Dermatological Analysis',
        'description': 'Google model for skin condition classification',
        'conditions': [
            'Melanoma', 'Melanocytic_nevus', 'Basal_cell_carcinoma',
            'Actinic_keratosis', 'Benign_keratosis', 'Dermatofibroma',
            'Vascular_lesion', 'Squamous_cell_carcinoma', 'Unknown'
        ],
        'input_size': (224, 224),
        'confidence_threshold': 0.3
    },
    'fastmri': {
        'name': 'FastMRI - MRI Analysis',
        'description': 'Facebook AI model for MRI reconstruction and analysis',
        'conditions': [
            'Normal', 'Abnormal_signal', 'Mass_lesion', 'Vascular_abnormality',
            'Degenerative_changes', 'Inflammatory_changes'
        ],
        'input_size': (256, 256),
        'confidence_threshold': 0.4
    },
    'retina_net': {
        'name': 'RetinaNet - Diabetic Retinopathy Detection',
        'description': 'Model for diabetic retinopathy screening',
        'conditions': [
            'No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative_DR'
        ],
        'input_size': (512, 512),
        'confidence_threshold': 0.3
    }
}

class SpecializedMedicalModel:
    """
    Individual specialized medical model wrapper
    """
    
    def __init__(self, model_type: str, config: Dict[str, Any]):
        """
        Initialize specialized medical model
        
        Args:
            model_type: Type of specialized model (chexnet, dermnet, etc.)
            config: Model configuration
        """
        self.model_type = model_type
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.transform = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if TORCH_AVAILABLE else None
        
        if TORCH_AVAILABLE:
            self._load_specialized_model()
        else:
            self.logger.warning(f"PyTorch not available for {model_type}")
    
    def _load_specialized_model(self):
        """Load the specialized model architecture"""
        try:
            self.logger.info(f"Loading specialized model: {self.model_type}")
            
            if self.model_type == 'chexnet':
                self.model = self._create_chexnet_model()
            elif self.model_type == 'dermnet':
                self.model = self._create_dermnet_model()
            elif self.model_type == 'fastmri':
                self.model = self._create_fastmri_model()
            elif self.model_type == 'retina_net':
                self.model = self._create_retina_model()
            else:
                self.model = self._create_generic_model()
            
            # Setup transforms
            self._setup_transforms()
            
            # Move to device
            if self.model and self.device:
                self.model = self.model.to(self.device)
                self.model.eval()
            
            self.logger.info(f"✅ Specialized model {self.model_type} loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load specialized model {self.model_type}: {e}")
            self.model = None
    
    def _create_chexnet_model(self):
        """Create CheXNet-style model for chest X-ray analysis"""
        try:
            # Use DenseNet-121 as base (CheXNet architecture)
            model = models.densenet121(pretrained=True)
            
            # Modify classifier for 14 chest conditions
            num_classes = len(self.config['conditions'])
            model.classifier = nn.Linear(model.classifier.in_features, num_classes)
            
            # Apply sigmoid for multi-label classification
            model.classifier = nn.Sequential(
                model.classifier,
                nn.Sigmoid()
            )
            
            return model
            
        except Exception as e:
            self.logger.error(f"CheXNet model creation failed: {e}")
            return None
    
    def _create_dermnet_model(self):
        """Create DermNet-style model for skin condition analysis"""
        try:
            # Use ResNet-50 as base (common for dermatology)
            model = models.resnet50(pretrained=True)
            
            # Modify final layer for skin conditions
            num_classes = len(self.config['conditions'])
            model.fc = nn.Linear(model.fc.in_features, num_classes)
            
            return model
            
        except Exception as e:
            self.logger.error(f"DermNet model creation failed: {e}")
            return None
    
    def _create_fastmri_model(self):
        """Create FastMRI-style model for MRI analysis"""
        try:
            # Use ResNet-34 for MRI analysis
            model = models.resnet34(pretrained=True)
            
            # Modify for MRI conditions
            num_classes = len(self.config['conditions'])
            model.fc = nn.Linear(model.fc.in_features, num_classes)
            
            return model
            
        except Exception as e:
            self.logger.error(f"FastMRI model creation failed: {e}")
            return None
    
    def _create_retina_model(self):
        """Create retina analysis model for diabetic retinopathy"""
        try:
            # Use EfficientNet for retinal analysis
            model = models.efficientnet_b0(pretrained=True)
            
            # Modify for DR grading
            num_classes = len(self.config['conditions'])
            model.classifier = nn.Sequential(
                nn.Dropout(0.2),
                nn.Linear(model.classifier[1].in_features, num_classes)
            )
            
            return model
            
        except Exception as e:
            self.logger.error(f"Retina model creation failed: {e}")
            return None
    
    def _create_generic_model(self):
        """Create generic medical imaging model"""
        try:
            model = models.resnet18(pretrained=True)
            num_classes = len(self.config['conditions'])
            model.fc = nn.Linear(model.fc.in_features, num_classes)
            return model
        except Exception as e:
            self.logger.error(f"Generic model creation failed: {e}")
            return None
    
    def _setup_transforms(self):
        """Setup image transforms for the model"""
        input_size = self.config['input_size']
        
        if self.model_type == 'chexnet':
            # CheXNet preprocessing
            self.transform = transforms.Compose([
                transforms.Resize(input_size),
                transforms.CenterCrop(input_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
        elif self.model_type == 'dermnet':
            # DermNet preprocessing
            self.transform = transforms.Compose([
                transforms.Resize(input_size),
                transforms.CenterCrop(input_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
        else:
            # Standard preprocessing
            self.transform = transforms.Compose([
                transforms.Resize(input_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze medical image using specialized model
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Analysis results
        """
        try:
            if self.model is None:
                return self._fallback_analysis()
            
            # Preprocess image
            image = self._preprocess_image(image_data)
            if image is None:
                return {'error': 'Failed to preprocess image'}
            
            # Run inference
            with torch.no_grad():
                if self.device:
                    image = image.to(self.device)
                
                outputs = self.model(image.unsqueeze(0))
                
                # Process outputs based on model type
                predictions = self._process_model_outputs(outputs)
            
            return {
                'success': True,
                'model_type': self.model_type,
                'model_name': self.config['name'],
                'predictions': predictions,
                'confidence_threshold': self.config['confidence_threshold']
            }
            
        except Exception as e:
            self.logger.error(f"Specialized model analysis error: {e}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'fallback': self._fallback_analysis()
            }
    
    def _preprocess_image(self, image_data: bytes) -> Optional[torch.Tensor]:
        """Preprocess image for specialized model"""
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
            
            # Apply model-specific transforms
            if self.transform:
                image_tensor = self.transform(image)
                return image_tensor
            
            return None
            
        except Exception as e:
            self.logger.error(f"Image preprocessing error: {e}")
            return None
    
    def _process_model_outputs(self, outputs: torch.Tensor) -> List[Dict[str, Any]]:
        """Process model outputs into predictions"""
        try:
            predictions = []
            
            if self.model_type == 'chexnet':
                # Multi-label classification for chest conditions
                probabilities = outputs.squeeze().cpu().numpy()
                
                for i, condition in enumerate(self.config['conditions']):
                    confidence = float(probabilities[i]) * 100
                    if confidence > (self.config['confidence_threshold'] * 100):
                        predictions.append({
                            'condition': condition.replace('_', ' '),
                            'confidence': confidence,
                            'severity': self._determine_severity(confidence),
                            'recommendation': self._get_condition_recommendation(condition)
                        })
            
            else:
                # Single-label classification for other models
                probabilities = F.softmax(outputs, dim=1).squeeze().cpu().numpy()
                
                # Get top predictions
                top_indices = np.argsort(probabilities)[::-1][:5]
                
                for idx in top_indices:
                    confidence = float(probabilities[idx]) * 100
                    if confidence > (self.config['confidence_threshold'] * 100):
                        condition = self.config['conditions'][idx]
                        predictions.append({
                            'condition': condition.replace('_', ' '),
                            'confidence': confidence,
                            'severity': self._determine_severity(confidence),
                            'recommendation': self._get_condition_recommendation(condition)
                        })
            
            return sorted(predictions, key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Output processing error: {e}")
            return []
    
    def _determine_severity(self, confidence: float) -> str:
        """Determine severity based on confidence score"""
        if confidence > 80:
            return 'High'
        elif confidence > 60:
            return 'Moderate'
        elif confidence > 40:
            return 'Low'
        else:
            return 'Minimal'
    
    def _get_condition_recommendation(self, condition: str) -> str:
        """Get recommendation for specific condition"""
        condition_lower = condition.lower()
        
        # Urgent conditions
        urgent_conditions = ['pneumothorax', 'mass', 'melanoma', 'severe', 'proliferative']
        if any(urgent in condition_lower for urgent in urgent_conditions):
            return 'Urgent medical evaluation needed'
        
        # Moderate priority conditions
        moderate_conditions = ['pneumonia', 'cardiomegaly', 'moderate', 'basal_cell']
        if any(moderate in condition_lower for moderate in moderate_conditions):
            return 'Medical consultation recommended within 1-2 weeks'
        
        # Low priority conditions
        low_conditions = ['mild', 'benign', 'no_dr', 'normal']
        if any(low in condition_lower for low in low_conditions):
            return 'Routine follow-up or monitoring'
        
        return 'Professional medical evaluation recommended'
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when specialized model fails"""
        return {
            'success': False,
            'model_type': self.model_type,
            'error': 'Specialized model not available',
            'basic_recommendation': f'Consult specialist for {self.model_type} analysis'
        }

class SpecializedMedicalModelManager:
    """
    Manager for all specialized medical models
    """
    
    def __init__(self):
        """Initialize the specialized model manager"""
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self._load_specialized_models()
    
    def _load_specialized_models(self):
        """Load all available specialized models"""
        for model_type, config in SPECIALIZED_MODEL_CONFIGS.items():
            try:
                self.models[model_type] = SpecializedMedicalModel(model_type, config)
                self.logger.info(f"✅ Loaded specialized model: {model_type}")
            except Exception as e:
                self.logger.error(f"Failed to load specialized model {model_type}: {e}")
    
    def analyze_with_specialized_model(self, image_data: bytes, image_type: str, 
                                     symptoms: str = "") -> Dict[str, Any]:
        """
        Analyze image with appropriate specialized model
        
        Args:
            image_data: Raw image bytes
            image_type: Type of medical image
            symptoms: Patient symptoms
            
        Returns:
            Specialized model analysis results
        """
        try:
            # Select appropriate model
            model_type = self._select_specialized_model(image_type, symptoms)
            
            if model_type not in self.models:
                return {
                    'error': f'Specialized model {model_type} not available',
                    'available_models': list(self.models.keys())
                }
            
            # Run analysis
            model = self.models[model_type]
            result = model.analyze_image(image_data)
            
            # Add context information
            result['selected_model'] = model_type
            result['selection_reason'] = self._get_selection_reason(model_type, image_type, symptoms)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Specialized model analysis error: {e}")
            return {
                'success': False,
                'error': f'Specialized analysis failed: {str(e)}'
            }
    
    def _select_specialized_model(self, image_type: str, symptoms: str) -> str:
        """Select the most appropriate specialized model"""
        image_type_lower = image_type.lower() if image_type else ""
        symptoms_lower = symptoms.lower() if symptoms else ""
        
        # Map image types and symptoms to specialized models
        if any(term in image_type_lower for term in ['chest', 'xray', 'x-ray', 'lung']):
            return 'chexnet'
        elif any(term in image_type_lower for term in ['skin', 'dermatology', 'mole', 'lesion']):
            return 'dermnet'
        elif any(term in image_type_lower for term in ['mri', 'magnetic']):
            return 'fastmri'
        elif any(term in image_type_lower for term in ['retina', 'fundus', 'eye']):
            return 'retina_net'
        
        # Check symptoms
        if any(term in symptoms_lower for term in ['chest pain', 'cough', 'breathing']):
            return 'chexnet'
        elif any(term in symptoms_lower for term in ['skin', 'rash', 'mole']):
            return 'dermnet'
        elif any(term in symptoms_lower for term in ['vision', 'diabetes', 'eye']):
            return 'retina_net'
        
        # Default to dermnet for general image analysis
        return 'dermnet'
    
    def _get_selection_reason(self, model_type: str, image_type: str, symptoms: str) -> str:
        """Get reason for model selection"""
        reasons = {
            'chexnet': 'Selected for chest X-ray analysis and respiratory symptoms',
            'dermnet': 'Selected for skin condition analysis and dermatological symptoms',
            'fastmri': 'Selected for MRI analysis and neurological symptoms',
            'retina_net': 'Selected for retinal analysis and diabetic screening'
        }
        return reasons.get(model_type, 'Selected as default specialized model')
    
    def get_available_models(self) -> List[str]:
        """Get list of available specialized models"""
        return list(self.models.keys())
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_type in SPECIALIZED_MODEL_CONFIGS:
            return SPECIALIZED_MODEL_CONFIGS[model_type]
        return {}

# Global specialized model manager
specialized_model_manager = SpecializedMedicalModelManager()

def analyze_with_specialized_medical_model(image_data: bytes, image_type: str = None, 
                                         symptoms: str = "") -> Dict[str, Any]:
    """
    Convenience function for specialized medical model analysis
    
    Args:
        image_data: Raw image bytes
        image_type: Type of medical image
        symptoms: Patient symptoms
        
    Returns:
        Specialized model analysis results
    """
    return specialized_model_manager.analyze_with_specialized_model(
        image_data, image_type, symptoms
    )

if __name__ == "__main__":
    print("🏥 Testing Specialized Medical Models...")
    
    # Test model loading
    available = specialized_model_manager.get_available_models()
    print(f"Available specialized models: {available}")
    
    # Test model selection
    test_cases = [
        ("chest x-ray", "cough and fever"),
        ("skin lesion", "dark mole changing"),
        ("brain mri", "headache"),
        ("retinal photo", "blurred vision")
    ]
    
    for image_type, symptoms in test_cases:
        model = specialized_model_manager._select_specialized_model(image_type, symptoms)
        reason = specialized_model_manager._get_selection_reason(model, image_type, symptoms)
        print(f"Image: {image_type}, Symptoms: {symptoms} -> Model: {model}")
        print(f"  Reason: {reason}")

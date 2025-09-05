# src/ai/enhanced_medical_analysis.py
"""
Enhanced Medical Image Analysis with Doctor Integration
Purpose: Provides detailed diagnosis, specialist recommendations, and integration with doctor database
"""
import logging
import base64
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import io
from openai import OpenAI

class EnhancedMedicalAnalysis:
    """
    Enhanced Medical Analysis with Doctor Database Integration
    """
    
    def __init__(self):
        """Initialize enhanced medical analysis"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI
        self.openai_client = None
        self.openai_available = False
        
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                self.openai_available = True
                self.logger.info("✅ OpenAI Vision initialized for enhanced medical analysis")
            else:
                self.logger.warning("⚠ OpenAI API key not found")
        except Exception as e:
            self.logger.error(f"❌ OpenAI initialization failed: {e}")
        
        # Specialist mapping for doctor database integration
        self.specialist_mapping = {
            'skin': {
                'primary': 'dermatologist',
                'conditions': {
                    'melanoma': 'dermatologist',
                    'skin_cancer': 'dermatologist', 
                    'mole': 'dermatologist',
                    'rash': 'dermatologist',
                    'eczema': 'dermatologist',
                    'psoriasis': 'dermatologist',
                    'acne': 'dermatologist'
                }
            },
            'chest': {
                'primary': 'pulmonologist',
                'conditions': {
                    'pneumonia': 'pulmonologist',
                    'tuberculosis': 'pulmonologist',
                    'asthma': 'pulmonologist',
                    'copd': 'pulmonologist',
                    'heart': 'cardiologist',
                    'cardiac': 'cardiologist'
                }
            },
            'eye': {
                'primary': 'ophthalmologist',
                'conditions': {
                    'glaucoma': 'ophthalmologist',
                    'retina': 'ophthalmologist',
                    'cataract': 'ophthalmologist',
                    'vision': 'ophthalmologist'
                }
            },
            'bone': {
                'primary': 'orthopedist',
                'conditions': {
                    'fracture': 'orthopedist',
                    'joint': 'orthopedist',
                    'arthritis': 'orthopedist',
                    'spine': 'orthopedist'
                }
            }
        }
    
    def analyze_with_doctor_integration(self, image_data: bytes, image_type: str, 
                                      symptoms: str = "", context: str = "",
                                      user_city: str = "Bangalore") -> Dict[str, Any]:
        """
        Enhanced analysis with doctor recommendations integration
        """
        try:
            # Step 1: Get detailed medical analysis from OpenAI
            medical_analysis = self._get_detailed_medical_analysis(
                image_data, image_type, symptoms, context
            )
            
            # Step 2: Extract specialist recommendation
            specialist_info = self._determine_specialist_from_analysis(
                medical_analysis, image_type, symptoms
            )
            
            # Step 3: Get doctor recommendations from database
            doctor_recommendations = self._get_doctor_recommendations(
                specialist_info['primary_specialist'], 
                user_city,
                specialist_info['secondary_specialists']
            )
            
            # Step 4: Create chat redirect data
            chat_redirect_data = self._create_chat_redirect_data(
                medical_analysis, specialist_info, doctor_recommendations, symptoms
            )
            
            # Step 5: Combine all results
            enhanced_result = {
                'medical_analysis': medical_analysis,
                'specialist_recommendation': specialist_info,
                'doctor_recommendations': doctor_recommendations,
                'chat_redirect': chat_redirect_data,
                'urgency_level': medical_analysis.get('urgency_level', 'MODERATE'),
                'confidence_score': medical_analysis.get('confidence', 0.7),
                'next_steps': self._generate_next_steps(medical_analysis, specialist_info),
                'timestamp': str(self._get_current_timestamp())
            }
            
            return {
                'success': True,
                'enhanced_analysis': enhanced_result
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced medical analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_recommendation': self._get_fallback_recommendation(image_type)
            }
    
    def _get_detailed_medical_analysis(self, image_data: bytes, image_type: str,
                                     symptoms: str, context: str) -> Dict[str, Any]:
        """
        Get detailed medical analysis from OpenAI Vision
        """
        if not self.openai_available:
            return self._get_fallback_analysis(image_type, symptoms)
        
        try:
            # Validate and preprocess image
            self.logger.info(f"📸 Processing image: {len(image_data)} bytes, type: {image_type}")
            
            # Validate image format
            try:
                from PIL import Image
                image = Image.open(io.BytesIO(image_data))
                
                # Log image properties
                self.logger.info(f"🖼️ Image format: {image.format}, size: {image.size}, mode: {image.mode}")
                
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    self.logger.info(f"🔄 Converting image from {image.mode} to RGB")
                    image = image.convert('RGB')
                
                # Resize if too large (OpenAI has limits)
                max_size = 2048
                if max(image.size) > max_size:
                    self.logger.info(f"📏 Resizing large image from {image.size}")
                    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    self.logger.info(f"📏 New size: {image.size}")
                
                # Convert back to bytes
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='JPEG', quality=90)
                image_data = img_buffer.getvalue()
                
            except Exception as img_error:
                self.logger.warning(f"⚠️ Image preprocessing failed: {img_error}")
                # Continue with original image data
            
            # Encode image for OpenAI
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            self.logger.info(f"🔗 Base64 encoded length: {len(image_base64)}")
            
            # Create comprehensive medical prompt based on image type
            if image_type == 'bone':
                medical_prompt = f"""
                You are an expert orthopedic radiologist analyzing an X-ray image showing bone/skeletal structures.
                
                Patient Information:
                - Symptoms: {symptoms if symptoms else "None provided"}
                - Context: {context if context else "None"}
                
                Please analyze this X-ray image and provide detailed findings:
                
                BONE/SKELETAL OBSERVATIONS:
                Describe exactly what you see in the X-ray - bone structures, any fractures, alignment, density, joint spaces, soft tissue shadows.
                
                POSSIBLE ORTHOPEDIC CONDITIONS:
                List 2-3 most likely bone/joint conditions with confidence percentages and explanations.
                
                SPECIALIST RECOMMENDATION:
                Recommend orthopedist or orthopedic surgeon for treatment.
                
                URGENCY ASSESSMENT:
                Rate as LOW/MODERATE/HIGH/URGENT with detailed explanation.
                
                QUESTIONS FOR ORTHOPEDIST:
                List 3-5 specific questions about bone healing, treatment options, recovery time.
                
                ORTHOPEDIC PREPARATION:
                What to document and bring to orthopedic consultation.
                
                RED FLAGS:
                Signs requiring immediate orthopedic emergency care.
                
                Focus on detailed visual analysis of bone structures and fracture patterns.
                """
            elif image_type == 'skin':
                medical_prompt = f"""
                You are an expert dermatologist analyzing a skin condition image.
                
                Patient Information:
                - Image type: Dermatological/Skin imaging
                - Reported symptoms: {symptoms if symptoms else "None provided"}
                - Additional context: {context if context else "None"}
                
                Please provide dermatological analysis in this format:
                
                SKIN OBSERVATIONS:
                [Describe skin lesions, color, texture, size, distribution]
                
                POSSIBLE DERMATOLOGICAL CONDITIONS:
                [List 2-3 skin conditions with confidence percentages]
                
                SPECIALIST RECOMMENDATION:
                [MUST recommend: dermatologist or dermatology subspecialist]
                
                URGENCY ASSESSMENT:
                [Rate urgency for dermatological evaluation]
                
                QUESTIONS FOR DERMATOLOGIST:
                [Specific dermatology questions]
                
                DERMATOLOGY PREPARATION:
                [What to prepare for dermatology consultation]
                
                RED FLAGS:
                [Signs requiring immediate dermatological attention]
                """
            else:
                # Generic prompt for other image types
                medical_prompt = f"""
                You are an expert medical AI assistant analyzing a {image_type} medical image. 
                Provide a comprehensive analysis for specialist consultation preparation.
                
                Patient Information:
                - Image type: {image_type}
                - Reported symptoms: {symptoms if symptoms else "None provided"}
                - Additional context: {context if context else "None"}
                
                Please provide a detailed analysis in the following format:
                
                VISUAL OBSERVATIONS:
                [Describe exactly what you see in the image - colors, shapes, abnormalities, size, location]
                
                POSSIBLE CONDITIONS:
                [List 2-3 most likely conditions with confidence percentages and brief explanations]
                
                SPECIALIST RECOMMENDATION:
                [Specify the exact type of specialist needed - be specific: dermatologist, cardiologist, pulmonologist, etc.]
                
                URGENCY ASSESSMENT:
                [Rate as LOW/MODERATE/URGENT with detailed explanation of why]
                
                QUESTIONS FOR SPECIALIST:
                [List 3-5 specific questions the patient should ask during consultation]
                
                PREPARATION FOR APPOINTMENT:
                [What the patient should document, bring, or prepare before seeing the specialist]
                
                RED FLAGS:
                [Any warning signs that would require immediate medical attention]
                
                Be thorough, professional, and focus on preparing the patient for an informed consultation with the appropriate specialist.
                """
            
            # Call OpenAI Vision API
            self.logger.info(f"🤖 Calling OpenAI GPT-4o Vision API...")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": medical_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,  # Increased for more detailed analysis
                temperature=0.2   # Lower for more consistent medical analysis
            )
            
            self.logger.info(f"✅ OpenAI API call successful")
            analysis_text = response.choices[0].message.content
            
            # DEBUG: Log the actual OpenAI response
            self.logger.info(f"🔍 OpenAI Analysis Response Length: {len(analysis_text)}")
            self.logger.info(f"📝 OpenAI Analysis Preview: {analysis_text[:500]}...")
            
            # Validate we got a proper response
            if not analysis_text or len(analysis_text) < 50:
                self.logger.error(f"❌ OpenAI returned insufficient analysis: '{analysis_text}'")
                return self._get_fallback_analysis(image_type, symptoms)
            
            # Parse into structured format
            return self._parse_detailed_analysis(analysis_text, image_type)
            
        except Exception as e:
            self.logger.error(f"OpenAI detailed analysis failed: {e}")
            return self._get_fallback_analysis(image_type, symptoms)
    
    def _parse_detailed_analysis(self, analysis_text: str, image_type: str) -> Dict[str, Any]:
        """
        Parse detailed analysis text into structured format
        """
        sections = {
            'visual_observations': '',
            'possible_conditions': [],
            'specialist_recommendation': '',
            'urgency_assessment': '',
            'questions_for_specialist': [],
            'preparation_notes': [],
            'red_flags': [],
            'confidence': 0.75,
            'urgency_level': 'MODERATE'
        }
        
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            line_lower = line.lower()
            if 'visual observations' in line_lower:
                current_section = 'visual_observations'
                continue
            elif 'possible conditions' in line_lower:
                current_section = 'possible_conditions'
                continue
            elif 'specialist recommendation' in line_lower:
                current_section = 'specialist_recommendation'
                continue
            elif 'urgency assessment' in line_lower:
                current_section = 'urgency_assessment'
                continue
            elif 'questions for specialist' in line_lower:
                current_section = 'questions_for_specialist'
                continue
            elif 'preparation' in line_lower:
                current_section = 'preparation_notes'
                continue
            elif 'red flags' in line_lower:
                current_section = 'red_flags'
                continue
            
            # Parse content based on section
            if current_section == 'visual_observations':
                sections['visual_observations'] += line + ' '
            
            elif current_section == 'possible_conditions':
                condition = self._extract_condition_info(line)
                if condition:
                    sections['possible_conditions'].append(condition)
            
            elif current_section == 'specialist_recommendation':
                sections['specialist_recommendation'] += line + ' '
            
            elif current_section == 'urgency_assessment':
                sections['urgency_assessment'] += line + ' '
                # Extract urgency level
                if 'urgent' in line.lower():
                    sections['urgency_level'] = 'URGENT'
                elif 'low' in line.lower():
                    sections['urgency_level'] = 'LOW'
            
            elif current_section in ['questions_for_specialist', 'preparation_notes', 'red_flags']:
                if line.startswith(('-', '*', '•')) or line[0].isdigit():
                    clean_line = line.lstrip('-*•0123456789. ')
                    if clean_line:
                        sections[current_section].append(clean_line)
        
        # Clean up text fields
        sections['visual_observations'] = sections['visual_observations'].strip()
        sections['specialist_recommendation'] = sections['specialist_recommendation'].strip()
        sections['urgency_assessment'] = sections['urgency_assessment'].strip()
        
        return sections
    
    def _extract_condition_info(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Extract condition information from a line
        """
        # Look for patterns like "Condition Name (75% confidence)" or "Condition: explanation"
        if '%' in line:
            # Try to extract confidence percentage
            import re
            confidence_match = re.search(r'(\d+)%', line)
            confidence = int(confidence_match.group(1)) if confidence_match else 70
            
            # Extract condition name (everything before the percentage)
            condition_name = re.sub(r'\s*\(\d+%.*?\)', '', line).strip()
            condition_name = condition_name.lstrip('-*•0123456789. ')
            
            return {
                'name': condition_name,
                'confidence': confidence,
                'description': line
            }
        elif ':' in line:
            # Format like "Condition: description"
            parts = line.split(':', 1)
            if len(parts) == 2:
                condition_name = parts[0].strip().lstrip('-*•0123456789. ')
                description = parts[1].strip()
                return {
                    'name': condition_name,
                    'confidence': 65,
                    'description': description
                }
        
        return None
    
    def _determine_specialist_from_analysis(self, analysis: Dict[str, Any], 
                                          image_type: str, symptoms: str) -> Dict[str, Any]:
        """
        Determine specialist recommendations from analysis
        """
        specialist_text = analysis.get('specialist_recommendation', '').lower()
        conditions = analysis.get('possible_conditions', [])
        
        # Define specialist keywords for all cases
        specialist_keywords = {
            'dermatologist': ['dermatologist', 'skin', 'dermatology'],
            'cardiologist': ['cardiologist', 'heart', 'cardiac', 'cardiology'],
            'pulmonologist': ['pulmonologist', 'lung', 'respiratory', 'chest'],
            'ophthalmologist': ['ophthalmologist', 'eye', 'vision', 'retina'],
            'orthopedist': ['orthopedist', 'bone', 'joint', 'fracture', 'orthopedic'],
            'neurologist': ['neurologist', 'brain', 'nerve', 'neurology'],
            'gastroenterologist': ['gastroenterologist', 'stomach', 'digestive', 'gut'],
            'urologist': ['urologist', 'kidney', 'bladder', 'urinary'],
            'gynecologist': ['gynecologist', 'women', 'female', 'gynecology'],
            'psychiatrist': ['psychiatrist', 'mental', 'psychology', 'psychiatric'],
            'general-physician': ['general', 'physician', 'gp', 'family']
        }
        
        # FORCE orthopedist for bone images - NO EXCEPTIONS
        if image_type == 'bone':
            primary_specialist = 'orthopedist'
        # FORCE dermatologist for skin images  
        elif image_type == 'skin':
            primary_specialist = 'dermatologist'
        else:
            # Primary specialist based on image type
            primary_specialist = self.specialist_mapping.get(image_type, {}).get('primary', 'general-physician')
            
            # Check specialist recommendation in analysis for AI override
            for specialist, keywords in specialist_keywords.items():
                if any(keyword in specialist_text for keyword in keywords):
                    primary_specialist = specialist
                    break
        
        # Secondary specialists based on conditions
        secondary_specialists = []
        for condition in conditions:
            condition_name = condition.get('name', '').lower()
            for specialist, keywords in specialist_keywords.items():
                if specialist != primary_specialist and any(keyword in condition_name for keyword in keywords):
                    if specialist not in secondary_specialists:
                        secondary_specialists.append(specialist)
        
        return {
            'primary_specialist': primary_specialist,
            'secondary_specialists': secondary_specialists,
            'reasoning': specialist_text,
            'confidence': analysis.get('confidence', 0.75)
        }
    
    def _get_doctor_recommendations(self, primary_specialist: str, user_city: str,
                                  secondary_specialists: List[str]) -> Dict[str, Any]:
        """
        Get doctor recommendations from database
        """
        try:
            # Import doctor recommender
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from doctor_recommender import DoctorRecommender
            
            dr = DoctorRecommender()
            
            # Get primary specialist doctors
            primary_doctors = dr.recommend_doctors(
                primary_specialist, 
                user_city, 
                limit=5, 
                sort_by="rating"
            )
            
            # Get secondary specialist doctors if needed
            secondary_doctors = {}
            for specialist in secondary_specialists[:2]:  # Limit to 2 secondary
                try:
                    docs = dr.recommend_doctors(specialist, user_city, limit=3, sort_by="rating")
                    secondary_doctors[specialist] = docs
                except Exception as e:
                    self.logger.warning(f"Failed to get {specialist} recommendations: {e}")
            
            return {
                'primary_specialist': primary_specialist,
                'primary_doctors': primary_doctors,
                'secondary_specialists': secondary_doctors,
                'total_doctors_found': len(primary_doctors) + sum(len(docs) for docs in secondary_doctors.values()),
                'city': user_city
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get doctor recommendations: {e}")
            return {
                'error': str(e),
                'primary_specialist': primary_specialist,
                'primary_doctors': [],
                'secondary_specialists': {},
                'total_doctors_found': 0
            }
    
    def _create_chat_redirect_data(self, medical_analysis: Dict[str, Any], 
                                 specialist_info: Dict[str, Any],
                                 doctor_recommendations: Dict[str, Any],
                                 symptoms: str) -> Dict[str, Any]:
        """
        Create data for chat redirect with pre-loaded information
        """
        # Format questions for specialist
        questions = medical_analysis.get('questions_for_specialist', [])
        if not questions:
            questions = self._generate_default_questions(specialist_info['primary_specialist'])
        
        # Create chat context
        chat_context = f"""
        Based on your medical image analysis, here's what I found:
        
        **Analysis Summary:**
        {medical_analysis.get('visual_observations', 'Medical image analyzed')}
        
        **Recommended Specialist:** {specialist_info['primary_specialist'].replace('-', ' ').title()}
        
        **Questions to ask your specialist:**
        """ + '\n'.join([f"• {q}" for q in questions[:5]])
        
        if doctor_recommendations.get('primary_doctors'):
            chat_context += f"\n\n**I found {len(doctor_recommendations['primary_doctors'])} recommended {specialist_info['primary_specialist'].replace('-', ' ').title()}s in {doctor_recommendations.get('city', 'your area')}:**"
        
        return {
            'chat_message': chat_context,
            'specialist_loaded': specialist_info['primary_specialist'],
            'doctors_loaded': doctor_recommendations,
            'urgency': medical_analysis.get('urgency_level', 'MODERATE'),
            'redirect_url': '/chat?specialist=' + specialist_info['primary_specialist']
        }
    
    def _generate_next_steps(self, medical_analysis: Dict[str, Any], 
                           specialist_info: Dict[str, Any]) -> List[str]:
        """
        Generate specific next steps for the patient
        """
        urgency = medical_analysis.get('urgency_level', 'MODERATE')
        specialist = specialist_info['primary_specialist'].replace('-', ' ').title()
        
        steps = []
        
        if urgency == 'URGENT':
            steps.append("🚨 Seek immediate medical attention")
            steps.append("🏥 Consider emergency room or urgent care")
            steps.append("📱 Call healthcare provider immediately")
        elif urgency == 'MODERATE':
            steps.append(f"📅 Schedule appointment with {specialist} within 1-2 weeks")
            steps.append("📝 Prepare questions listed below for your consultation")
        else:
            steps.append(f"📋 Consider routine consultation with {specialist}")
        
        steps.extend([
            "📸 Save this analysis report for your appointment",
            "📋 Document any changes in symptoms",
            "🎯 Use the specialist finder below to locate doctors",
            "💬 Continue in chat for more guidance"
        ])
        
        return steps
    
    def _generate_default_questions(self, specialist: str) -> List[str]:
        """
        Generate default questions based on specialist type
        """
        common_questions = {
            'dermatologist': [
                "What is your assessment of this skin condition?",
                "Are there any concerning features I should monitor?",
                "What treatment options are available?",
                "How often should I have follow-up appointments?",
                "Are there lifestyle changes I should make?"
            ],
            'cardiologist': [
                "What do you see in my chest imaging?",
                "Are there any heart-related concerns?",
                "What additional tests might be needed?",
                "What lifestyle modifications would you recommend?",
                "Should I monitor any specific symptoms?"
            ],
            'pulmonologist': [
                "What do you observe in my chest image?",
                "Are there any lung-related abnormalities?",
                "What breathing tests might be helpful?",
                "How can I improve my respiratory health?",
                "What follow-up care is recommended?"
            ]
        }
        
        return common_questions.get(specialist, [
            "What is your professional assessment?",
            "What additional tests might be needed?",
            "What are my treatment options?",
            "What should I monitor at home?",
            "When should I schedule follow-up?"
        ])
    
    def _get_fallback_analysis(self, image_type: str, symptoms: str) -> Dict[str, Any]:
        """
        Fallback analysis when OpenAI is not available
        """
        return {
            'visual_observations': f'Medical {image_type} image received for analysis',
            'possible_conditions': [
                {
                    'name': f'Condition requiring {image_type} specialist evaluation',
                    'confidence': 50,
                    'description': 'Professional medical evaluation needed for accurate diagnosis'
                }
            ],
            'specialist_recommendation': self.specialist_mapping.get(image_type, {}).get('primary', 'general-physician'),
            'urgency_assessment': 'Professional medical consultation recommended',
            'questions_for_specialist': self._generate_default_questions(image_type),
            'preparation_notes': ['Bring original image', 'Document symptoms'],
            'red_flags': ['Worsening symptoms', 'New concerning features'],
            'confidence': 0.5,
            'urgency_level': 'MODERATE'
        }
    
    def _get_fallback_recommendation(self, image_type: str) -> Dict[str, Any]:
        """
        Get fallback recommendation when analysis fails
        """
        specialist = self.specialist_mapping.get(image_type, {}).get('primary', 'general-physician')
        return {
            'specialist_recommendation': specialist,
            'urgency_level': 'MODERATE',
            'message': f'Professional {specialist.replace("-", " ").title()} consultation recommended'
        }
    
    def _get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now()

# Add these updates to src/llm/recommender.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from medical_translator import MedicalResponseTranslator

# Initialize medical translator
medical_translator = MedicalResponseTranslator()

def get_medical_recommendations(user_message, user_location=None, sort_preference='rating', user_id=None, language='en'):
    """
    Enhanced medical recommendation function with multilingual support
    """
    try:
        # Set language for medical translator
        medical_translator.set_language(language)
        
        # Original OpenAI conversation in English (for better AI understanding)
        conversation = [
            {
                "role": "system",
                "content": """You are MedBot, an advanced medical AI assistant. Your role is to:

1. ANALYZE user symptoms and medical concerns with empathy and professionalism
2. RECOMMEND appropriate medical specialties based on symptoms
3. PROVIDE general health guidance (not medical diagnosis)
4. ALWAYS encourage consulting healthcare professionals for serious concerns

IMPORTANT GUIDELINES:
- Never provide medical diagnoses or treatment advice
- Always recommend consulting qualified medical professionals
- Focus on specialist recommendations based on symptoms
- Be empathetic and supportive in your responses
- Include relevant health tips when appropriate

When recommending specialists, use this format at the end of your response:
**SPECIALIST_RECOMMENDATIONS: [specialty1, specialty2, ...]**

Available specialties: Cardiology, Dermatology, Endocrinology, Gastroenterology, Gynecology, Neurology, Oncology, Ophthalmology, Orthopedics, Pediatrics, Psychiatry, Pulmonology, Urology, General Medicine, ENT, Nephrology"""
            },
            {
                "role": "user", 
                "content": user_message
            }
        ]
        
        # Get AI response in English
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=800,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"🤖 AI Response (English): {ai_response}")
        
        # Extract specialist recommendations
        specialists = []
        if "**SPECIALIST_RECOMMENDATIONS:" in ai_response:
            try:
                specialist_section = ai_response.split("**SPECIALIST_RECOMMENDATIONS:")[1]
                specialist_list = specialist_section.split("**")[0].strip()
                specialists = [s.strip() for s in specialist_list.strip("[]").split(",") if s.strip()]
                print(f"🎯 Extracted specialists: {specialists}")
                
                # Remove specialist section from main response for cleaner output
                ai_response = ai_response.split("**SPECIALIST_RECOMMENDATIONS:")[0].strip()
                
            except Exception as e:
                print(f"⚠️ Error extracting specialists: {e}")
        
        # Translate the AI response to target language
        if language != 'en':
            ai_response = medical_translator.translate_text(ai_response)
            print(f"🌍 Translated Response ({language}): {ai_response}")
        
        # Store conversation in chat history
        if user_id:
            chat_history_manager.add_message(user_id, user_message, 'user', language)
        
        # Build final response
        final_response = ai_response
        
        # Add doctor recommendations if specialists were identified
        if specialists:
            print(f"🔍 Processing {len(specialists)} specialist recommendations...")
            
            # Get user location for distance calculations
            user_lat, user_lng = None, None
            if user_location and 'lat' in user_location and 'lng' in user_location:
                user_lat = float(user_location['lat'])
                user_lng = float(user_location['lng'])
                print(f"📍 User location: {user_lat}, {user_lng}")
            
            # Get doctor recommendations for each specialty
            all_doctors = []
            for specialty in specialists:
                try:
                    print(f"🏥 Finding doctors for specialty: {specialty}")
                    doctors = find_doctors_by_specialty(
                        specialty=specialty,
                        user_lat=user_lat,
                        user_lng=user_lng,
                        sort_preference=sort_preference,
                        limit=3  # Limit per specialty
                    )
                    
                    if doctors:
                        print(f"✅ Found {len(doctors)} doctors for {specialty}")
                        all_doctors.extend(doctors)
                    else:
                        print(f"❌ No doctors found for {specialty}")
                        
                except Exception as e:
                    print(f"❌ Error finding doctors for {specialty}: {e}")
                    continue
            
            # Format doctor recommendations
            if all_doctors:
                print(f"🎯 Total doctors found: {len(all_doctors)}")
                
                # Sort all doctors by the selected preference
                if sort_preference == 'rating':
                    all_doctors.sort(key=lambda x: float(x.get('rating', 0)), reverse=True)
                elif sort_preference == 'experience':
                    all_doctors.sort(key=lambda x: int(x.get('experience_years', 0)), reverse=True)
                elif sort_preference == 'location' and user_lat and user_lng:
                    all_doctors.sort(key=lambda x: float(x.get('distance_km', float('inf'))))
                
                # Take top doctors
                top_doctors = all_doctors[:6]  # Show top 6 overall
                
                # Create doctor table with multilingual headers
                doctor_table = create_multilingual_doctor_table(top_doctors, language)
                final_response += f"\n\n{doctor_table}"
                
                print(f"✅ Added doctor recommendations table with {len(top_doctors)} doctors")
            else:
                no_doctors_msg = medical_translator.get_text('doctor.no_doctors_found') if language != 'en' else "No doctors found for the recommended specialties in our database."
                final_response += f"\n\n{no_doctors_msg}"
        
        # Store final response in chat history
        if user_id:
            chat_history_manager.add_message(user_id, final_response, 'bot', language)
        
        return final_response
        
    except Exception as e:
        error_msg = f"Error in medical recommendations: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Translate error message
        if language != 'en':
            error_msg = medical_translator.get_text('error.processing') + ": " + str(e)
        
        return error_msg

def create_multilingual_doctor_table(doctors, language='en'):
    """
    Create doctor recommendation table with multilingual headers
    """
    try:
        # Get translated headers
        headers = {
            'en': {
                'title': '🏥 **Recommended Doctors**',
                'name': 'Doctor',
                'specialty': 'Specialty', 
                'rating': 'Rating',
                'experience': 'Experience',
                'location': 'Location',
                'distance': 'Distance'
            },
            'hi': {
                'title': '🏥 **अनुशंसित डॉक्टर**',
                'name': 'डॉक्टर',
                'specialty': 'विशेषज्ञता',
                'rating': 'रेटिंग', 
                'experience': 'अनुभव',
                'location': 'स्थान',
                'distance': 'दूरी'
            },
            'kn': {
                'title': '🏥 **ಶಿಫಾರಸು ಮಾಡಿದ ವೈದ್ಯರು**',
                'name': 'ವೈದ್ಯರು',
                'specialty': 'ವಿಶೇಷತೆ',
                'rating': 'ರೇಟಿಂಗ್',
                'experience': 'ಅನುಭವ', 
                'location': 'ಸ್ಥಳ',
                'distance': 'ಅಂತರ'
            }
        }
        
        # Use English as fallback
        header_texts = headers.get(language, headers['en'])
        
        table_html = f"""
        <div class="doctor-recommendations">
            <h3>{header_texts['title']}</h3>
            <div class="table-container">
                <table class="doctor-table">
                    <thead>
                        <tr>
                            <th>{header_texts['name']}</th>
                            <th>{header_texts['specialty']}</th>
                            <th>{header_texts['rating']}</th>
                            <th>{header_texts['experience']}</th>
                            <th>{header_texts['location']}</th>
                            <th>{header_texts['distance']}</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for doctor in doctors:
            # Translate specialty if needed
            specialty = doctor.get('specialty', 'General Medicine')
            if language != 'en':
                specialty = medical_translator.translate_specialty(specialty)
            
            distance_text = f"{doctor.get('distance_km', 'N/A')} km" if doctor.get('distance_km') != 'N/A' else 'N/A'
            
            table_html += f"""
                        <tr>
                            <td><strong>Dr. {doctor.get('name', 'Unknown')}</strong></td>
                            <td>{specialty}</td>
                            <td>⭐ {doctor.get('rating', 'N/A')}</td>
                            <td>{doctor.get('experience_years', 'N/A')} years</td>
                            <td>{doctor.get('locality', 'Unknown')}, {doctor.get('city', 'Unknown')}</td>
                            <td>{distance_text}</td>
                        </tr>
            """
        
        table_html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return table_html
        
    except Exception as e:
        print(f"❌ Error creating multilingual doctor table: {e}")
        return f"Error displaying doctor recommendations: {str(e)}"

# Update find_doctors_by_specialty function for better integration
def find_doctors_by_specialty(specialty, user_lat=None, user_lng=None, sort_preference='rating', limit=5):
    """
    Enhanced doctor finding with better specialty matching
    """
    try:
        from doctor_recommender import DoctorRecommender
        recommender = DoctorRecommender()
        
        # Specialty mapping for better matching
        specialty_mapping = {
            'cardiology': 'Cardiologist',
            'dermatology': 'Dermatologist', 
            'endocrinology': 'Endocrinologist',
            'gastroenterology': 'Gastroenterologist',
            'gynecology': 'Gynecologist',
            'neurology': 'Neurologist',
            'oncology': 'Oncologist',
            'ophthalmology': 'Ophthalmologist',
            'orthopedics': 'Orthopedist',
            'pediatrics': 'Pediatrician',
            'psychiatry': 'Psychiatrist',
            'pulmonology': 'Pulmonologist',
            'urology': 'Urologist',
            'general medicine': 'General Physician',
            'ent': 'ENT Specialist',
            'nephrology': 'Nephrologist'
        }
        
        # Map specialty to database format
        db_specialty = specialty_mapping.get(specialty.lower(), specialty)
        
        # Find doctors
        doctors = recommender.find_doctors_by_specialty(
            specialty=db_specialty,
            user_lat=user_lat,
            user_lng=user_lng,
            sort_by=sort_preference,
            limit=limit
        )
        
        return doctors
        
    except Exception as e:
        print(f"❌ Error in find_doctors_by_specialty: {e}")
        return []

# simple_translator.py
"""
Simple translation system for Medibot without external dependencies
Uses pre-defined translations instead of Google Translate API
"""
import json
import os

class SimpleTranslator:
    def __init__(self):
        self.translations = {}
        self.current_language = 'en'
        self.load_translations()
        
    def load_translations(self):
        """Load translation files"""
        try:
            translations_dir = os.path.join(os.path.dirname(__file__), 'i18n', 'translations')
            
            for lang_file in ['en.json', 'hi.json', 'kn.json']:
                lang_code = lang_file.split('.')[0]
                file_path = os.path.join(translations_dir, lang_file)
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                else:
                    self.translations[lang_code] = {}
                    
        except Exception as e:
            print(f"Error loading translations: {e}")
            self.translations = {'en': {}, 'hi': {}, 'kn': {}}
    
    def set_language(self, language):
        """Set current language"""
        if language in self.translations:
            self.current_language = language
    
    def get_text(self, key, default=None):
        """Get translated text for a key"""
        try:
            # Navigate nested keys (e.g., 'error.invalid_input')
            keys = key.split('.')
            value = self.translations.get(self.current_language, {})
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # Fallback to English
                    value = self.translations.get('en', {})
                    for k in keys:
                        if isinstance(value, dict) and k in value:
                            value = value[k]
                        else:
                            return default or key
                    break
            
            return value if isinstance(value, str) else (default or key)
            
        except Exception:
            return default or key
    
    def translate_specialty(self, specialty):
        """Translate medical specialty"""
        specialty_key = f"medical.specialties.{specialty.lower().replace(' ', '_')}"
        return self.get_text(specialty_key, specialty)
    
    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.translations.keys())

# Medical specialties translation mapping
MEDICAL_SPECIALTIES = {
    'en': {
        'cardiologist': 'Cardiologist',
        'dermatologist': 'Dermatologist',
        'endocrinologist': 'Endocrinologist',
        'gastroenterologist': 'Gastroenterologist',
        'gynecologist': 'Gynecologist',
        'neurologist': 'Neurologist',
        'oncologist': 'Oncologist',
        'ophthalmologist': 'Ophthalmologist',
        'orthopedist': 'Orthopedist',
        'pediatrician': 'Pediatrician',
        'psychiatrist': 'Psychiatrist',
        'pulmonologist': 'Pulmonologist',
        'urologist': 'Urologist',
        'general_physician': 'General Physician',
        'ent_specialist': 'ENT Specialist',
        'nephrologist': 'Nephrologist'
    },
    'hi': {
        'cardiologist': 'हृदय रोग विशेषज्ञ',
        'dermatologist': 'त्वचा रोग विशेषज्ञ',
        'endocrinologist': 'अंतःस्रावी विशेषज्ञ',
        'gastroenterologist': 'गैस्ट्रो विशेषज्ञ',
        'gynecologist': 'स्त्री रोग विशेषज्ञ',
        'neurologist': 'न्यूरोलॉजिस्ट',
        'oncologist': 'कैंसर विशेषज्ञ',
        'ophthalmologist': 'नेत्र रोग विशेषज्ञ',
        'orthopedist': 'हड्डी रोग विशेषज्ञ',
        'pediatrician': 'बाल रोग विशेषज्ञ',
        'psychiatrist': 'मानसिक रोग विशेषज्ञ',
        'pulmonologist': 'फेफड़े के विशेषज्ञ',
        'urologist': 'यूरोलॉजिस्ट',
        'general_physician': 'सामान्य चिकित्सक',
        'ent_specialist': 'कान नाक गला विशेषज्ञ',
        'nephrologist': 'गुर्दे के विशेषज्ञ'
    },
    'kn': {
        'cardiologist': 'ಹೃದಯ ರೋಗ ತಜ್ಞ',
        'dermatologist': 'ಚರ್ಮ ರೋಗ ತಜ್ಞ',
        'endocrinologist': 'ಅಂತಃಸ್ರಾವಶಾಸ್ತ್ರ ತಜ್ಞ',
        'gastroenterologist': 'ಗ್ಯಾಸ್ಟ್ರೋ ತಜ್ಞ',
        'gynecologist': 'ಸ್ತ್ರೀ ರೋಗ ತಜ್ಞ',
        'neurologist': 'ನ್ಯೂರಾಲಜಿಸ್ಟ್',
        'oncologist': 'ಕ್ಯಾನ್ಸರ್ ತಜ್ಞ',
        'ophthalmologist': 'ನೇತ್ರ ರೋಗ ತಜ್ಞ',
        'orthopedist': 'ಮೂಳೆ ರೋಗ ತಜ್ಞ',
        'pediatrician': 'ಮಕ್ಕಳ ವೈದ್ಯ',
        'psychiatrist': 'ಮಾನಸಿಕ ರೋಗ ತಜ್ಞ',
        'pulmonologist': 'ಶ್ವಾಸಕೋಶ ತಜ್ಞ',
        'urologist': 'ಯೂರಾಲಜಿಸ್ಟ್',
        'general_physician': 'ಸಾಮಾನ್ಯ ವೈದ್ಯ',
        'ent_specialist': 'ಇಎನ್‌ಟಿ ತಜ್ಞ',
        'nephrologist': 'ಮೂತ್ರಪಿಂಡ ತಜ್ಞ'
    }
}

class MedicalTranslator:
    def __init__(self):
        self.current_language = 'en'
    
    def set_language(self, language):
        self.current_language = language if language in MEDICAL_SPECIALTIES else 'en'
    
    def translate_specialty(self, specialty):
        """Translate medical specialty"""
        specialty_key = specialty.lower().replace(' ', '_')
        return MEDICAL_SPECIALTIES.get(self.current_language, {}).get(
            specialty_key, 
            MEDICAL_SPECIALTIES['en'].get(specialty_key, specialty)
        )
    
    def translate_text(self, text):
        """Basic text translation - in a real implementation you'd add more translations"""
        # For now, return the original text (can be extended with more translations)
        return text

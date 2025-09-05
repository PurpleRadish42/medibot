# config/languages.py
"""
Language configuration for Medibot
"""

# Supported languages
LANGUAGES = {
    'en': 'English',
    'hi': 'हिन्दी (Hindi)',
    'kn': 'ಕನ್ನಡ (Kannada)',
    'ta': 'தமிழ் (Tamil)',
    'te': 'తెలుగు (Telugu)',
    'ml': 'മലയാളം (Malayalam)',
    'bn': 'বাংলা (Bengali)',
    'gu': 'ગુજરાતી (Gujarati)',
    'mr': 'मराठी (Marathi)',
    'pa': 'ਪੰਜਾਬੀ (Punjabi)'
}

# Default language
DEFAULT_LANGUAGE = 'en'

# Language direction (for RTL languages like Arabic/Hebrew if added later)
LANGUAGE_DIRECTION = {
    'en': 'ltr',
    'hi': 'ltr',
    'kn': 'ltr',
    'ta': 'ltr',
    'te': 'ltr',
    'ml': 'ltr',
    'bn': 'ltr',
    'gu': 'ltr',
    'mr': 'ltr',
    'pa': 'ltr'
}

# Language-specific medical specialties mapping
MEDICAL_SPECIALTIES_I18N = {
    'en': {
        'cardiologist': 'Cardiologist',
        'orthopedist': 'Orthopedist',
        'neurologist': 'Neurologist',
        'dermatologist': 'Dermatologist',
        'gastroenterologist': 'Gastroenterologist',
        'gynecologist': 'Gynecologist',
        'pediatrician': 'Pediatrician',
        'psychiatrist': 'Psychiatrist',
        'general-physician': 'General Physician'
    },
    'hi': {
        'cardiologist': 'हृदय रोग विशेषज्ञ',
        'orthopedist': 'हड्डी रोग विशेषज्ञ',
        'neurologist': 'न्यूरोलॉजिस्ट',
        'dermatologist': 'त्वचा रोग विशेषज्ञ',
        'gastroenterologist': 'गैस्ट्रोएंटेरोलॉजिस्ट',
        'gynecologist': 'स्त्री रोग विशेषज्ञ',
        'pediatrician': 'बाल रोग विशेषज्ञ',
        'psychiatrist': 'मनोचिकित्सक',
        'general-physician': 'सामान्य चिकित्सक'
    },
    'kn': {
        'cardiologist': 'ಹೃದಯ ರೋಗ ತಜ್ಞ',
        'orthopedist': 'ಮೂಳೆ ರೋಗ ತಜ್ಞ',
        'neurologist': 'ನರರೋಗ ತಜ್ಞ',
        'dermatologist': 'ಚರ್ಮ ರೋಗ ತಜ್ಞ',
        'gastroenterologist': 'ಜೀರ್ಣಾಂಗ ತಜ್ಞ',
        'gynecologist': 'ಸ್ತ್ರೀ ರೋಗ ತಜ್ಞ',
        'pediatrician': 'ಮಕ್ಕಳ ರೋಗ ತಜ್ಞ',
        'psychiatrist': 'ಮನೋವೈದ್ಯ',
        'general-physician': 'ಸಾಮಾನ್ಯ ವೈದ್ಯ'
    }
    # Add more languages as needed
}

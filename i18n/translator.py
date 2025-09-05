# i18n/translator.py
"""
Translation management system for Medibot
"""
import os
import json
from flask import request, session
from config.languages import LANGUAGES, DEFAULT_LANGUAGE, MEDICAL_SPECIALTIES_I18N

class MedibotTranslator:
    def __init__(self, app=None):
        self.translations = {}
        self.current_language = DEFAULT_LANGUAGE
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the translator with Flask app"""
        self.load_translations()
        
        @app.context_processor
        def inject_language_vars():
            return {
                'LANGUAGES': LANGUAGES,
                'current_language': self.get_current_language(),
                '_': self.gettext,
                'ngettext': self.ngettext
            }
    
    def load_translations(self):
        """Load all translation files"""
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        
        for lang_code in LANGUAGES.keys():
            translation_file = os.path.join(translations_dir, f'{lang_code}.json')
            if os.path.exists(translation_file):
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            else:
                self.translations[lang_code] = {}
    
    def get_current_language(self):
        """Get current language from session or browser"""
        # Priority: 1. Session, 2. URL parameter, 3. Browser, 4. Default
        lang = session.get('language')
        if not lang:
            lang = request.args.get('lang')
        if not lang and request.headers.get('Accept-Language'):
            # Parse browser language
            browser_lang = request.headers.get('Accept-Language', '').split(',')[0].split('-')[0]
            lang = browser_lang if browser_lang in LANGUAGES else DEFAULT_LANGUAGE
        return lang or DEFAULT_LANGUAGE
    
    def set_language(self, language_code):
        """Set current language"""
        if language_code in LANGUAGES:
            session['language'] = language_code
            self.current_language = language_code
            return True
        return False
    
    def gettext(self, key, **kwargs):
        """Get translated text"""
        lang = self.get_current_language()
        translation = self.translations.get(lang, {}).get(key, key)
        
        # Handle placeholder substitution
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return translation
    
    def ngettext(self, singular, plural, num):
        """Get plural-aware translated text"""
        lang = self.get_current_language()
        key = singular if num == 1 else plural
        return self.translations.get(lang, {}).get(key, key)
    
    def get_medical_specialty(self, specialty_key):
        """Get translated medical specialty"""
        lang = self.get_current_language()
        return MEDICAL_SPECIALTIES_I18N.get(lang, {}).get(specialty_key, specialty_key)

# Global translator instance
translator = MedibotTranslator()

# i18n/medical_translator.py
"""
Medical response translation system
"""
import re
from translator import translator

class MedicalResponseTranslator:
    """Translates medical AI responses while preserving HTML tables and medical data"""
    
    def translate_medical_response(self, response):
        """Translate medical response while preserving structured data"""
        try:
            # Split response into text and HTML table parts
            parts = self.split_response(response)
            translated_parts = []
            
            for part in parts:
                if part['type'] == 'text':
                    translated_parts.append(self.translate_text_part(part['content']))
                elif part['type'] == 'table':
                    translated_parts.append(self.translate_table_part(part['content']))
                else:
                    translated_parts.append(part['content'])
            
            return ''.join(translated_parts)
            
        except Exception as e:
            print(f"Translation error: {e}")
            return response  # Return original if translation fails
    
    def split_response(self, response):
        """Split response into translatable parts"""
        parts = []
        current_pos = 0
        
        # Find all table tags
        table_pattern = r'<table[^>]*>.*?</table>'
        table_matches = list(re.finditer(table_pattern, response, re.DOTALL | re.IGNORECASE))
        
        for match in table_matches:
            # Add text before table
            if match.start() > current_pos:
                text_content = response[current_pos:match.start()].strip()
                if text_content:
                    parts.append({'type': 'text', 'content': text_content})
            
            # Add table
            parts.append({'type': 'table', 'content': match.group()})
            current_pos = match.end()
        
        # Add remaining text after last table
        if current_pos < len(response):
            text_content = response[current_pos:].strip()
            if text_content:
                parts.append({'type': 'text', 'content': text_content})
        
        # If no tables found, treat entire response as text
        if not parts:
            parts.append({'type': 'text', 'content': response})
        
        return parts
    
    def translate_text_part(self, text):
        """Translate text parts of the response"""
        # Translate common medical phrases
        translations = {
            'Based on your symptoms, I recommend': translator.gettext('medical_recommendation_prefix'),
            'Here are qualified': translator.gettext('doctor_list_title').split('{specialty}')[0].strip(),
            'doctors in your area': translator.gettext('doctor_list_title').split('{specialty}')[1].strip() if '{specialty}' in translator.gettext('doctor_list_title') else '',
        }
        
        translated_text = text
        for english, translated in translations.items():
            if translated:
                translated_text = translated_text.replace(english, translated)
        
        return translated_text
    
    def translate_table_part(self, table_html):
        """Translate table headers while preserving data and structure"""
        # Translate table headers
        header_translations = {
            'Doctor Name': translator.gettext('doctor_table_name'),
            'Specialty': translator.gettext('doctor_table_specialty'),
            'Experience': translator.gettext('doctor_table_experience'),
            'Rating': translator.gettext('doctor_table_rating'),
            'Consultation Fee': translator.gettext('doctor_table_fee'),
            'Location': translator.gettext('doctor_table_location'),
            'Contact': translator.gettext('doctor_table_contact'),
        }
        
        translated_table = table_html
        for english, translated in header_translations.items():
            translated_table = translated_table.replace(f'>{english}<', f'>{translated}<')
            translated_table = translated_table.replace(f'<th>{english}</th>', f'<th>{translated}</th>')
        
        return translated_table

# Global medical translator instance
medical_translator = MedicalResponseTranslator()

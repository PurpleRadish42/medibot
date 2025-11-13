# Internationalization (i18n)

This directory contains translation and localization modules for MediBot.

## Files

- `translator.py` - Translation service handler
  - Language detection
  - Text translation API integration
  - Multi-language support

- `medical_translator.py` - Medical term translation
  - Specialized medical terminology
  - Symptom translation
  - Specialty name localization

## Subdirectories

- **translations/** - Translation files for different languages
  - Language-specific JSON or PO files
  - Medical term dictionaries
  - UI text translations

## Configuration

Language settings are managed in `config/languages.py`:
```python
SUPPORTED_LANGUAGES = ['en', 'hi', 'kn', 'ta']
DEFAULT_LANGUAGE = 'en'
```

## Usage

```python
from i18n.translator import translate_text
from i18n.medical_translator import translate_symptom

# Translate general text
translated = translate_text("Hello", target_lang="hi")

# Translate medical terms
symptom = translate_symptom("headache", target_lang="hi")
```

## Adding Languages

1. Create translation file in `translations/<lang_code>/`
2. Add language code to `config/languages.py`
3. Update medical term dictionary
4. Test with all UI components

## Dependencies

- `googletrans` or similar translation library
- `babel` for locale management

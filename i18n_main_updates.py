# Add this to your main.py imports section

# Add these imports after your existing imports
import sys
import os
from pathlib import Path

# Add the i18n directory to the Python path
project_root = Path(__file__).parent
i18n_path = project_root / "i18n"
config_path = project_root / "config"
sys.path.insert(0, str(i18n_path))
sys.path.insert(0, str(config_path))

# Import translation system
from translator import MedibotTranslator, translator
from languages import LANGUAGES, DEFAULT_LANGUAGE

# In your Flask app initialization section, add:
# Initialize translator
translator.init_app(app)

# Add language route
@app.route('/set_language/<language_code>')
def set_language(language_code):
    """Set user's preferred language"""
    success = translator.set_language(language_code)
    if success:
        return jsonify({
            'success': True,
            'message': translator.gettext('language_changed'),
            'language': language_code
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid language'
        }), 400

# Add language API endpoint
@app.route('/api/languages')
def get_languages():
    """Get available languages"""
    return jsonify({
        'languages': LANGUAGES,
        'current': translator.get_current_language(),
        'default': DEFAULT_LANGUAGE
    })

# Update your existing chat endpoint to include language support
# (This would replace your existing chat endpoint)
@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """Enhanced chat API with multilingual support"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        sort_preference = data.get('sort_preference', 'rating')
        user_location = data.get('user_location')
        
        if not message:
            return jsonify({
                'error': translator.gettext('error_invalid_input')
            }), 400
        
        user_id = request.user['id']
        user_city = "Bangalore"  # You can make this dynamic
        
        # Get conversation history
        conversation_history = user_conversations.get(user_id, [])
        
        # Generate response with language context
        if medical_functions_available and medical_recommender:
            try:
                # Pass language context to the AI
                language = translator.get_current_language()
                response = medical_recommender.generate_response(
                    conversation_history, 
                    message, 
                    user_city=user_city,
                    sort_preference=sort_preference,
                    user_location=user_location,
                    language=language  # Add language parameter
                )
                
                # Translate system-generated parts if needed
                response = translator.translate_medical_response(response)
                
            except Exception as e:
                print(f"❌ Medical AI error: {e}")
                response = fallback_medical_response(
                    message, 
                    sort_preference, 
                    user_location, 
                    language=translator.get_current_language()
                )
        else:
            response = fallback_medical_response(
                message, 
                sort_preference, 
                user_location,
                language=translator.get_current_language()
            )
        
        # Save to conversation history and MongoDB
        user_conversations[user_id] = conversation_history + [(message, response)]
        
        # Save to MongoDB with language info
        chat_history_db.save_chat_message(
            user_id=user_id,
            message=message,
            response=response,
            metadata={'language': translator.get_current_language()}
        )
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        return jsonify({
            'error': translator.gettext('error_server')
        }), 500

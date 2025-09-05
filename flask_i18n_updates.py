# Add these updates to your main.py file

from i18n.translator import MedibotTranslator
from medical_translator import MedicalResponseTranslator

# Initialize translators
medibot_translator = MedibotTranslator()
medical_translator = MedicalResponseTranslator()

# Add language detection middleware
@app.before_request
def before_request():
    # Get language from session, query param, or Accept-Language header
    language = (
        session.get('language') or
        request.args.get('lang') or
        request.headers.get('Accept-Language', '').split(',')[0][:2] or
        'en'
    )
    
    # Set language in session
    session['language'] = language
    
    # Update translator language
    medibot_translator.set_language(language)
    medical_translator.set_language(language)

# Route to change language
@app.route('/api/set-language', methods=['POST'])
def set_language():
    try:
        data = request.get_json()
        language = data.get('language', 'en')
        
        # Validate language
        if language not in medibot_translator.get_available_languages():
            return jsonify({'error': 'Unsupported language'}), 400
        
        # Set in session
        session['language'] = language
        
        # Update translators
        medibot_translator.set_language(language)
        medical_translator.set_language(language)
        
        return jsonify({
            'success': True,
            'message': 'Language updated successfully',
            'language': language
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Updated chat route with translation support
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        sort_preference = data.get('sort_preference', 'rating')
        user_location = data.get('user_location')
        language = data.get('language', session.get('language', 'en'))
        
        # Set language for this request
        medibot_translator.set_language(language)
        medical_translator.set_language(language)
        
        if not user_message:
            return jsonify({
                'error': medibot_translator.get_text('error.invalid_input')
            }), 400
        
        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'error': medibot_translator.get_text('error.authentication_required')
            }), 401
        
        # Get user details
        db = DatabaseConnection()
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'error': medibot_translator.get_text('error.user_not_found')
            }), 404
        
        # Store user message in chat history
        chat_history_manager.add_message(user_id, user_message, 'user', language)
        
        try:
            from src.llm.recommender import get_medical_recommendations
            
            # Get recommendations with language context
            recommendations = get_medical_recommendations(
                user_message=user_message,
                user_location=user_location,
                sort_preference=sort_preference,
                user_id=user_id,
                language=language
            )
            
            # Translate the response
            translated_response = medical_translator.translate_response(recommendations)
            
            # Store bot response
            chat_history_manager.add_message(user_id, translated_response, 'bot', language)
            
            return jsonify({
                'response': translated_response,
                'language': language,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            error_message = f"{medibot_translator.get_text('error.processing')}: {str(e)}"
            chat_history_manager.add_message(user_id, error_message, 'bot', language)
            
            return jsonify({
                'response': error_message,
                'language': language
            })
    
    except Exception as e:
        return jsonify({
            'error': f"{medibot_translator.get_text('error.server')}: {str(e)}"
        }), 500

# Updated dashboard route with translation
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    language = session.get('language', 'en')
    medibot_translator.set_language(language)
    
    user_id = session['user_id']
    db = DatabaseConnection()
    user = db.get_user_by_id(user_id)
    
    if not user:
        flash(medibot_translator.get_text('error.user_not_found'), 'error')
        return redirect(url_for('login'))
    
    # Get translated data
    dashboard_data = {
        'user': user,
        'translations': medibot_translator.get_translations(),
        'current_language': language,
        'available_languages': medibot_translator.get_available_languages()
    }
    
    return render_template('dashboard.html', **dashboard_data)

# Updated chat page route
@app.route('/chat')
def chat_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    language = session.get('language', 'en')
    medibot_translator.set_language(language)
    
    user_id = session['user_id']
    
    # Get chat history with language context
    chat_history = chat_history_manager.get_chat_history(user_id)
    
    # Prepare translated data
    chat_data = {
        'chat_history': chat_history,
        'translations': medibot_translator.get_translations(),
        'current_language': language,
        'available_languages': medibot_translator.get_available_languages(),
        'user_id': user_id
    }
    
    return render_template('chat.html', **chat_data)

# Updated login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    language = session.get('language', 'en')
    medibot_translator.set_language(language)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash(medibot_translator.get_text('error.missing_credentials'), 'error')
            return render_template('login.html', 
                                 translations=medibot_translator.get_translations(),
                                 current_language=language)
        
        db = DatabaseConnection()
        user = db.authenticate_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(medibot_translator.get_text('auth.login_success'), 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(medibot_translator.get_text('error.invalid_credentials'), 'error')
    
    return render_template('login.html', 
                         translations=medibot_translator.get_translations(),
                         current_language=language,
                         available_languages=medibot_translator.get_available_languages())

# Updated register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    language = session.get('language', 'en')
    medibot_translator.set_language(language)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation with translated messages
        if not all([username, email, password, confirm_password]):
            flash(medibot_translator.get_text('error.missing_fields'), 'error')
        elif password != confirm_password:
            flash(medibot_translator.get_text('error.password_mismatch'), 'error')
        elif len(password) < 6:
            flash(medibot_translator.get_text('error.password_too_short'), 'error')
        else:
            db = DatabaseConnection()
            if db.create_user(username, email, password):
                flash(medibot_translator.get_text('auth.register_success'), 'success')
                return redirect(url_for('login'))
            else:
                flash(medibot_translator.get_text('error.user_exists'), 'error')
    
    return render_template('register.html', 
                         translations=medibot_translator.get_translations(),
                         current_language=language,
                         available_languages=medibot_translator.get_available_languages())

# Add API endpoint to get translations
@app.route('/api/translations')
def get_translations():
    language = request.args.get('lang', session.get('language', 'en'))
    medibot_translator.set_language(language)
    
    return jsonify({
        'translations': medibot_translator.get_translations(),
        'language': language,
        'available_languages': medibot_translator.get_available_languages()
    })

if __name__ == '__main__':
    app.run(debug=True)

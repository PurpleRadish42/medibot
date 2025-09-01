import sys
import os
from pathlib import Path
from functools import wraps
import threading
import time
import pymysql

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables.")
    print("To install: pip install python-dotenv")

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))  # Add project root for doctor_recommender

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
import gradio as gr

# Import authentication database
from medibot2_auth import MedibotAuthDatabase

# Import your medical recommender directly with doctor integration
medical_recommender = None
medical_functions_available = False

try:
    # Import your MedicalRecommender class (updated version with doctor integration)
    from src.llm.recommender import MedicalRecommender
    medical_recommender = MedicalRecommender()
    medical_functions_available = True
    print("✅ MedicalRecommender with doctor integration initialized successfully")
except ImportError as e:
    print(f"⚠ MedicalRecommender import failed: {e}")
    print("Using fallback medical responses")
except Exception as e:
    print(f"⚠ MedicalRecommender initialization failed: {e}")
    print("Using fallback medical responses")

# Your existing imports with error handling
gradio_available = False

try:
    from ui.gradio_app import launch_app  # Your existing Gradio app
    gradio_available = True
    print("✅ Gradio app import successful")
except ImportError as e:
    print(f"⚠ Gradio app import failed: {e}")
    print("Gradio interface will not be available")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Initialize authentication database
auth_db = MedibotAuthDatabase()

# Store conversation histories for each user
user_conversations = {}

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session token
        session_token = request.cookies.get('session_token')
        if not session_token:
            return redirect(url_for('login'))
        
        # Verify session
        user_data = auth_db.verify_session(session_token)
        if not user_data:
            # Invalid session, redirect to login
            response = make_response(redirect(url_for('login')))
            response.set_cookie('session_token', '', expires=0)
            return response
        
        # Store user data in request context
        request.user = user_data
        return f(*args, **kwargs)
    return decorated_function

# Fallback medical response function
def fallback_medical_response(message):
    """Fallback response when medical AI is not available"""
    responses = {
        "hello": "Hello! I'm your medical assistant. How can I help you today?",
        "headache": "For headaches, try resting in a quiet, dark room, staying hydrated, and applying a cold compress. If headaches persist or are severe, please consult a healthcare professional.",
        "fever": "For fever, rest, stay hydrated, and consider over-the-counter fever reducers if appropriate. Seek medical attention if fever is high (over 103°F/39.4°C) or persists.",
        "default": "I'm here to help with medical questions. However, the AI medical system is currently unavailable. For urgent medical concerns, please contact your healthcare provider or emergency services."
    }
    
    message_lower = message.lower()
    if "hello" in message_lower or "hi" in message_lower:
        return responses["hello"]
    elif "headache" in message_lower or "head" in message_lower:
        return responses["headache"]
    elif "fever" in message_lower or "temperature" in message_lower:
        return responses["fever"]
    else:
        return responses["default"]

# Authentication Routes
@app.route('/')
def index():
    """Landing page - redirect based on authentication status"""
    session_token = request.cookies.get('session_token')
    if session_token and auth_db.verify_session(session_token):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Login page"""
    # If already logged in, redirect to dashboard
    session_token = request.cookies.get('session_token')
    if session_token and auth_db.verify_session(session_token):
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register')
def register():
    """Registration page"""
    # If already logged in, redirect to dashboard
    session_token = request.cookies.get('session_token')
    if session_token and auth_db.verify_session(session_token):
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    """Handle user registration"""
    try:
        data = request.get_json()
        
        # Extract data
        full_name = data.get('fullName', '').strip()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate required fields
        if not all([full_name, username, email, password]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Register user
        success, message = auth_db.register_user(username, email, password, full_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
    try:
        data = request.get_json()
        
        # Extract data
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        # Validate required fields
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Authenticate user
        success, message, user_data = auth_db.authenticate_user(username, password)
        
        if success:
            # Create session
            session_token = auth_db.create_session(user_data['id'])
            
            if session_token:
                response = make_response(jsonify({
                    'success': True,
                    'message': message,
                    'user': {
                        'username': user_data['username'],
                        'email': user_data['email'],
                        'full_name': user_data['full_name']
                    }
                }))
                
                # Set session cookie
                max_age = 7 * 24 * 60 * 60 if remember_me else None  # 7 days if remember me
                response.set_cookie(
                    'session_token', 
                    session_token, 
                    max_age=max_age,
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite='Lax'
                )
                
                return response
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create session'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/logout')
def logout():
    """Handle user logout"""
    session_token = request.cookies.get('session_token')
    if session_token:
        auth_db.logout_user(session_token)
        # Clear user conversation when logging out
        user_id = request.user.get('id') if hasattr(request, 'user') else None
        if user_id and user_id in user_conversations:
            del user_conversations[user_id]
    
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session_token', '', expires=0)
    return response

# Protected Routes (require authentication)
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - updated homepage for authenticated users"""
    return render_template('dashboard.html', user=request.user)

@app.route('/chat')
@login_required
def chat_page():
    """Custom chat interface page"""
    return render_template('chat.html', user=request.user)

# API Routes (require authentication) - FIXED WITH PROPER RESET
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """API endpoint for custom chat interface - WITH DOCTOR RECOMMENDATIONS"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_city = data.get('city', None)  # Optional: get user's city for better recommendations
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        user_id = request.user['id']
        
        print(f"💬 Chat request from user {user_id}: {message[:50]}...")
        
        # Initialize conversation history for this user if not exists
        if user_id not in user_conversations:
            user_conversations[user_id] = []
            print(f"📝 Created new conversation for user {user_id}")
        
        # Get conversation history for this user
        conversation_history = user_conversations[user_id]
        
        # Use your MedicalRecommender with proper conversation history and doctor recommendations
        if medical_functions_available and medical_recommender:
            try:
                print(f"🤖 Using MedicalRecommender with {len(conversation_history)} previous messages")
                
                # IMPORTANT: Pass the conversation history correctly
                # The recommender needs the full history to maintain context
                response = medical_recommender.generate_response(
                    conversation_history, 
                    message, 
                    user_city=user_city or "Mumbai"  # Default city if not provided
                )
                
                print(f"✅ Got AI response: {response[:100]}...")
                
                # Add this exchange to the conversation history
                user_conversations[user_id].append((message, response))
                
                # Keep only last 20 exchanges to prevent memory issues
                if len(user_conversations[user_id]) > 20:
                    user_conversations[user_id] = user_conversations[user_id][-20:]
                    print("🧹 Trimmed conversation history to last 20 exchanges")
                
            except Exception as e:
                print(f"❌ Medical AI error: {e}")
                import traceback
                traceback.print_exc()
                response = fallback_medical_response(message)
        else:
            print("⚠ Using fallback response - MedicalRecommender not available")
            response = fallback_medical_response(message)
        
        # Save chat to database
        try:
            # Get session token for saving chat with conversation tracking
            session_token = request.cookies.get('session_token')
            auth_db.save_chat_message(user_id, message, response, session_token=session_token)
            print("💾 Chat saved to database")
        except Exception as e:
            print(f"⚠ Failed to save chat to database: {e}")
        
        # EHR Integration: Check if message contains symptoms and save them
        try:
            # Simple symptom detection - check if message talks about health issues
            symptom_indicators = [
                'feel', 'pain', 'hurt', 'ache', 'sick', 'ill', 'symptom', 'problem',
                'headache', 'fever', 'cough', 'cold', 'tired', 'weak', 'dizzy',
                'nausea', 'vomit', 'stomach', 'chest', 'throat', 'back', 'neck'
            ]
            
            message_lower = message.lower()
            if any(indicator in message_lower for indicator in symptom_indicators):
                print(f"🏥 Detected potential symptoms in message: {message[:50]}...")
                
                # Extract keywords and save symptoms
                keywords = auth_db.extract_symptom_keywords(message)
                if keywords:  # Only save if we found relevant keywords
                    conversation_id = session_token or f"user-{user_id}-{int(time.time())}"
                    
                    symptom_id = auth_db.save_patient_symptoms(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        symptoms_text=message,
                        keywords=keywords
                    )
                    
                    if symptom_id:
                        # Check for similar historical symptoms
                        similar_symptoms = auth_db.find_similar_symptoms(user_id, message)
                        if similar_symptoms:
                            print(f"🔍 Found {len(similar_symptoms)} similar historical symptoms")
                        
        except Exception as e:
            print(f"⚠ EHR integration error: {e}")
        
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"❌ API Error in /api/chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/reset', methods=['POST'])
@login_required
def api_reset():
    """API endpoint to reset conversation - PROPERLY FIXED"""
    try:
        user_id = request.user['id']
        
        print(f"🔄 Resetting conversation for user {user_id}")
        
        # 1. Clear the conversation history for this user in memory
        if user_id in user_conversations:
            del user_conversations[user_id]
            print(f"✅ Cleared memory conversation for user {user_id}")
        
        # 2. Re-initialize empty conversation for the user
        user_conversations[user_id] = []
        print(f"✅ Re-initialized empty conversation for user {user_id}")
        
        # 3. Reset the MedicalRecommender instance if needed
        global medical_recommender
        if medical_functions_available:
            try:
                # Option 1: If your MedicalRecommender has a reset method
                if hasattr(medical_recommender, 'reset_conversation'):
                    medical_recommender.reset_conversation()
                    print("✅ Called reset_conversation method")
                
                # Option 2: Create a fresh instance (more reliable)
                # This ensures complete reset of any internal state
                from src.llm.recommender import MedicalRecommender
                medical_recommender = MedicalRecommender()
                print("✅ Created fresh MedicalRecommender instance")
                
            except Exception as e:
                print(f"⚠ Could not reset MedicalRecommender: {e}")
                # Continue anyway - the empty conversation history should be enough
        
        print("✅ Conversation reset completed successfully")
        
        return jsonify({
            'success': True,
            'message': 'Conversation reset successfully',
            'user_id': user_id,
            'conversation_cleared': True,
            'recommender_reset': medical_functions_available
        })
        
    except Exception as e:
        print(f"❌ Reset Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to reset conversation: {str(e)}'
        }), 500

# NEW ROUTE: Send doctor recommendations via email
@app.route('/api/send-email', methods=['POST'])
@login_required
def api_send_email():
    """Send doctor recommendations via email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        doctor_html = data.get('doctor_html', '').strip()
        user_query = data.get('user_query', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email address is required'
            }), 400
            
        if not doctor_html:
            return jsonify({
                'success': False,
                'message': 'Doctor recommendations data is required'
            }), 400
        
        # Import and use email service
        from email_service import EmailService
        email_service = EmailService()
        
        # Send email
        success = email_service.send_doctor_recommendations(
            to_email=email,
            doctor_table_html=doctor_html,
            user_query=user_query
        )
        
        if success:
            user_id = request.user['id']
            print(f"✅ Email sent successfully to {email} for user {user_id}")
            return jsonify({
                'success': True,
                'message': f'Doctor recommendations sent successfully to {email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send email. Please check your email address and try again.'
            }), 500
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'An error occurred while sending the email'
        }), 500

# NEW ROUTE: Update user city for better doctor recommendations
@app.route('/api/user/city', methods=['POST'])
@login_required
def api_update_user_city():
    """Update user's city for better doctor recommendations"""
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        
        if city:
            # You can save this to user profile in database if needed
            user_id = request.user['id']
            print(f"🏙️ User {user_id} set city to: {city}")
            
            # For now, we'll just return success
            # In future, you could save this to the users table
            return jsonify({
                'success': True,
                'message': f'City updated to {city}',
                'city': city
            })
        else:
            return jsonify({
                'success': False,
                'message': 'City name is required'
            }), 400
            
    except Exception as e:
        print(f"❌ City update error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# NEW ROUTE: Get doctor database statistics
@app.route('/api/doctors/stats')
@login_required
def api_doctor_stats():
    """Get statistics about the doctor database"""
    try:
        if medical_functions_available and medical_recommender and medical_recommender.doctor_recommender:
            stats = medical_recommender.doctor_recommender.get_statistics()
            return jsonify({
                'success': True,
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Doctor database not available'
            })
            
    except Exception as e:
        print(f"❌ Doctor stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat-history')
@login_required
def api_chat_history():
    """Get user's chat history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = auth_db.get_chat_history(request.user['id'], limit)
        
        # Format history for frontend
        formatted_history = []
        for message, response, timestamp in history:
            formatted_history.append({
                'message': message,
                'response': response,
                'timestamp': timestamp
            })
        
        return jsonify({
            'success': True,
            'history': formatted_history
        })
    except Exception as e:
        print(f"Chat history error: {e}")
        return jsonify({'error': 'Failed to retrieve chat history'}), 500

@app.route('/api/user')
@login_required
def api_user():
    """Get current user information"""
    return jsonify({
        'success': True,
        'user': request.user
    })

@app.route('/api/status')
def api_status():
    """Check system status including doctor database"""
    doctor_db_available = False
    total_doctors = 0
    
    if medical_functions_available and medical_recommender:
        try:
            if hasattr(medical_recommender, 'doctor_recommender') and medical_recommender.doctor_recommender:
                doctor_db_available = True
                stats = medical_recommender.doctor_recommender.get_statistics()
                total_doctors = stats.get('total_doctors', 0)
        except:
            pass
    
    return jsonify({
        'status': 'online',
        'gradio_available': gradio_available,
        'medical_ai_available': medical_functions_available,
        'doctor_database_available': doctor_db_available,
        'total_doctors': total_doctors,
        'openai_key_set': bool(os.getenv('OPENAI_API_KEY'))
    })

# Chat history management routes
@app.route('/api/chat-history/clear', methods=['DELETE'])
@login_required
def api_clear_chat_history():
    """Clear all chat history for the current user"""
    try:
        user_id = request.user['id']
        
        # Clear from database using the new method
        deleted_count = auth_db.clear_all_user_chats(user_id)
        
        # Clear from memory conversation
        if user_id in user_conversations:
            del user_conversations[user_id]
        
        return jsonify({
            'success': True, 
            'message': f'Deleted {deleted_count} chat messages',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"Clear chat history error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# New conversation management API endpoints
@app.route('/api/conversations', methods=['GET'])
@login_required
def api_get_conversations():
    """Get user's conversations"""
    try:
        conversations = auth_db.get_user_conversations(request.user['id'])
        return jsonify({
            'success': True,
            'conversations': conversations
        })
    except Exception as e:
        print(f"Get conversations error: {e}")
        return jsonify({'error': 'Failed to retrieve conversations'}), 500

@app.route('/api/conversation/<conversation_id>/messages', methods=['GET'])
@login_required
def api_get_conversation_messages(conversation_id):
    """Get messages in a specific conversation"""
    try:
        messages = auth_db.get_conversation_messages(conversation_id, request.user['id'])
        return jsonify({
            'success': True,
            'messages': messages,
            'conversation_id': conversation_id
        })
    except Exception as e:
        print(f"Get conversation messages error: {e}")
        return jsonify({'error': 'Failed to retrieve conversation messages'}), 500

@app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
@login_required
def api_delete_conversation(conversation_id):
    """Delete a specific conversation"""
    try:
        success = auth_db.delete_conversation(conversation_id, request.user['id'])
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete conversation'}), 500
            
    except Exception as e:
        print(f"Delete conversation error: {e}")
        return jsonify({'error': 'Failed to delete conversation'}), 500

# Updated clear all chats to use the new method
@app.route('/api/chat-history/clear-all', methods=['DELETE'])
@login_required
def api_clear_all_chats():
    """Clear all chat history for the current user - Enhanced version"""
    try:
        user_id = request.user['id']
        
        # Use the new clear method
        deleted_count = auth_db.clear_all_user_chats(user_id)
        
        # Clear from memory conversation
        if user_id in user_conversations:
            del user_conversations[user_id]
        
        return jsonify({
            'success': True, 
            'message': f'Deleted {deleted_count} chat messages',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"Clear all chats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# EHR (Electronic Health Record) API endpoints
@app.route('/api/ehr/symptoms', methods=['POST'])
@login_required
def api_save_symptoms():
    """Save patient symptoms to EHR system"""
    try:
        data = request.get_json()
        user_id = request.user['id']
        
        symptoms_text = data.get('symptoms', '').strip()
        conversation_id = data.get('conversation_id', '')
        
        if not symptoms_text:
            return jsonify({'success': False, 'error': 'Symptoms text is required'}), 400
        
        # Extract keywords and determine category
        keywords = auth_db.extract_symptom_keywords(symptoms_text)
        
        # Simple severity detection based on keywords
        severity = 'mild'
        urgent_words = ['severe', 'extreme', 'unbearable', 'emergency', 'urgent', 'blood', 'chest pain']
        if any(word in symptoms_text.lower() for word in urgent_words):
            severity = 'severe'
        elif any(word in symptoms_text.lower() for word in ['moderate', 'bad', 'worse', 'painful']):
            severity = 'moderate'
        
        # Save symptoms
        symptom_id = auth_db.save_patient_symptoms(
            user_id=user_id,
            conversation_id=conversation_id,
            symptoms_text=symptoms_text,
            keywords=keywords,
            severity=severity
        )
        
        if symptom_id:
            # Check for similar historical symptoms
            similar_symptoms = auth_db.find_similar_symptoms(user_id, symptoms_text)
            
            return jsonify({
                'success': True,
                'symptom_id': symptom_id,
                'keywords': keywords,
                'severity': severity,
                'similar_symptoms': similar_symptoms[:3]  # Return top 3 similar
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save symptoms'}), 500
        
    except Exception as e:
        print(f"Save symptoms API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ehr/symptoms')
@login_required
def api_get_symptoms():
    """Get patient's symptom history"""
    try:
        user_id = request.user['id']
        limit = request.args.get('limit', 20, type=int)
        
        symptoms = auth_db.get_patient_symptoms(user_id, limit)
        
        return jsonify({
            'success': True,
            'symptoms': symptoms,
            'count': len(symptoms)
        })
        
    except Exception as e:
        print(f"Get symptoms API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ehr/symptoms/similar', methods=['POST'])
@login_required
def api_find_similar_symptoms():
    """Find similar symptoms in patient's history"""
    try:
        data = request.get_json()
        user_id = request.user['id']
        
        current_symptoms = data.get('symptoms', '').strip()
        threshold = data.get('threshold', 0.5)
        
        if not current_symptoms:
            return jsonify({'success': False, 'error': 'Symptoms text is required'}), 400
        
        similar_symptoms = auth_db.find_similar_symptoms(user_id, current_symptoms, threshold)
        
        return jsonify({
            'success': True,
            'similar_symptoms': similar_symptoms,
            'count': len(similar_symptoms)
        })
        
    except Exception as e:
        print(f"Find similar symptoms API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# SKIN ANALYZER ROUTES
@app.route('/skin-analyzer')
@login_required
def skin_analyzer():
    """Skin condition analyzer page"""
    return render_template('skin_analyzer.html')

@app.route('/api/v1/analyze-skin', methods=['POST'])
@login_required
def api_analyze_skin():
    """API endpoint for skin condition analysis"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No image file selected'
            }), 400
        
        # Read image data
        image_data = image_file.read()
        
        # Get user city from form data if provided
        user_city = request.form.get('city', None)
        
        print(f"🔬 Analyzing skin image for user {request.user['id']}")
        print(f"   Image size: {len(image_data)} bytes")
        print(f"   User city: {user_city}")
        
        # Import and use skin analyzer
        try:
            from src.ai.skin_analyzer import analyze_skin_image
            result = analyze_skin_image(image_data, user_city)
            
            if result['success']:
                print(f"✅ Skin analysis completed successfully")
                print(f"   Found {len(result['analysis']['conditions'])} potential conditions")
                print(f"   Recommended specialist: {result['analysis']['specialist_type']}")
                print(f"   Found {len(result['analysis']['doctors'])} doctors")
                
                return jsonify(result)
            else:
                print(f"❌ Skin analysis failed: {result.get('error', 'Unknown error')}")
                return jsonify(result), 400
                
        except ImportError as e:
            print(f"❌ Skin analyzer import error: {e}")
            return jsonify({
                'success': False,
                'message': 'Skin analyzer not available'
            }), 500
        except Exception as e:
            print(f"❌ Skin analysis error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }), 500
    
    except Exception as e:
        print(f"❌ API Error in /api/v1/analyze-skin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

def run_gradio():
    """Run Gradio in a separate thread"""
    if gradio_available:
        try:
            launch_app()  # Your existing function
            print("✅ Gradio interface started successfully")
        except Exception as e:
            print(f"⚠ Could not launch Gradio app: {e}")
    else:
        print("⚠ Gradio interface not available due to import errors")

def create_templates_directory():
    """Create templates directory if it doesn't exist"""
    templates_dir = project_root / "templates"
    if not templates_dir.exists():
        templates_dir.mkdir()
        print(f"Created templates directory: {templates_dir}")

def create_dashboard_template():
    """Create a basic dashboard template if it doesn't exist - FIXED Unicode Error"""
    templates_dir = project_root / "templates"
    dashboard_file = templates_dir / "dashboard.html"
    
    if not dashboard_file.exists():
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - MedBot AI</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; margin-bottom: 3rem; }
        .header h1 { font-size: 3rem; margin-bottom: 1rem; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .feature-card { background: rgba(255, 255, 255, 0.1); padding: 2rem; border-radius: 15px; text-align: center; cursor: pointer; transition: transform 0.3s ease; }
        .feature-card:hover { transform: translateY(-5px); }
        .feature-icon { font-size: 3rem; margin-bottom: 1rem; color: #4facfe; }
        .btn { padding: 1rem 2rem; background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; text-decoration: none; border-radius: 25px; display: inline-block; margin: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome, {{ user.full_name }}!</h1>
            <p>Your AI medical assistant with doctor recommendations</p>
            <a href="/chat" class="btn"><i class="fas fa-comments"></i> Start Chat</a>
            <a href="/logout" class="btn" style="background: #ef4444;"><i class="fas fa-sign-out-alt"></i> Logout</a>
        </div>
        <div class="features-grid">
            <div class="feature-card" onclick="window.location.href='/chat'">
                <div class="feature-icon"><i class="fas fa-comments"></i></div>
                <h3>Chat with AI Doctor</h3>
                <p>Get medical guidance and real doctor recommendations</p>
            </div>
            <div class="feature-card" onclick="checkSystemStatus()">
                <div class="feature-icon"><i class="fas fa-heartbeat"></i></div>
                <h3>System Status</h3>
                <p>Check AI and doctor database status</p>
            </div>
            <div class="feature-card" onclick="window.location.href='/logout'">
                <div class="feature-icon"><i class="fas fa-sign-out-alt"></i></div>
                <h3>Sign Out</h3>
                <p>Securely log out of your account</p>
            </div>
        </div>
    </div>
    <script>
        async function checkSystemStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                let status = `System Status:\\n\\n`;
                status += `Medical AI: ${data.medical_ai_available ? '✅ Available' : '❌ Unavailable'}\\n`;
                status += `Doctor Database: ${data.doctor_database_available ? '✅ Available' : '❌ Unavailable'}\\n`;
                status += `Total Doctors: ${data.total_doctors}\\n`;
                status += `OpenAI: ${data.openai_key_set ? '✅ Connected' : '❌ Not Connected'}`;
                alert(status);
            } catch (error) { alert('Error checking status'); }
        }
    </script>
</body>
</html>'''
        
        # FIXED: Use UTF-8 encoding explicitly to handle Unicode characters
        try:
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            print(f"✅ Created dashboard template with UTF-8 encoding")
        except Exception as e:
            print(f"⚠ Error creating dashboard template: {e}")

def check_openai_setup():
    """Check if OpenAI is properly configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n⚠ WARNING: OpenAI API key not found!")
        print("To fix this:")
        print("1. Create a .env file in your project root")
        print("2. Add: OPENAI_API_KEY=your_api_key_here")
        print("3. Or set the environment variable: set OPENAI_API_KEY=your_key")
        print("4. Install python-dotenv: pip install python-dotenv")
        print("\nThe app will still work with fallback responses.\n")
        return False
    else:
        print(f"✅ OpenAI API key found: {api_key[:8]}...")
        return True

def check_doctor_database():
    """Check if doctor database is loaded"""
    if medical_functions_available and medical_recommender:
        try:
            if hasattr(medical_recommender, 'doctor_recommender') and medical_recommender.doctor_recommender:
                stats = medical_recommender.doctor_recommender.get_statistics()
                total_doctors = stats.get('total_doctors', 0)
                total_cities = stats.get('total_cities', 0)
                print(f"✅ Doctor database loaded: {total_doctors} doctors in {total_cities} cities")
                return True
        except Exception as e:
            print(f"⚠ Doctor database error: {e}")
            return False
    else:
        print("⚠ Doctor database not available")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🏥 STARTING MEDICAL CHATBOT WITH MEDIBOT2 DATABASE")
    print("=" * 70)
    print(f"Project root: {project_root}")
    print(f"Source path: {src_path}")
    print(f"Database: medibot2 (MySQL)")
    
    # Check OpenAI setup
    openai_ok = check_openai_setup()
    
    # Check doctor database
    doctor_db_ok = check_doctor_database()
    
    # Create templates directory if needed
    create_templates_directory()
    create_dashboard_template()
    
    # Initialize database
    print("Initializing medibot2 authentication database...")
    # The database initialization is handled automatically in MedibotAuthDatabase __init__
    
    # Run Flask app
    print("\n" + "=" * 70)
    print("🚀 FLASK WEB SERVER STARTING")
    print("=" * 70)
    print("✅ Features Available:")
    print(f"  📱 Authentication System: ✅ Ready (medibot2 MySQL)")
    print(f"  🤖 Medical AI: {'✅ Ready' if openai_ok else '⚠ Limited'}")
    print(f"  🏥 Doctor Database: {'✅ Ready' if doctor_db_ok else '⚠ Unavailable'}")
    print(f"  🗄️  Database: medibot2 (MySQL)")
    print("\n🌐 Access URLs:")
    print("  📱 Main app: http://localhost:5000")
    print("  🔐 Login: http://localhost:5000/login")
    print("  📝 Register: http://localhost:5000/register")
    print("  💬 Chat (after login): http://localhost:5000/chat")
    print("=" * 70)
    
    app.run(debug=True, port=5000, use_reloader=False)
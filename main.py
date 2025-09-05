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
from datetime import datetime

# Import authentication database and MongoDB chat history
from medibot2_auth import MedibotAuthDatabase
from mongodb_chat import MongoDBChatHistory

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

# Initialize authentication database (MySQL) and chat history (MongoDB)
auth_db = MedibotAuthDatabase()
chat_history_db = MongoDBChatHistory()

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
def fallback_medical_response(message, sort_preference="rating", user_location=None):
    """Fallback response when medical AI is not available - WITH DOCTOR RECOMMENDATIONS"""
    
    # Try to provide doctor recommendations even without OpenAI
    try:
        # Import doctor recommender
        from doctor_recommender import DoctorRecommender
        dr = DoctorRecommender()
        
        # Simple symptom to specialist mapping for fallback
        symptom_specialist_map = {
            "headache": "neurologist",
            "head": "neurologist", 
            "migraine": "neurologist",
            "chest": "cardiologist",
            "heart": "cardiologist",
            "stomach": "gastroenterologist",
            "digestive": "gastroenterologist",
            "skin": "dermatologist",
            "rash": "dermatologist",
            "eye": "ophthalmologist",
            "vision": "ophthalmologist",
            "joint": "orthopedist",
            "bone": "orthopedist",
            "hand": "orthopedist",
            "elbow": "orthopedist",
            "arm": "orthopedist",
            "wrist": "orthopedist",
            "shoulder": "orthopedist",
            "knee": "orthopedist",
            "ankle": "orthopedist",
            "back": "orthopedist",
            "neck": "orthopedist",
            "spine": "orthopedist",
            "fracture": "orthopedist",
            "sprain": "orthopedist",
            "accident": "orthopedist",
            "injury": "orthopedist",
            "fell": "orthopedist",
            "pain": "general-physician",
            "fever": "general-physician",
            "cold": "general-physician",
            "cough": "pulmonologist",
            "breathing": "pulmonologist"
        }
        
        # Find matching specialist
        message_lower = message.lower()
        recommended_specialist = None
        
        for symptom, specialist in symptom_specialist_map.items():
            if symptom in message_lower:
                recommended_specialist = specialist
                break
        
        if recommended_specialist:
            # Prepare location parameters
            user_lat = None
            user_lng = None
            if user_location:
                user_lat = user_location.get('latitude')
                user_lng = user_location.get('longitude')
                
            # Get doctor recommendations with enhanced parameters
            doctors = dr.recommend_doctors(
                recommended_specialist, 
                "Bangalore", 
                limit=3, 
                sort_by=sort_preference,
                user_lat=user_lat,
                user_lng=user_lng
            )
            if doctors:
                # Format as HTML with table
                specialist_name = recommended_specialist.replace("_", " ").title()
                response = f"<p>I understand you're having {message.lower()}. Let me help you find the right specialist for your condition.</p>\n"
                response += f"<p>Based on your symptoms, I recommend consulting a <strong>{specialist_name}</strong>.</p>\n"
                response += dr.format_doctor_recommendations(doctors, specialist_name)
                return response
        
        # No specialist match found
        user_lat = None
        user_lng = None
        if user_location:
            user_lat = user_location.get('latitude')
            user_lng = user_location.get('longitude')
            
        doctors = dr.recommend_doctors(
            "general physician", 
            "Bangalore", 
            limit=2, 
            sort_by=sort_preference,
            user_lat=user_lat,
            user_lng=user_lng
        )
        if doctors:
            response = "<p>I can help you find medical care for your condition.</p>\n"
            response += "<p>For your symptoms, I recommend starting with a <strong>General Physician</strong> who can evaluate your condition and refer you to a specialist if needed.</p>\n"
            response += dr.format_doctor_recommendations(doctors, "General Physician")
            return response
            
    except Exception as e:
        print(f"⚠ Fallback doctor recommendation failed: {e}")
    
    # Final fallback without doctor recommendations
    responses = {
        "hello": "Hello! I'm your medical assistant. How can I help you today?",
        "headache": "For headaches, try resting in a quiet, dark room, staying hydrated, and applying a cold compress. If headaches persist or are severe, please consult a healthcare professional.",
        "fever": "For fever, rest, stay hydrated, and consider over-the-counter fever reducers if appropriate. Seek medical attention if fever is high (over 103°F/39.4°C) or persists.",
        "default": "I'm here to help with medical questions. For urgent medical concerns, please contact your healthcare provider or emergency services."
    }
    
    message_lower = message.lower()
    if "hello" in message_lower or "hi" in message_lower:
        return responses["hello"]
    elif "headache" in message_lower or "head" in message_lower:
        return responses["headache"]
    elif "fever" in message_lower or "temperature" in message_lower:
        return responses["fever"]
    else:
        # If no specific keywords found, show general physician recommendations
        try:
            from doctor_recommender import DoctorRecommender
            dr = DoctorRecommender()
            doctors = dr.recommend_doctors("general physician", "Bangalore", limit=2)
            if doctors:
                response = "<p>I understand you have medical concerns. While our AI assistant is temporarily unavailable, I can help you find medical care.</p>\n"
                response += "<p>I recommend starting with a <strong>General Physician</strong> who can evaluate your condition and refer you to a specialist if needed.</p>\n"
                response += dr.format_doctor_recommendations(doctors, "General Physician")
                return response
        except Exception as e:
            print(f"⚠ General physician recommendation failed: {e}")
        
        return responses["default"]

# Simple test endpoint without authentication
@app.route('/api/test-chat', methods=['POST'])
def api_test_chat():
    """Simple test endpoint to verify doctor recommendations work"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"🧪 TEST: Processing message: {message}")
        
        # Use fallback response (since OpenAI is not configured)
        response = fallback_medical_response(message)
        
        print(f"🧪 TEST: Generated response of {len(response)} characters")
        print(f"🧪 TEST: Contains table: {'<table' in response}")
        print(f"🧪 TEST: Contains Important Notes: {'Important Notes:' in response}")
        
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# Test page for verifying fixes
@app.route('/test-fixes')
def test_fixes():
    """Test page to verify both fixes work properly"""
    from flask import send_from_directory
    return send_from_directory('static', 'test_fixes.html')

# Test chat interface
@app.route('/test-chat-interface')
def test_chat_interface():
    """Test page for doctor recommendations"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_chat_interface.html')

# Doctor recommendations test page
@app.route('/doctor-test')
def doctor_test():
    """Test page for doctor recommendations without authentication"""
    from flask import send_from_directory
    return send_from_directory('static', 'doctor_test.html')

# Direct test page
@app.route('/test-direct')
def test_direct():
    """Direct test page for debugging"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_direct.html')

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
    """API endpoint for custom chat interface - WITH ENHANCED DOCTOR RECOMMENDATIONS"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_city = data.get('city', None)  # Optional: get user's city for better recommendations
        sort_preference = data.get('sortPreference', 'rating')  # New: sorting preference
        user_location = data.get('userLocation', None)  # New: user's GPS location
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        user_id = request.user['id']
        
        print(f"💬 Chat request from user {user_id}: {message[:50]}...")
        print(f"📍 User location: {user_location}")
        print(f"🔄 Sort preference: {sort_preference}")
        
        # Initialize conversation history for this user if not exists
        if user_id not in user_conversations:
            user_conversations[user_id] = []
            print(f"📝 Created new conversation for user {user_id}")
        
        # Get conversation history for this user
        conversation_history = user_conversations[user_id]
        
        # Use MedicalRecommender for AI chat, with fallback for doctor recommendations
        if medical_functions_available and medical_recommender:
            try:
                print(f"🤖 Using MedicalRecommender with {len(conversation_history)} previous messages")
                
                # Get AI response from MedicalRecommender with enhanced parameters
                response = medical_recommender.generate_response(
                    conversation_history, 
                    message, 
                    user_city=user_city or "Bangalore",
                    sort_preference=sort_preference,
                    user_location=user_location
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
                print("🔄 Falling back to doctor recommendations system")
                response = fallback_medical_response(message, sort_preference, user_location)
                user_conversations[user_id].append((message, response))
        else:
            print("⚠ MedicalRecommender not available, using fallback system")
            response = fallback_medical_response(message, sort_preference, user_location)
            user_conversations[user_id].append((message, response))
        
        print(f"✅ Generated response: {response[:100]}...")
        
        # Save chat to MongoDB
        try:
            # Get session token for conversation tracking  
            session_token = request.cookies.get('session_token')
            
            # Get conversation_id from user session if available
            conversation_id = None
            if session_token:
                user_session = auth_db.verify_session(session_token)
                if user_session:
                    conversation_id = user_session.get('conversation_id')
            
            chat_history_db.save_chat_message(user_id, message, response, conversation_id, session_token)
            print("💾 Chat saved to MongoDB")
        except Exception as e:
            print(f"⚠ Failed to save chat to MongoDB: {e}")
        
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
                    # Generate conversation_id based on session token and current time
                    session_token = request.cookies.get('session_token', '')
                    conversation_id = f"conv-{session_token[-8:] if session_token else 'anon'}-{int(time.time() // 3600)}"  # Hour-based conversation grouping
                    
                    symptom_id = auth_db.save_patient_symptoms(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        symptoms_text=message,
                        keywords=keywords
                    )
                    
                    if symptom_id:
                        print(f"✅ Symptoms saved with ID: {symptom_id}")
                        # Check for similar historical symptoms
                        similar_symptoms = auth_db.find_similar_symptoms(user_id, message)
                        if similar_symptoms:
                            print(f"🔍 Found {len(similar_symptoms)} similar historical symptoms")
                    else:
                        print("❌ Failed to save symptoms to database")
                else:
                    print("ℹ️ No specific medical keywords found, symptoms not saved")
                        
        except Exception as e:
            print(f"⚠ EHR integration error: {e}")
            import traceback
            traceback.print_exc()
        
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
    """Get user's chat history from MongoDB"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = chat_history_db.get_chat_history(request.user['id'], limit)
        
        # Format history for frontend
        formatted_history = []
        for message, response, timestamp in history:
            # Convert timestamp to string if it's a datetime object
            timestamp_str = timestamp
            if hasattr(timestamp, 'isoformat'):
                timestamp_str = timestamp.isoformat()
            
            formatted_history.append({
                'message': message,
                'response': response,
                'timestamp': timestamp_str
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
        
        # Clear from MongoDB
        deleted_count = chat_history_db.clear_all_user_chats(user_id)
        
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



# Updated clear all chats to use the new method
@app.route('/api/chat-history/clear-all', methods=['DELETE'])
@login_required
def api_clear_all_chats():
    """Clear all chat history for the current user - Enhanced version"""
    try:
        user_id = request.user['id']
        
        # Use MongoDB clear method
        deleted_count = chat_history_db.clear_all_user_chats(user_id)
        
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
    """Enhanced API endpoint for medical image analysis"""
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
        
        # Get additional parameters
        user_city = request.form.get('city', None)
        image_type = request.form.get('image_type', None)
        context = request.form.get('context', None)
        symptoms = request.form.get('symptoms', '')
        specialty = request.form.get('specialty', None)
        
        print(f"🔬 Analyzing medical image for user {request.user['id']}")
        print(f"   Image size: {len(image_data)} bytes")
        print(f"   Image type: {image_type}")
        print(f"   Context: {context}")
        print(f"   Symptoms: {symptoms}")
        print(f"   Requested specialty: {specialty}")
        print(f"   User city: {user_city}")
        
        # FAST Analysis Pipeline - Optimized for Presentations
        analysis_results = {}
        
        # 1. Image type detection using router
        try:
            from src.ai.medical_image_router import route_medical_image
            routing_result = route_medical_image(image_data, image_type, symptoms)
            
            if routing_result['success']:
                detected_type = routing_result['image_type']
                detection_confidence = routing_result['confidence']
                analysis_results['routing'] = routing_result
                print(f"✅ Image type detected: {detected_type} (confidence: {detection_confidence}%)")
            else:
                detected_type = image_type or 'unknown'
                detection_confidence = 50
                print(f"⚠️ Image type detection failed, using: {detected_type}")
                
        except Exception as e:
            print(f"❌ Image routing failed: {e}")
            detected_type = image_type or 'skin'  # Default to skin
            detection_confidence = 30
        
        # 2. FAST Medical AI Analysis (PRIMARY - for presentations)
        try:
            from src.ai.fast_medical_ai import analyze_medical_image_fast
            fast_result = analyze_medical_image_fast(
                image_data, detected_type, symptoms, context
            )
            analysis_results['fast_medical_ai'] = fast_result
            print(f"✅ Fast Medical AI analysis completed in {fast_result.get('processing_time_ms', 0)}ms")
            
        except Exception as e:
            print(f"⚠️ Fast Medical AI failed: {e}")
            analysis_results['fast_medical_ai'] = {'error': str(e)}
        
        # 3. Backup analysis (if fast AI failed)
        if 'error' in analysis_results.get('fast_medical_ai', {}):
            print("🔄 Fast AI failed, attempting backup analysis...")
            try:
                import io
                # Simple fallback using basic image analysis
                # Basic image feature analysis
                fallback_result = {
                    'success': True,
                    'condition': f"Possible {detected_type} condition requiring examination",
                    'confidence': 0.3,
                    'urgency': 'moderate',
                    'recommendations': [
                        f"Professional {detected_type} examination recommended",
                        "Monitor symptoms for changes",
                        "Consider specialist consultation"
                    ],
                    'analysis_method': 'fallback_basic'
                }
                
                analysis_results['fallback_analysis'] = fallback_result
                print(f"✅ Fallback analysis completed")
                
            except Exception as e:
                print(f"⚠️ Fallback analysis failed: {e}")
                analysis_results['fallback_analysis'] = {'error': str(e)}
        
        # 4. Final result compilation - Optimized for Fast Analysis
        final_analysis = _combine_fast_medical_analysis(
            analysis_results, detected_type, symptoms
        )
        
        # Add metadata
        final_analysis['timestamp'] = str(datetime.now())
        final_analysis['user_id'] = request.user['id']
        final_analysis['image_type'] = detected_type
        final_analysis['detection_confidence'] = detection_confidence
        final_analysis['presentation_mode'] = True  # Flag for fast analysis
        
        return jsonify({
            'success': True,
            'image_type': detected_type,
            'detection_confidence': detection_confidence,
            'analysis': final_analysis,
            'fast_analysis': True,
            'processing_time_ms': analysis_results.get('fast_medical_ai', {}).get('processing_time_ms', 0),
            'analysis_methods': ['fast_medical_ai', 'image_routing']
        })
        
    except Exception as e:
        print(f"❌ Medical image analysis error: {e}")
        return jsonify({
            'success': False,
            'message': f'Analysis failed: {str(e)}'
        }), 500

def _combine_medical_analysis_results(analysis_results: dict, image_type: str, symptoms: str = "") -> dict:
    """
    Combine multiple analysis results into comprehensive medical analysis
    
    Args:
        analysis_results: Dictionary containing all analysis results
        image_type: Detected image type
        symptoms: Patient symptoms
        
    Returns:
        Combined comprehensive analysis
    """
    try:
        final_analysis = {
            'analysis_type': 'Multi-Modal Enhanced Medical Analysis',
            'image_type': image_type,
            'analysis_methods': [],
            'conditions': [],
            'recommendations': [],
            'confidence_scores': {},
            'specialist_needed': 'General Practitioner',
            'urgency_level': 'MODERATE',
            'summary': '',
            'model_insights': {}
        }
        
        # Process VLM analysis (NEW)
        vlm_result = analysis_results.get('vlm_analysis', {})
        if vlm_result.get('success') and not vlm_result.get('error'):
            final_analysis['analysis_methods'].append('vision_language_model')
            if 'analysis' in vlm_result:
                vlm_analysis = vlm_result['analysis']
                if 'conditions' in vlm_analysis:
                    final_analysis['conditions'].extend(vlm_analysis['conditions'])
                final_analysis['model_insights']['vlm'] = {
                    'model_used': vlm_result.get('model_used', 'unknown'),
                    'confidence': vlm_analysis.get('overall_confidence', 70),
                    'description': vlm_analysis.get('image_description', ''),
                    'correlation': vlm_analysis.get('symptom_correlation', {})
                }
            final_analysis['confidence_scores']['vlm'] = 85
        
        # Process Specialized model analysis (CheXNet, DermNet, etc.)
        specialized_result = analysis_results.get('specialized_model', {})
        if specialized_result.get('success') and not specialized_result.get('error'):
            final_analysis['analysis_methods'].append('specialized_medical_model')
            if 'predictions' in specialized_result:
                for pred in specialized_result['predictions']:
                    final_analysis['conditions'].append({
                        'name': pred.get('condition', 'Unknown'),
                        'confidence': pred.get('confidence', 0),
                        'severity': pred.get('severity', 'Unknown'),
                        'source': 'specialized_model',
                        'recommendation': pred.get('recommendation', '')
                    })
            final_analysis['model_insights']['specialized'] = {
                'model_used': specialized_result.get('selected_model', 'unknown'),
                'model_name': specialized_result.get('model_name', ''),
                'selection_reason': specialized_result.get('selection_reason', '')
            }
            final_analysis['confidence_scores']['specialized'] = 90
        
        # Process Lightweight AI analysis (NEW FALLBACK)
        lightweight_result = analysis_results.get('lightweight_ai', {})
        if lightweight_result.get('success') and not lightweight_result.get('error'):
            final_analysis['analysis_methods'].append('lightweight_medical_ai')
            if 'predicted_condition' in lightweight_result:
                final_analysis['conditions'].append({
                    'name': lightweight_result['predicted_condition'],
                    'confidence': lightweight_result.get('confidence', 0),
                    'severity': lightweight_result.get('severity', 'Unknown'),
                    'source': 'lightweight_ai',
                    'recommendation': lightweight_result.get('primary_recommendation', '')
                })
            
            # Add computer vision analysis insights
            if 'computer_vision_analysis' in lightweight_result:
                cv_analysis = lightweight_result['computer_vision_analysis']
                final_analysis['model_insights']['lightweight_cv'] = {
                    'visual_features': cv_analysis.get('visual_features', {}),
                    'color_analysis': cv_analysis.get('color_analysis', {}),
                    'texture_analysis': cv_analysis.get('texture_analysis', {}),
                    'shape_analysis': cv_analysis.get('shape_analysis', {})
                }
            
            # Add medical rules analysis
            if 'medical_rules_analysis' in lightweight_result:
                rules_analysis = lightweight_result['medical_rules_analysis']
                final_analysis['model_insights']['medical_rules'] = {
                    'matching_conditions': rules_analysis.get('matching_conditions', []),
                    'symptom_matches': rules_analysis.get('symptom_matches', []),
                    'rule_confidence': rules_analysis.get('confidence', 0)
                }
            
            final_analysis['confidence_scores']['lightweight'] = lightweight_result.get('confidence', 70)
        
        # Process specialist analysis
        specialist_result = analysis_results.get('specialist_analysis', {})
        if specialist_result.get('success') and not specialist_result.get('error'):
            final_analysis['analysis_methods'].append('specialist_ai_model')
            if 'conditions' in specialist_result:
                final_analysis['conditions'].extend(specialist_result['conditions'])
            final_analysis['confidence_scores']['specialist'] = 80
            if 'specialty' in specialist_result:
                final_analysis['specialist_needed'] = specialist_result['specialty'].title()
        
        # Process traditional analysis
        traditional_result = analysis_results.get('traditional_analysis', {})
        if traditional_result and traditional_result.get('success'):
            final_analysis['analysis_methods'].append('traditional_analysis')
            if 'analysis' in traditional_result and 'conditions' in traditional_result['analysis']:
                final_analysis['conditions'].extend(traditional_result['analysis']['conditions'])
            final_analysis['confidence_scores']['traditional'] = traditional_result.get('confidence', 70)
        
        # Process LLM analysis
        llm_result = analysis_results.get('llm_analysis', {})
        if llm_result.get('success') and 'analysis' in llm_result:
            final_analysis['analysis_methods'].append('llm_enhanced')
            llm_analysis = llm_result['analysis']
            
            # Add LLM predictions
            if 'condition_predictions' in llm_analysis:
                final_analysis['conditions'].extend(llm_analysis['condition_predictions'])
            
            # Add urgency assessment
            if 'urgency_assessment' in llm_analysis:
                urgency = llm_analysis['urgency_assessment']
                final_analysis['urgency_level'] = urgency.get('urgency_level', 'MODERATE')
                final_analysis['urgency_details'] = urgency
            
            # Add specialist recommendation
            if 'specialist_recommendation' in llm_analysis:
                specialist_rec = llm_analysis['specialist_recommendation']
                if specialist_rec.get('confidence', 0) > 70:
                    final_analysis['specialist_needed'] = specialist_rec.get('primary_specialist', 'General Practitioner')
            
            final_analysis['confidence_scores']['llm'] = 75
        
        # Remove duplicates and rank conditions
        unique_conditions = {}
        for condition in final_analysis['conditions']:
            name = condition.get('name', 'Unknown').lower()
            confidence = condition.get('confidence', 0)
            
            if name not in unique_conditions or confidence > unique_conditions[name].get('confidence', 0):
                unique_conditions[name] = condition
        
        final_analysis['conditions'] = sorted(
            list(unique_conditions.values()),
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )[:7]  # Top 7 conditions
        
        # Generate enhanced recommendations
        final_analysis['recommendations'] = _generate_enhanced_medical_recommendations(
            final_analysis['conditions'],
            final_analysis.get('urgency_details', {}),
            final_analysis['specialist_needed'],
            final_analysis['model_insights'],
            symptoms
        )
        
        # Calculate overall confidence with weighted scoring
        confidence_weights = {
            'specialized': 0.25,   # High weight for specialized models
            'vlm': 0.20,          # High weight for VLM  
            'lightweight': 0.25,   # High weight for lightweight AI (when used as primary)
            'specialist': 0.15,    # Medium weight for specialist models
            'llm': 0.10,          # Medium weight for LLM
            'traditional': 0.05   # Lower weight for traditional
        }
        
        weighted_confidence = 0
        total_weight = 0
        for method, score in final_analysis['confidence_scores'].items():
            weight = confidence_weights.get(method, 0.1)
            weighted_confidence += score * weight
            total_weight += weight
        
        final_analysis['overall_confidence'] = weighted_confidence / total_weight if total_weight > 0 else 50
        
        # Generate comprehensive summary
        final_analysis['summary'] = _generate_enhanced_analysis_summary(final_analysis)
        
        return final_analysis
        
    except Exception as e:
        print(f"Error combining enhanced medical analysis results: {e}")
        return {
            'analysis_type': 'Basic Analysis (Error Recovery)',
            'error': 'Failed to combine analysis results',
            'image_type': image_type,
            'analysis_methods': ['error_recovery'],
            'conditions': [],
            'recommendations': ['Consult healthcare provider for proper evaluation'],
            'specialist_needed': 'General Practitioner'
        }

def _combine_fast_medical_analysis(analysis_results: dict, image_type: str, symptoms: str = "") -> dict:
    """
    Combine fast medical AI analysis results for presentation purposes
    
    Args:
        analysis_results: Dictionary containing fast analysis results
        image_type: Detected image type
        symptoms: Patient symptoms
        
    Returns:
        Combined fast analysis optimized for presentations
    """
    try:
        # Get fast medical AI result (primary)
        fast_result = analysis_results.get('fast_medical_ai', {})
        
        if fast_result.get('success') and not fast_result.get('error'):
            # Use fast AI results directly
            final_analysis = {
                'analysis_type': 'Fast Medical AI Analysis (Presentation Mode)',
                'image_type': image_type,
                'analysis_methods': ['fast_medical_ai'],
                'conditions': fast_result.get('conditions', []),
                'recommendations': fast_result.get('recommendations', []),
                'confidence_score': fast_result.get('confidence', 0.7),
                'specialist_needed': fast_result.get('specialist_recommendation', 'General Practitioner'),
                'urgency_level': fast_result.get('urgency', 'MODERATE').upper(),
                'summary': fast_result.get('analysis_summary', 'Fast medical analysis completed'),
                'processing_time_ms': fast_result.get('processing_time_ms', 0),
                'overall_confidence': int(fast_result.get('confidence', 0.7) * 100)
            }
            
            # Add routing information if available
            routing_result = analysis_results.get('routing', {})
            if routing_result.get('success'):
                final_analysis['detection_details'] = {
                    'confidence': routing_result.get('confidence', 0),
                    'method': 'ai_router'
                }
                final_analysis['analysis_methods'].append('image_routing')
            
        else:
            # Use fallback analysis if fast AI failed
            fallback_result = analysis_results.get('fallback_analysis', {})
            if fallback_result.get('success'):
                final_analysis = {
                    'analysis_type': 'Fallback Medical Analysis',
                    'image_type': image_type,
                    'analysis_methods': ['fallback_basic'],
                    'conditions': [{
                        'name': fallback_result.get('condition', 'Unknown condition'),
                        'confidence': fallback_result.get('confidence', 0.3),
                        'source': 'fallback'
                    }],
                    'recommendations': fallback_result.get('recommendations', []),
                    'confidence_score': fallback_result.get('confidence', 0.3),
                    'specialist_needed': 'General Practitioner',
                    'urgency_level': fallback_result.get('urgency', 'MODERATE').upper(),
                    'summary': 'Basic analysis performed - professional evaluation recommended',
                    'overall_confidence': int(fallback_result.get('confidence', 0.3) * 100)
                }
            else:
                # Last resort - minimal analysis
                final_analysis = {
                    'analysis_type': 'Minimal Analysis (Backup)',
                    'image_type': image_type,
                    'analysis_methods': ['minimal_backup'],
                    'conditions': [{
                        'name': f'Possible {image_type} condition',
                        'confidence': 0.2,
                        'source': 'minimal'
                    }],
                    'recommendations': [
                        'Professional medical evaluation required',
                        'Bring image to healthcare provider',
                        'Monitor symptoms'
                    ],
                    'confidence_score': 0.2,
                    'specialist_needed': 'General Practitioner',
                    'urgency_level': 'MODERATE',
                    'summary': 'Image received - professional evaluation recommended',
                    'overall_confidence': 20
                }
        
        return final_analysis
        
    except Exception as e:
        print(f"Error combining fast medical analysis results: {e}")
        return {
            'analysis_type': 'Error Recovery Analysis',
            'error': 'Failed to combine fast analysis results',
            'image_type': image_type,
            'analysis_methods': ['error_recovery'],
            'conditions': [],
            'recommendations': ['Consult healthcare provider for proper evaluation'],
            'specialist_needed': 'General Practitioner',
            'overall_confidence': 0
        }

def _generate_medical_recommendations(conditions: list, urgency: dict, specialist: str, symptoms: str = "") -> list:
    """Generate comprehensive medical recommendations"""
    recommendations = []
    
    # Urgency-based recommendations
    urgency_level = urgency.get('urgency_level', 'MODERATE')
    if urgency_level == 'URGENT':
        recommendations.append('🚨 Seek immediate medical attention')
        recommendations.append('Consider emergency room or urgent care')
    elif urgency_level == 'MODERATE':
        recommendations.append('📅 Schedule appointment within 1-2 weeks')
    else:
        recommendations.append('📋 Routine medical consultation recommended')
    
    # Specialist recommendation
    if specialist and specialist != 'General Practitioner':
        recommendations.append(f'👨‍⚕️ Consultation with {specialist} recommended')
    
    # Condition-specific recommendations
    if conditions:
        top_condition = conditions[0]
        confidence = top_condition.get('confidence', 0)
        condition_name = top_condition.get('name', 'Unknown condition')
        
        if confidence > 80:
            recommendations.append(f'🎯 High confidence finding: {condition_name}')
        elif confidence > 60:
            recommendations.append(f'🤔 Possible condition: {condition_name}')
        else:
            recommendations.append('❓ Multiple possibilities - professional evaluation needed')
    
    # General medical recommendations
    recommendations.extend([
        '📸 Document any changes in appearance',
        '📝 Bring image and symptoms to appointment',
        '⚠️ Monitor for worsening symptoms'
    ])
    
    return recommendations[:7]  # Limit to 7 recommendations

def _generate_analysis_summary(analysis: dict) -> str:
    """Generate a comprehensive analysis summary"""
    try:
        image_type = analysis.get('image_type', 'unknown')
        methods = analysis.get('analysis_methods', [])
        conditions = analysis.get('conditions', [])
        specialist = analysis.get('specialist_needed', 'General Practitioner')
        urgency = analysis.get('urgency_level', 'MODERATE')
        confidence = analysis.get('overall_confidence', 50)
        
        summary_parts = []
        
        # Analysis overview
        summary_parts.append(f"Analysis of {image_type} image completed using {len(methods)} methods.")
        
        # Key findings
        if conditions:
            top_condition = conditions[0]
            summary_parts.append(f"Primary finding: {top_condition.get('name', 'Unknown')} "
                               f"(confidence: {top_condition.get('confidence', 0):.0f}%).")
        else:
            summary_parts.append("No specific conditions identified.")
        
        # Recommendations
        if urgency == 'URGENT':
            summary_parts.append("⚠️ Urgent medical attention recommended.")
        elif specialist != 'General Practitioner':
            summary_parts.append(f"Recommend consultation with {specialist}.")
        else:
            summary_parts.append("Routine medical evaluation suggested.")
        
        # Confidence note
        if confidence > 75:
            summary_parts.append("High confidence in analysis results.")
        elif confidence > 50:
            summary_parts.append("Moderate confidence - additional evaluation recommended.")
        else:
            summary_parts.append("Low confidence - professional medical assessment essential.")
        
        return " ".join(summary_parts)
        
    except Exception as e:
        return f"Analysis completed. Professional medical evaluation recommended for accurate diagnosis."

def _generate_enhanced_medical_recommendations(conditions: list, urgency: dict, specialist: str, 
                                            model_insights: dict, symptoms: str = "") -> list:
    """Generate enhanced medical recommendations based on all analysis methods"""
    recommendations = []
    
    # Urgency-based recommendations
    urgency_level = urgency.get('urgency_level', 'MODERATE')
    if urgency_level == 'URGENT':
        recommendations.append('🚨 URGENT: Seek immediate medical attention')
        recommendations.append('🏥 Consider emergency room or urgent care')
    elif urgency_level == 'MODERATE':
        recommendations.append('📅 Schedule appointment within 1-2 weeks')
    else:
        recommendations.append('📋 Routine medical consultation recommended')
    
    # Model-specific insights
    if 'specialized' in model_insights:
        specialized = model_insights['specialized']
        model_name = specialized.get('model_name', 'Specialized model')
        recommendations.append(f'🤖 {model_name} analysis completed')
    
    if 'vlm' in model_insights:
        vlm = model_insights['vlm']
        correlation = vlm.get('correlation', {})
        if correlation.get('strength', 0) > 70:
            recommendations.append('✅ Strong correlation between symptoms and image findings')
        elif correlation.get('strength', 0) < 40:
            recommendations.append('⚠️ Symptoms may not fully match visual findings')
    
    # Specialist recommendation
    if specialist and specialist != 'General Practitioner':
        recommendations.append(f'👨‍⚕️ Consultation with {specialist} recommended')
    
    # Condition-specific recommendations
    if conditions:
        top_condition = conditions[0]
        confidence = top_condition.get('confidence', 0)
        condition_name = top_condition.get('name', 'Unknown condition')
        source = top_condition.get('source', 'analysis')
        
        if confidence > 85:
            recommendations.append(f'🎯 High confidence finding: {condition_name} ({source})')
        elif confidence > 65:
            recommendations.append(f'🤔 Probable condition: {condition_name} ({source})')
        else:
            recommendations.append('❓ Multiple possibilities - professional evaluation needed')
    
    # Enhanced medical recommendations
    recommendations.extend([
        '📸 Document any changes in appearance or symptoms',
        '📱 Bring this analysis report to your appointment',
        '⚠️ Monitor for worsening or new symptoms'
    ])
    
    return recommendations[:8]  # Limit to 8 recommendations

def _generate_enhanced_analysis_summary(analysis: dict) -> str:
    """Generate enhanced comprehensive analysis summary"""
    try:
        image_type = analysis.get('image_type', 'unknown')
        methods = analysis.get('analysis_methods', [])
        conditions = analysis.get('conditions', [])
        specialist = analysis.get('specialist_needed', 'General Practitioner')
        urgency = analysis.get('urgency_level', 'MODERATE')
        confidence = analysis.get('overall_confidence', 50)
        model_insights = analysis.get('model_insights', {})
        
        summary_parts = []
        
        # Analysis overview
        if 'vision_language_model' in methods and 'specialized_medical_model' in methods:
            summary_parts.append(f"Advanced multi-modal analysis of {image_type} image using {len(methods)} AI methods including Vision-Language Models and specialized medical AI.")
        elif len(methods) > 3:
            summary_parts.append(f"Comprehensive analysis of {image_type} image using {len(methods)} advanced AI methods.")
        else:
            summary_parts.append(f"Analysis of {image_type} image completed using {len(methods)} methods.")
        
        # Model insights
        if 'specialized' in model_insights:
            specialized = model_insights['specialized']
            model_used = specialized.get('model_used', 'unknown')
            if model_used in ['chexnet', 'dermnet', 'fastmri', 'retina_net']:
                summary_parts.append(f"Specialized {model_used.upper()} model provided targeted analysis.")
        
        if 'vlm' in model_insights:
            vlm = model_insights['vlm']
            correlation = vlm.get('correlation', {})
            if correlation.get('strength', 0) > 70:
                summary_parts.append("Vision-Language Model found strong symptom-image correlation.")
        
        # Key findings
        if conditions:
            top_condition = conditions[0]
            condition_name = top_condition.get('name', 'Unknown')
            condition_confidence = top_condition.get('confidence', 0)
            source = top_condition.get('source', 'analysis')
            
            if source == 'specialized_model':
                summary_parts.append(f"Primary finding from specialized medical AI: {condition_name} "
                                   f"(confidence: {condition_confidence:.0f}%).")
            else:
                summary_parts.append(f"Primary finding: {condition_name} "
                                   f"(confidence: {condition_confidence:.0f}%).")
        else:
            summary_parts.append("No specific conditions identified with high confidence.")
        
        # Urgency and recommendations
        if urgency == 'URGENT':
            summary_parts.append("⚠️ URGENT medical attention recommended.")
        elif specialist != 'General Practitioner':
            summary_parts.append(f"Recommend consultation with {specialist}.")
        else:
            summary_parts.append("Medical evaluation suggested for confirmation.")
        
        # Confidence assessment
        if confidence > 80:
            summary_parts.append("High confidence in analysis results from multiple AI models.")
        elif confidence > 65:
            summary_parts.append("Good confidence in analysis - consider professional confirmation.")
        elif confidence > 50:
            summary_parts.append("Moderate confidence - professional medical assessment recommended.")
        else:
            summary_parts.append("Low confidence - professional medical assessment essential.")
        
        return " ".join(summary_parts)
        
    except Exception as e:
        return f"Enhanced AI analysis completed using multiple models. Professional medical evaluation recommended for accurate diagnosis."

        # 7. Combine all results
        final_analysis = _combine_medical_analysis_results(
            analysis_results, detected_type, symptoms
        )
        
        # Add metadata
        final_analysis['timestamp'] = str(datetime.now())
        final_analysis['user_id'] = request.user['id']
        final_analysis['image_type'] = detected_type
        final_analysis['detection_confidence'] = detection_confidence
        
        return jsonify({
            'success': True,
            'image_type': detected_type,
            'detection_confidence': detection_confidence,
            'analysis': final_analysis,
            'detailed_results': analysis_results,
            'specialist_used': analysis_results.get('specialist_analysis', {}).get('specialty', 'none'),
            'vlm_used': analysis_results.get('vlm_analysis', {}).get('model_used', 'none'),
            'specialized_model': analysis_results.get('specialized_model', {}).get('selected_model', 'none'),
            'analysis_methods': final_analysis.get('analysis_methods', [])
        })
        
    except Exception as e:
        print(f"❌ Medical image analysis error: {e}")
        return jsonify({
            'success': False,
            'message': f'Analysis failed: {str(e)}'
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
    
# ============================================
# MongoDB Conversation Management API Endpoints
# ============================================

@app.route('/api/conversations', methods=['GET'])
@login_required
def api_get_conversations():
    """Get user's conversations from MongoDB"""
    try:
        conversations = chat_history_db.get_user_conversations(request.user['id'])
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
    """Get messages in a specific conversation from MongoDB"""
    try:
        messages = chat_history_db.get_conversation_messages(conversation_id, request.user['id'])
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
    """Delete a specific conversation from MongoDB"""
    try:
        success = chat_history_db.delete_conversation(conversation_id, request.user['id'])
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

# ============================================
# Application Startup
# ============================================

if __name__ == "__main__":
    print("🚀 Starting medibot2 Application...")
    
    # Check dependencies
    openai_ok = check_openai_setup()
    doctor_db_ok = check_doctor_database()
    
    print("=" * 70)
    print("✅ Features Available:")
    print(f"  📱 Authentication System: ✅ Ready (medibot2 MySQL)")
    print(f"  💬 Chat History: ✅ Ready (MongoDB)")
    print(f"  🤖 Medical AI: {'✅ Ready' if openai_ok else '⚠ Limited'}")
    print(f"  🏥 Doctor Database: {'✅ Ready' if doctor_db_ok else '⚠ Unavailable'}")
    print(f"  🗄️  User Database: medibot2 (MySQL)")
    print(f"  🗄️  Chat Database: {chat_history_db.database_name} (MongoDB)")
    print("\n🌐 Access URLs:")
    print("  📱 Main app: http://localhost:5000")
    print("  🔐 Login: http://localhost:5000/login")
    print("  📝 Register: http://localhost:5000/register")
    print("  💬 Chat (after login): http://localhost:5000/chat")
    
    app.run(debug=True, port=5000, use_reloader=False)
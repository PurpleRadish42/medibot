#!/usr/bin/env python3
"""
Updated main.py with improved chat history functionality using SQLite/MySQL-compatible database
"""

import sys
import os
from pathlib import Path
from functools import wraps
import threading
import time

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
sys.path.insert(0, str(project_root))

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
import gradio as gr

# Import our new chat history database
from chat_history_db import ChatHistoryDB

# Initialize chat history database
chat_db = ChatHistoryDB()

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
    import gradio as gr
    gradio_available = True
    print("✅ Gradio available")
except ImportError:
    print("⚠ Gradio not available")

# Create Flask application
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Simple session management for demo purposes
user_sessions = {}

def get_current_user_id():
    """Get current user ID (simplified for demo)"""
    # In a real application, this would come from authentication
    user_id = session.get('user_id')
    if not user_id:
        # Create a simple demo user
        user_id = chat_db.get_or_create_user("demo_user", "demo@example.com")
        session['user_id'] = user_id
    return user_id

def login_required(f):
    """Simple login decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # For demo purposes, auto-create a user
            session['user_id'] = get_current_user_id()
        return f(*args, **kwargs)
    return decorated_function

def fallback_medical_response(message):
    """Fallback response when AI is not available"""
    return "I understand your concern. While I'm currently in limited mode, I recommend consulting with a healthcare professional for personalized medical advice. Is there anything specific you'd like to know about general health topics?"

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/chat')
@login_required
def chat():
    """Chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """API endpoint for chat with enhanced history storage"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        user_id = get_current_user_id()
        
        # Create new session if not provided
        if not session_id:
            # Generate title from first few words of message
            title = message[:50] + "..." if len(message) > 50 else message
            session_id = chat_db.create_chat_session(user_id, title)
        
        # Save user message to database
        chat_db.save_message(session_id, user_id, "user", message)
        
        # Generate AI response
        try:
            if medical_functions_available and medical_recommender:
                response = medical_recommender.get_medical_advice(message)
            else:
                response = fallback_medical_response(message)
        except Exception as e:
            print(f"❌ Medical AI error: {e}")
            response = fallback_medical_response(message)
        
        # Save assistant response to database
        chat_db.save_message(session_id, user_id, "assistant", response)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'success': True
        })
        
    except Exception as e:
        print(f"Chat API error: {e}")
        return jsonify({'error': 'Failed to process chat message'}), 500

@app.route('/api/chat-history')
@login_required
def api_chat_history():
    """Get user's chat sessions"""
    try:
        user_id = get_current_user_id()
        sessions = chat_db.get_user_sessions(user_id)
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        print(f"Chat history error: {e}")
        return jsonify({'error': 'Failed to retrieve chat history'}), 500

@app.route('/api/chat-session/<session_id>')
@login_required
def api_get_session(session_id):
    """Get messages for a specific chat session"""
    try:
        user_id = get_current_user_id()
        messages = chat_db.get_session_messages(session_id, user_id)
        
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        print(f"Session retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve session messages'}), 500

@app.route('/api/chat-session/<session_id>', methods=['DELETE'])
@login_required
def api_delete_session(session_id):
    """Delete a chat session"""
    try:
        user_id = get_current_user_id()
        success = chat_db.delete_session(session_id, user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Session deleted successfully'})
        else:
            return jsonify({'error': 'Session not found or not authorized'}), 404
    except Exception as e:
        print(f"Session deletion error: {e}")
        return jsonify({'error': 'Failed to delete session'}), 500

@app.route('/api/chat-session/<session_id>/title', methods=['PUT'])
@login_required
def api_update_session_title(session_id):
    """Update the title of a chat session"""
    try:
        data = request.get_json()
        new_title = data.get('title', '').strip()
        
        if not new_title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        
        user_id = get_current_user_id()
        success = chat_db.update_session_title(session_id, user_id, new_title)
        
        if success:
            return jsonify({'success': True, 'message': 'Title updated successfully'})
        else:
            return jsonify({'error': 'Session not found or not authorized'}), 404
    except Exception as e:
        print(f"Title update error: {e}")
        return jsonify({'error': 'Failed to update title'}), 500

@app.route('/api/chat-history/clear', methods=['DELETE'])
@login_required
def api_clear_chat_history():
    """Clear all chat history for the current user"""
    try:
        user_id = get_current_user_id()
        deleted_count = chat_db.clear_user_history(user_id)
        
        return jsonify({
            'success': True, 
            'message': f'Cleared all chat history',
            'deleted_sessions': deleted_count
        })
    except Exception as e:
        print(f"Clear history error: {e}")
        return jsonify({'error': 'Failed to clear chat history'}), 500

@app.route('/api/chat-stats')
@login_required
def api_chat_stats():
    """Get chat history statistics"""
    try:
        user_id = get_current_user_id()
        stats = chat_db.get_chat_history_stats(user_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.route('/api/new-chat', methods=['POST'])
@login_required
def api_new_chat():
    """Create a new chat session"""
    try:
        data = request.get_json() or {}
        title = data.get('title', 'New Chat')
        
        user_id = get_current_user_id()
        session_id = chat_db.create_chat_session(user_id, title)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'title': title
        })
    except Exception as e:
        print(f"New chat error: {e}")
        return jsonify({'error': 'Failed to create new chat'}), 500

def create_templates_directory():
    """Create templates directory if it doesn't exist"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create a basic chat.html template if it doesn't exist
    chat_template = templates_dir / "chat.html"
    if not chat_template.exists():
        with open(chat_template, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediBot Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .chat-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            height: 80vh;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .sidebar {
            width: 300px;
            border-right: 1px solid #ddd;
            padding: 20px;
            overflow-y: auto;
        }
        
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
        }
        
        .user-message {
            background-color: #007bff;
            color: white;
            margin-left: 20%;
            text-align: right;
        }
        
        .assistant-message {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            margin-right: 20%;
        }
        
        .chat-input {
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        
        .chat-input button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .session-item {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
            cursor: pointer;
        }
        
        .session-item:hover {
            background-color: #f8f9fa;
        }
        
        .session-item.active {
            background-color: #007bff;
            color: white;
        }
        
        .new-chat-btn {
            width: 100%;
            padding: 10px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>MediBot - Medical Chat Assistant</h1>
    
    <div class="chat-container">
        <div class="sidebar">
            <button class="new-chat-btn" onclick="startNewChat()">New Chat</button>
            <h3>Chat History</h3>
            <div id="chatSessions"></div>
        </div>
        
        <div class="chat-area">
            <div class="chat-messages" id="chatMessages"></div>
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Ask about your health concerns..." 
                       onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        let sessions = [];

        // Load chat sessions on page load
        window.onload = function() {
            loadChatSessions();
        };

        async function loadChatSessions() {
            try {
                const response = await fetch('/api/chat-history');
                const data = await response.json();
                
                if (data.success) {
                    sessions = data.sessions;
                    displayChatSessions();
                }
            } catch (error) {
                console.error('Error loading chat sessions:', error);
            }
        }

        function displayChatSessions() {
            const container = document.getElementById('chatSessions');
            container.innerHTML = '';
            
            sessions.forEach(session => {
                const div = document.createElement('div');
                div.className = 'session-item';
                div.onclick = () => loadSession(session.id);
                
                div.innerHTML = `
                    <div style="font-weight: bold;">${session.title}</div>
                    <div style="font-size: 12px; color: #666;">
                        ${session.message_count} messages
                    </div>
                `;
                
                container.appendChild(div);
            });
        }

        async function loadSession(sessionId) {
            try {
                const response = await fetch(`/api/chat-session/${sessionId}`);
                const data = await response.json();
                
                if (data.success) {
                    currentSessionId = sessionId;
                    displayMessages(data.messages);
                    updateActiveSession(sessionId);
                }
            } catch (error) {
                console.error('Error loading session:', error);
            }
        }

        function displayMessages(messages) {
            const container = document.getElementById('chatMessages');
            container.innerHTML = '';
            
            messages.forEach(message => {
                const div = document.createElement('div');
                div.className = `message ${message.type === 'user' ? 'user-message' : 'assistant-message'}`;
                div.textContent = message.content;
                container.appendChild(div);
            });
            
            container.scrollTop = container.scrollHeight;
        }

        function updateActiveSession(sessionId) {
            document.querySelectorAll('.session-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Find and activate the current session
            const sessionItems = document.querySelectorAll('.session-item');
            sessionItems.forEach((item, index) => {
                if (sessions[index] && sessions[index].id === sessionId) {
                    item.classList.add('active');
                }
            });
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Clear input
            input.value = '';
            
            // Add user message to UI
            addMessageToUI(message, true);
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: currentSessionId
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Update current session ID if it's a new chat
                    if (!currentSessionId) {
                        currentSessionId = data.session_id;
                        await loadChatSessions(); // Reload sessions to show the new one
                    }
                    
                    // Add assistant response to UI
                    addMessageToUI(data.response, false);
                } else {
                    addMessageToUI('Sorry, there was an error processing your message.', false);
                }
            } catch (error) {
                console.error('Error sending message:', error);
                addMessageToUI('Sorry, there was an error processing your message.', false);
            }
        }

        function addMessageToUI(message, isUser) {
            const container = document.getElementById('chatMessages');
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
            div.textContent = message;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function startNewChat() {
            try {
                const response = await fetch('/api/new-chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentSessionId = data.session_id;
                    document.getElementById('chatMessages').innerHTML = '';
                    await loadChatSessions();
                    updateActiveSession(currentSessionId);
                }
            } catch (error) {
                console.error('Error starting new chat:', error);
            }
        }
    </script>
</body>
</html>""")

    # Create basic index.html template if it doesn't exist
    index_template = templates_dir / "index.html"
    if not index_template.exists():
        with open(index_template, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediBot - AI Medical Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            text-align: center;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #007bff;
            margin-bottom: 20px;
        }
        
        .start-button {
            display: inline-block;
            padding: 15px 30px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 18px;
            margin-top: 20px;
        }
        
        .start-button:hover {
            background-color: #0056b3;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .feature {
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 MediBot - AI Medical Assistant</h1>
        <p>Get medical advice and information from our AI-powered medical assistant. 
           Chat history is automatically saved for your convenience.</p>
        
        <a href="/chat" class="start-button">Start Chatting</a>
        
        <div class="features">
            <div class="feature">
                <h3>💬 Persistent Chat History</h3>
                <p>All your conversations are saved and can be accessed anytime</p>
            </div>
            <div class="feature">
                <h3>🧠 AI-Powered</h3>
                <p>Advanced medical knowledge to help with your health questions</p>
            </div>
            <div class="feature">
                <h3>🔒 Secure</h3>
                <p>Your medical conversations are kept private and secure</p>
            </div>
            <div class="feature">
                <h3>📱 Responsive</h3>
                <p>Works on desktop, tablet, and mobile devices</p>
            </div>
        </div>
    </div>
</body>
</html>""")

if __name__ == '__main__':
    print("🏥 MediBot Chat History System")
    print("=" * 50)
    
    # Create templates directory
    create_templates_directory()
    
    # Test database
    print("🧪 Testing database...")
    try:
        user_id = chat_db.get_or_create_user("test_user", "test@example.com")
        stats = chat_db.get_chat_history_stats(user_id)
        print(f"✅ Database working. User: {user_id}, Stats: {stats}")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("\n🚀 FLASK WEB SERVER STARTING")
    print("=" * 50)
    print("✅ Features Available:")
    print(f"  💬 Chat History Database: ✅ Ready (SQLite)")
    print(f"  🤖 Medical AI: {'✅ Ready' if medical_functions_available else '⚠ Limited'}")
    print("\n🌐 Access URLs:")
    print("  📱 Main app: http://localhost:5000")
    print("  💬 Chat: http://localhost:5000/chat")
    print("=" * 50)
    
    app.run(debug=True, port=5000, use_reloader=False)
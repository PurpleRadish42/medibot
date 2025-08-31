#!/usr/bin/env python3
"""
MySQL authentication system for medibot2 database
This file handles user authentication, sessions, and chat history using MySQL
"""

import pymysql
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MedibotAuthDatabase:
    def __init__(self):
        """Initialize MySQL database connection for medibot2"""
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USERNAME', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'medibot2'),
            'charset': 'utf8mb4',
            'autocommit': False
        }
        self.init_database()
    
    def get_connection(self):
        """Get a MySQL database connection"""
        try:
            return pymysql.connect(**self.mysql_config)
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def init_database(self):
        """Initialize the medibot2 database and create tables"""
        try:
            # Connect to MySQL server without selecting database
            server_config = self.mysql_config.copy()
            database_name = server_config.pop('database')
            
            conn = pymysql.connect(**server_config)
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"✅ Database '{database_name}' created/verified")
            
            cursor.execute(f"USE {database_name}")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    salt VARCHAR(64) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ Users table created/verified")
            
            # Create user_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    session_token VARCHAR(128) UNIQUE NOT NULL,
                    conversation_id VARCHAR(36) NOT NULL,
                    session_title VARCHAR(200) DEFAULT 'New Conversation',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_sessions (user_id),
                    INDEX idx_session_token (session_token),
                    INDEX idx_conversation_id (conversation_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ User sessions table created/verified")
            
            # Create chat_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    session_id INT NOT NULL,
                    conversation_id VARCHAR(36) NOT NULL,
                    message_type ENUM('user', 'assistant') NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_order INT NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE CASCADE,
                    INDEX idx_user_chat (user_id),
                    INDEX idx_session_chat (session_id),
                    INDEX idx_conversation_chat (conversation_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ Chat history table created/verified")
            
            conn.commit()
            conn.close()
            print("✅ medibot2 database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise
    
    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password, password_hash, salt):
        """Verify password against hash"""
        computed_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return computed_hash.hex() == password_hash
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """Validate password strength - simplified to just length requirement"""
        return len(password) >= 8
    
    def register_user(self, username, email, password, full_name):
        """Register a new user"""
        try:
            # Validate inputs
            if not username or not email or not password or not full_name:
                return False, "All fields are required"
            
            if not self.validate_email(email):
                return False, "Invalid email format"
            
            if not self.validate_password(password):
                return False, "Password must be at least 8 characters long"
            
            # Hash password
            password_hash, salt = self.hash_password(password)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "Username or email already exists"
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, full_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, password_hash, salt, full_name))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            print(f"User {username} registered successfully with ID {user_id}")
            return True, f"User {username} registered successfully"
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}"
    
    def authenticate_user(self, username_or_email, password):
        """Authenticate user login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find user by username or email
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, full_name, is_active
                FROM users 
                WHERE (username = %s OR email = %s) AND is_active = TRUE
            """, (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return False, "Invalid username/email or password", None
            
            user_id, username, email, stored_hash, salt, full_name, is_active = user
            
            # Verify password
            if self.verify_password(password, stored_hash, salt):
                user_data = {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'full_name': full_name
                }
                return True, "Login successful", user_data
            else:
                return False, "Invalid username/email or password", None
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, "Authentication failed", None
    
    def create_session(self, user_id, session_title="New Conversation"):
        """Create a new session for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generate session token and conversation ID
            session_token = secrets.token_urlsafe(64)
            conversation_id = str(uuid.uuid4())
            
            # Set expiration (optional - 30 days from now)
            expires_at = datetime.now() + timedelta(days=30)
            
            # Insert new session
            cursor.execute("""
                INSERT INTO user_sessions (user_id, session_token, conversation_id, session_title, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, session_token, conversation_id, session_title, expires_at))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Session created for user {user_id}: {session_token[:16]}...")
            return session_token
            
        except Exception as e:
            print(f"Session creation error: {e}")
            return None
    
    def verify_session(self, session_token):
        """Verify session token and return user data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get session info with user data
            cursor.execute("""
                SELECT s.user_id, s.conversation_id, s.expires_at, s.is_active,
                       u.username, u.email, u.full_name
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = %s AND s.is_active = TRUE AND u.is_active = TRUE
            """, (session_token,))
            
            session = cursor.fetchone()
            conn.close()
            
            if not session:
                return None
            
            user_id, conversation_id, expires_at, is_active, username, email, full_name = session
            
            # Check if session has expired
            if expires_at and datetime.now() > expires_at:
                self.logout_user(session_token)
                return None
            
            return {
                'id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'conversation_id': conversation_id
            }
            
        except Exception as e:
            print(f"Session verification error: {e}")
            return None
    
    def logout_user(self, session_token):
        """Logout user by deactivating session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE session_token = %s
            """, (session_token,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Logout error: {e}")
            return False
    
    def save_chat_message(self, user_id, message, response, conversation_id=None, session_token=None):
        """Save chat message and response to history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get session info if session_token provided
            session_id = None
            if session_token:
                cursor.execute("""
                    SELECT id, conversation_id FROM user_sessions 
                    WHERE session_token = %s AND is_active = TRUE
                """, (session_token,))
                session_info = cursor.fetchone()
                if session_info:
                    session_id, conversation_id = session_info
            
            # If no session found, create a new one
            if not session_id:
                # Create a new session
                new_session_token = self.create_session(user_id)
                if new_session_token:
                    cursor.execute("""
                        SELECT id, conversation_id FROM user_sessions 
                        WHERE session_token = %s
                    """, (new_session_token,))
                    session_info = cursor.fetchone()
                    if session_info:
                        session_id, conversation_id = session_info
            
            if not session_id:
                print("Failed to create or find session")
                return False
            
            # Get next message order
            cursor.execute("""
                SELECT COALESCE(MAX(message_order), 0) + 1 
                FROM chat_history 
                WHERE conversation_id = %s
            """, (conversation_id,))
            next_order = cursor.fetchone()[0]
            
            # Save user message
            cursor.execute("""
                INSERT INTO chat_history (user_id, session_id, conversation_id, message_type, message, message_order)
                VALUES (%s, %s, %s, 'user', %s, %s)
            """, (user_id, session_id, conversation_id, message, next_order))
            
            # Save assistant response
            cursor.execute("""
                INSERT INTO chat_history (user_id, session_id, conversation_id, message_type, message, response, message_order)
                VALUES (%s, %s, %s, 'assistant', %s, %s, %s)
            """, (user_id, session_id, conversation_id, response, response, next_order + 1))
            
            # Update session title if it's the first message
            if next_order == 1:
                title = message[:50] + "..." if len(message) > 50 else message
                cursor.execute("""
                    UPDATE user_sessions 
                    SET session_title = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (title, session_id))
            
            conn.commit()
            conn.close()
            
            print(f"Chat message saved for conversation {conversation_id}")
            return True
            
        except Exception as e:
            print(f"Save chat message error: {e}")
            return False
    
    def get_user_conversations(self, user_id):
        """Get all conversations for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.conversation_id, s.session_title, s.created_at, s.updated_at,
                       COUNT(c.id) as message_count
                FROM user_sessions s
                LEFT JOIN chat_history c ON s.conversation_id = c.conversation_id
                WHERE s.user_id = %s AND s.is_active = TRUE
                GROUP BY s.conversation_id, s.session_title, s.created_at, s.updated_at
                ORDER BY s.updated_at DESC
            """, (user_id,))
            
            conversations = []
            for row in cursor.fetchall():
                conversation_id, title, created_at, updated_at, message_count = row
                conversations.append({
                    'id': conversation_id,
                    'title': title,
                    'created_at': created_at.isoformat() if created_at else None,
                    'updated_at': updated_at.isoformat() if updated_at else None,
                    'message_count': message_count
                })
            
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"Get conversations error: {e}")
            return []
    
    def get_conversation_messages(self, conversation_id, user_id):
        """Get all messages in a specific conversation"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT message_type, message, response, timestamp, message_order
                FROM chat_history
                WHERE conversation_id = %s AND user_id = %s
                ORDER BY message_order ASC, timestamp ASC
            """, (conversation_id, user_id))
            
            messages = []
            for row in cursor.fetchall():
                message_type, message, response, timestamp, message_order = row
                messages.append({
                    'type': message_type,
                    'message': message,
                    'response': response,
                    'timestamp': timestamp.isoformat() if timestamp else None,
                    'order': message_order
                })
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Get conversation messages error: {e}")
            return []
    
    def delete_conversation(self, conversation_id, user_id):
        """Delete a specific conversation"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Deactivate the session
            cursor.execute("""
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE conversation_id = %s AND user_id = %s
            """, (conversation_id, user_id))
            
            # Delete chat history for this conversation
            cursor.execute("""
                DELETE FROM chat_history 
                WHERE conversation_id = %s AND user_id = %s
            """, (conversation_id, user_id))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Deleted conversation {conversation_id}: {deleted_count} messages")
            return deleted_count > 0
            
        except Exception as e:
            print(f"Delete conversation error: {e}")
            return False
    
    def clear_all_user_chats(self, user_id):
        """Clear all chat history for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Deactivate all sessions
            cursor.execute("""
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE user_id = %s
            """, (user_id,))
            
            # Delete all chat history
            cursor.execute("""
                DELETE FROM chat_history 
                WHERE user_id = %s
            """, (user_id,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Cleared all chats for user {user_id}: {deleted_count} messages deleted")
            return deleted_count
            
        except Exception as e:
            print(f"Clear chats error: {e}")
            return 0
    
    def get_chat_history(self, user_id, limit=50):
        """Get user's recent chat history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT message, response, timestamp
                FROM chat_history
                WHERE user_id = %s AND message_type = 'user'
                ORDER BY timestamp DESC
                LIMIT %s
            """, (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                message, response, timestamp = row
                history.append((message, response, timestamp))
            
            conn.close()
            return history
            
        except Exception as e:
            print(f"Get chat history error: {e}")
            return []


# Test the database functionality
if __name__ == "__main__":
    print("Testing medibot2 MySQL authentication database...")
    print("Make sure MySQL is running and environment variables are set!")
    
    try:
        # Initialize the database
        auth = MedibotAuthDatabase()
        
        print("Testing authentication database...")
        
        # Test registration
        success, message = auth.register_user(
            "testuser", 
            "test@example.com", 
            "TestPassword123", 
            "Test User"
        )
        print(f"Registration: {success} - {message}")
        
        # Test login
        success, message, user_data = auth.authenticate_user("testuser", "TestPassword123")
        print(f"Login: {success} - {message}")
        if user_data:
            print(f"User data: {user_data}")
            
            # Test session creation
            session_token = auth.create_session(user_data['id'])
            if session_token:
                print(f"Session created: {session_token[:16]}...")
                
                # Test session verification
                verified_user = auth.verify_session(session_token)
                print(f"Session verified: {verified_user}")
                
                # Test chat message saving
                chat_saved = auth.save_chat_message(
                    user_data['id'], 
                    "Hello, I have a headache", 
                    "I understand you have a headache. Here are some recommendations...",
                    session_token=session_token
                )
                print(f"Chat saved: {chat_saved}")
                
                # Test getting conversations
                conversations = auth.get_user_conversations(user_data['id'])
                print(f"Conversations: {len(conversations)}")
                
                # Test logout
                auth.logout_user(session_token)
                print("User logged out")
        
        print("✅ medibot2 database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
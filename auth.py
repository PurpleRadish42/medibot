import pymysql
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
import re
import os
from config import DatabaseConfig

class AuthDatabase:
    def __init__(self, mysql_config=None):
        """Initialize MySQL database connection"""
        self.mysql_config = mysql_config or DatabaseConfig.get_mysql_config()
        self.init_database()
    
    def init_database(self):
        """Initialize the database with users table"""
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.mysql_config['database']}")
        cursor.execute(f"USE {self.mysql_config['database']}")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(512) NOT NULL,
                salt VARCHAR(64) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT 1,
                failed_login_attempts INT DEFAULT 0,
                locked_until TIMESTAMP NULL,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create sessions table for session management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                INDEX idx_session_token (session_token),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                INDEX idx_user_id_timestamp (user_id, timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        conn.commit()
        conn.close()
        print("MySQL database initialized successfully")
    
    def get_connection(self):
        """Get a MySQL database connection"""
        conn = pymysql.connect(**self.mysql_config)
        # Select the database
        cursor = conn.cursor()
        cursor.execute(f"USE {self.mysql_config['database']}")
        cursor.close()
        return conn
    
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
        return hashlib.pbkdf2_hmac('sha256', 
                                 password.encode('utf-8'), 
                                 salt.encode('utf-8'), 
                                 100000).hex() == password_hash
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """Validate password strength - simplified to just length requirement"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        return True, "Password is valid"
    
    def register_user(self, username, email, password, full_name):
        """Register a new user"""
        try:
            # Validate inputs
            if not username or len(username) < 3:
                return False, "Username must be at least 3 characters long"
            
            if not self.validate_email(email):
                return False, "Invalid email format"
            
            is_valid, message = self.validate_password(password)
            if not is_valid:
                return False, message
            
            if not full_name or len(full_name) < 2:
                return False, "Full name must be at least 2 characters long"
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', 
                          (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "Username or email already exists"
            
            # Hash password
            password_hash, salt = self.hash_password(password)
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, full_name)
                VALUES (%s, %s, %s, %s, %s)
            ''', (username, email, password_hash, salt, full_name))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            print(f"User {username} registered successfully with ID {user_id}")
            return True, f"User {username} registered successfully"
            
        except pymysql.Error as e:
            print(f"Database error during registration: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            print(f"Unexpected error during registration: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def authenticate_user(self, username_or_email, password):
        """Authenticate user login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user by username or email
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, full_name, 
                       failed_login_attempts, locked_until, is_active
                FROM users 
                WHERE (username = %s OR email = %s) AND is_active = 1
            ''', (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            if not user:
                conn.close()
                return False, "Invalid username/email or password", None
            
            user_id, username, email, password_hash, salt, full_name, failed_attempts, locked_until, is_active = user
            
            # Check if account is locked
            if locked_until:
                if datetime.now() < locked_until:
                    conn.close()
                    return False, f"Account locked until {locked_until.strftime('%Y-%m-%d %H:%M:%S')}", None
                else:
                    # Clear the lock since it's expired
                    cursor.execute('UPDATE users SET locked_until = NULL WHERE id = %s', (user_id,))
                    conn.commit()
            
            # Verify password
            if not self.verify_password(password, password_hash, salt):
                # Increment failed attempts
                failed_attempts += 1
                if failed_attempts >= 5:
                    # Lock account for 30 minutes
                    lock_until = datetime.now() + timedelta(minutes=30)
                    cursor.execute('''
                        UPDATE users 
                        SET failed_login_attempts = %s, locked_until = %s
                        WHERE id = %s
                    ''', (failed_attempts, lock_until, user_id))
                    conn.commit()
                    conn.close()
                    return False, "Too many failed attempts. Account locked for 30 minutes.", None
                else:
                    cursor.execute('''
                        UPDATE users 
                        SET failed_login_attempts = %s
                        WHERE id = %s
                    ''', (failed_attempts, user_id))
                    conn.commit()
                
                conn.close()
                return False, "Invalid username/email or password", None
            
            # Reset failed attempts and update last login
            cursor.execute('''
                UPDATE users 
                SET failed_login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            user_data = {
                'id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name
            }
            
            print(f"User {username} logged in successfully")
            return True, "Login successful", user_data
            
        except pymysql.Error as e:
            print(f"Database error during authentication: {str(e)}")
            return False, f"Database error: {str(e)}", None
        except Exception as e:
            print(f"Unexpected error during authentication: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    def create_session(self, user_id):
        """Create a new session for user"""
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=7)  # Session expires in 7 days
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Deactivate old sessions
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE user_id = %s AND is_active = 1
            ''', (user_id,))
            
            # Create new session
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, %s)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
            conn.close()
            
            print(f"Session created for user ID {user_id}")
            return session_token
            
        except Exception as e:
            print(f"Session creation error: {e}")
            return None
    
    def verify_session(self, session_token):
        """Verify session token and return user data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.username, u.email, u.full_name, s.expires_at
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = %s AND s.is_active = 1 AND u.is_active = 1
            ''', (session_token,))
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return None
            
            user_id, username, email, full_name, expires_at = result
            
            # Check if session is expired
            if datetime.now() > expires_at:
                # Deactivate expired session
                cursor.execute('''
                    UPDATE user_sessions 
                    SET is_active = 0 
                    WHERE session_token = %s
                ''', (session_token,))
                conn.commit()
                conn.close()
                print(f"Session expired for token {session_token[:10]}...")
                return None
            
            conn.close()
            
            return {
                'id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name
            }
            
        except Exception as e:
            print(f"Session verification error: {e}")
            return None
    
    def logout_user(self, session_token):
        """Logout user by deactivating session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE session_token = %s
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            print(f"User logged out, session token {session_token[:10]}... deactivated")
            return True
            
        except Exception as e:
            print(f"Logout error: {e}")
            return False
    
    def save_chat_message(self, user_id, message, response):
        """Save chat message to history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chat_history (user_id, message, response)
                VALUES (%s, %s, %s)
            ''', (user_id, message, response))
            
            conn.commit()
            conn.close()
            print(f"Chat message saved for user ID {user_id}")
            return True
            
        except Exception as e:
            print(f"Chat save error: {e}")
            return False
    
    def get_chat_history(self, user_id, limit=50):
        """Get chat history for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT message, response, timestamp
                FROM chat_history
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            ''', (user_id, limit))
            
            history = cursor.fetchall()
            conn.close()
            
            print(f"Retrieved {len(history)} chat messages for user ID {user_id}")
            return history
            
        except Exception as e:
            print(f"Chat history error: {e}")
            return []
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user info
            cursor.execute('''
                SELECT username, email, full_name, created_at, last_login
                FROM users
                WHERE id = %s
            ''', (user_id,))
            
            user_info = cursor.fetchone()
            if not user_info:
                conn.close()
                return None
            
            # Get chat count
            cursor.execute('''
                SELECT COUNT(*)
                FROM chat_history
                WHERE user_id = %s
            ''', (user_id,))
            
            chat_count = cursor.fetchone()[0]
            
            # Get first chat date
            cursor.execute('''
                SELECT MIN(timestamp)
                FROM chat_history
                WHERE user_id = %s
            ''', (user_id,))
            
            first_chat = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'username': user_info[0],
                'email': user_info[1],
                'full_name': user_info[2],
                'created_at': user_info[3],
                'last_login': user_info[4],
                'total_chats': chat_count,
                'first_chat': first_chat
            }
            
        except Exception as e:
            print(f"User stats error: {e}")
            return None
    
    def delete_user_data(self, user_id):
        """Delete all user data (GDPR compliance)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete chat history
            cursor.execute('DELETE FROM chat_history WHERE user_id = %s', (user_id,))
            
            # Delete sessions
            cursor.execute('DELETE FROM user_sessions WHERE user_id = %s', (user_id,))
            
            # Delete user
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            
            conn.commit()
            conn.close()
            
            print(f"All data deleted for user ID {user_id}")
            return True
            
        except Exception as e:
            print(f"Data deletion error: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (run periodically)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            current_time = datetime.now()
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE expires_at < %s AND is_active = 1
            ''', (current_time,))
            
            cleaned = cursor.rowcount
            conn.commit()
            conn.close()
            
            if cleaned > 0:
                print(f"Cleaned up {cleaned} expired sessions")
            return cleaned
            
        except Exception as e:
            print(f"Session cleanup error: {e}")
            return 0

# Test the database functionality
if __name__ == "__main__":
    # Test with environment variables or fallback to default
    print("Testing MySQL authentication database...")
    print("Make sure MySQL is running and environment variables are set!")
    
    try:
        # Initialize the database
        auth = AuthDatabase()
        
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
            print(f"Session token: {session_token}")
            
            # Test session verification
            verified_user = auth.verify_session(session_token)
            print(f"Session verification: {verified_user}")
            
            # Test chat saving
            auth.save_chat_message(user_data['id'], "Hello", "Hi there!")
            
            # Test chat history
            history = auth.get_chat_history(user_data['id'])
            print(f"Chat history: {history}")
        
        print("Database test completed!")
        
    except Exception as e:
        print(f"Database test failed: {e}")
        print("Please check your MySQL connection and environment variables.")
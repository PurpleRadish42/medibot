#!/usr/bin/env python3
"""
Chat History Database Module for MediBot
This module provides a simple SQLite-based chat history system that can be easily migrated to MySQL later.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
import uuid


class ChatHistoryDB:
    def __init__(self, db_path="data/chat_history.db"):
        """Initialize the chat history database"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        if os.path.dirname(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize the database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table (simplified - can be extended)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chat sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL DEFAULT 'New Chat',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    metadata TEXT,  -- JSON field for additional data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id)")
            
            conn.commit()
    
    def get_or_create_user(self, username, email=None):
        """Get existing user or create a new one"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Try to get existing user
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user:
                return user['id']
            
            # Create new user
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)", 
                (username, email)
            )
            return cursor.lastrowid
    
    def create_chat_session(self, user_id, title="New Chat"):
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_sessions (id, user_id, title) VALUES (?, ?, ?)",
                (session_id, user_id, title)
            )
            conn.commit()
        
        return session_id
    
    def save_message(self, session_id, user_id, message_type, content, metadata=None):
        """Save a chat message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert metadata to JSON if provided
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO chat_messages (session_id, user_id, message_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, message_type, content, metadata_json))
            
            # Update session's updated_at timestamp
            cursor.execute("""
                UPDATE chat_sessions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (session_id,))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_user_sessions(self, user_id, limit=50):
        """Get user's chat sessions ordered by most recent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id, s.title, s.created_at, s.updated_at,
                    COUNT(m.id) as message_count,
                    MAX(m.created_at) as last_message_at
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON s.id = m.session_id
                WHERE s.user_id = ?
                GROUP BY s.id, s.title, s.created_at, s.updated_at
                ORDER BY s.updated_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'id': row['id'],
                    'title': row['title'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'message_count': row['message_count'],
                    'last_message_at': row['last_message_at']
                })
            
            return sessions
    
    def get_session_messages(self, session_id, user_id):
        """Get all messages for a specific session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_type, content, metadata, created_at
                FROM chat_messages
                WHERE session_id = ? AND user_id = ?
                ORDER BY created_at ASC
            """, (session_id, user_id))
            
            messages = []
            for row in cursor.fetchall():
                message = {
                    'type': row['message_type'],
                    'content': row['content'],
                    'timestamp': row['created_at']
                }
                
                # Parse metadata if available
                if row['metadata']:
                    try:
                        message['metadata'] = json.loads(row['metadata'])
                    except json.JSONDecodeError:
                        pass
                
                messages.append(message)
            
            return messages
    
    def update_session_title(self, session_id, user_id, title):
        """Update the title of a chat session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE chat_sessions 
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (title, session_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_session(self, session_id, user_id):
        """Delete a chat session and all its messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete messages first (due to foreign key)
            cursor.execute("DELETE FROM chat_messages WHERE session_id = ? AND user_id = ?", 
                         (session_id, user_id))
            
            # Delete session
            cursor.execute("DELETE FROM chat_sessions WHERE id = ? AND user_id = ?", 
                         (session_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_user_history(self, user_id):
        """Clear all chat history for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete all messages for user
            cursor.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
            
            # Delete all sessions for user
            cursor.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
            
            conn.commit()
            return cursor.rowcount
    
    def get_chat_history_stats(self, user_id):
        """Get statistics about user's chat history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT s.id) as total_sessions,
                    COUNT(m.id) as total_messages,
                    MIN(s.created_at) as first_chat,
                    MAX(s.updated_at) as last_chat
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON s.id = m.session_id
                WHERE s.user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_sessions': row['total_sessions'],
                    'total_messages': row['total_messages'],
                    'first_chat': row['first_chat'],
                    'last_chat': row['last_chat']
                }
            
            return None


def test_chat_history_db():
    """Test function for the chat history database"""
    print("🧪 Testing ChatHistoryDB...")
    
    # Use a test database
    db = ChatHistoryDB("test_chat_history.db")
    
    # Create a test user
    user_id = db.get_or_create_user("test_user", "test@example.com")
    print(f"✅ Created user with ID: {user_id}")
    
    # Create a chat session
    session_id = db.create_chat_session(user_id, "Test Medical Chat")
    print(f"✅ Created session with ID: {session_id}")
    
    # Add some messages
    db.save_message(session_id, user_id, "user", "Hello, I have a headache")
    db.save_message(session_id, user_id, "assistant", "I understand you have a headache. Can you describe the pain?")
    db.save_message(session_id, user_id, "user", "It's a sharp pain on the left side")
    db.save_message(session_id, user_id, "assistant", "Based on your symptoms, this could be a tension headache...")
    print("✅ Added test messages")
    
    # Get sessions
    sessions = db.get_user_sessions(user_id)
    print(f"✅ Retrieved {len(sessions)} sessions")
    
    # Get messages for session
    messages = db.get_session_messages(session_id, user_id)
    print(f"✅ Retrieved {len(messages)} messages")
    
    # Print messages
    for msg in messages:
        print(f"  {msg['type']}: {msg['content']}")
    
    # Get stats
    stats = db.get_chat_history_stats(user_id)
    print(f"✅ Stats: {stats}")
    
    # Clean up test database
    os.remove("test_chat_history.db")
    print("✅ Test completed successfully!")


if __name__ == "__main__":
    test_chat_history_db()
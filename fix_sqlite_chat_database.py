#!/usr/bin/env python3
"""
SQLite Chat Database Fix Script
Fixes chat history issues for the existing SQLite database.
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json
import traceback

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class SQLiteChatDatabaseFixer:
    def __init__(self):
        """Initialize the SQLite database fixer"""
        self.db_path = project_root / "users.db"
        self.backup_created = False
        self.migration_log = []
        
    def log(self, message, level="INFO"):
        """Log migration steps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.migration_log.append(log_entry)
        
    def diagnose_database(self):
        """Step 1: Diagnose current database schema and identify issues"""
        self.log("=== STEP 1: DATABASE DIAGNOSTICS ===")
        
        issues_found = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check chat_history table structure
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = cursor.fetchall()
            
            if not columns:
                issues_found.append("❌ chat_history table does not exist")
                self.log("❌ chat_history table does not exist", "ERROR")
            else:
                self.log(f"✅ Found chat_history table with {len(columns)} columns")
                column_names = [col[1] for col in columns]
                for col in columns:
                    self.log(f"   Column: {col[1]} ({col[2]})")
                
                # Check for missing columns for conversation support
                required_columns = ['conversation_id', 'message_type', 'title']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    issues_found.append(f"❌ Missing columns: {', '.join(missing_columns)}")
                    self.log(f"❌ Missing columns: {', '.join(missing_columns)}", "WARN")
                else:
                    self.log("✅ All conversation columns present")
            
            # Check existing data
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            chat_count = cursor.fetchone()[0]
            self.log(f"📊 Current chat history records: {chat_count}")
            
            if chat_count > 0:
                cursor.execute("""
                    SELECT user_id, COUNT(*) as msg_count, MIN(timestamp) as first_msg, MAX(timestamp) as last_msg
                    FROM chat_history 
                    GROUP BY user_id
                """)
                user_stats = cursor.fetchall()
                self.log(f"📊 Chat data by user:")
                for user_id, msg_count, first_msg, last_msg in user_stats:
                    self.log(f"   User {user_id}: {msg_count} messages ({first_msg} to {last_msg})")
            
            conn.close()
            
        except Exception as e:
            issues_found.append(f"❌ Database connection error: {e}")
            self.log(f"❌ Database diagnostics failed: {e}", "ERROR")
            traceback.print_exc()
        
        self.log(f"🔍 DIAGNOSTICS COMPLETE: Found {len(issues_found)} issues")
        return issues_found
    
    def backup_existing_data(self):
        """Step 2: Backup existing chat data before migration"""
        self.log("=== STEP 2: BACKUP EXISTING DATA ===")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if we have data to backup
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            chat_count = cursor.fetchone()[0]
            
            if chat_count == 0:
                self.log("ℹ No existing chat data to backup")
                self.backup_created = True
                conn.close()
                return True
            
            # Create JSON backup
            cursor.execute("SELECT * FROM chat_history ORDER BY timestamp")
            all_data = cursor.fetchall()
            
            backup_file = project_root / f"chat_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_data = []
            
            for row in all_data:
                backup_data.append({
                    'id': row[0],
                    'user_id': row[1], 
                    'message': row[2],
                    'response': row[3],
                    'timestamp': row[4]
                })
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            self.log(f"✅ JSON backup created: {backup_file} ({len(backup_data)} records)")
            self.backup_created = True
            
            conn.close()
            return True
            
        except Exception as e:
            self.log(f"❌ Backup failed: {e}", "ERROR")
            traceback.print_exc()
            return False
    
    def migrate_schema(self):
        """Step 3: Migrate database schema to support conversations"""
        self.log("=== STEP 3: SCHEMA MIGRATION ===")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            self.log(f"Current columns: {column_names}")
            
            # Add conversation_id column if it doesn't exist
            if 'conversation_id' not in column_names:
                self.log("Adding conversation_id column...")
                cursor.execute("ALTER TABLE chat_history ADD COLUMN conversation_id TEXT")
                self.log("✅ Added conversation_id column")
            
            # Add message_type column if it doesn't exist
            if 'message_type' not in column_names:
                self.log("Adding message_type column...")
                cursor.execute("ALTER TABLE chat_history ADD COLUMN message_type TEXT DEFAULT 'user'")
                self.log("✅ Added message_type column")
            
            # Add title column if it doesn't exist
            if 'title' not in column_names:
                self.log("Adding title column...")
                cursor.execute("ALTER TABLE chat_history ADD COLUMN title TEXT")
                self.log("✅ Added title column")
            
            # Create indexes for better performance
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_id ON chat_history(conversation_id)")
                self.log("✅ Added index on conversation_id")
            except Exception as e:
                self.log(f"⚠ Index creation warning: {e}", "WARN")
            
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_conversation ON chat_history(user_id, conversation_id, timestamp)")
                self.log("✅ Added composite index for user conversations")
            except Exception as e:
                self.log(f"⚠ Index creation warning: {e}", "WARN")
            
            conn.commit()
            conn.close()
            
            self.log("✅ Schema migration completed successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Schema migration failed: {e}", "ERROR")
            traceback.print_exc()
            return False
    
    def migrate_existing_data(self):
        """Step 4: Migrate existing chat data to new conversation format"""
        self.log("=== STEP 4: DATA MIGRATION ===")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for data that needs conversation_id
            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE conversation_id IS NULL OR conversation_id = ''")
            unmigrated_count = cursor.fetchone()[0]
            
            if unmigrated_count == 0:
                self.log("ℹ No data needs conversation migration")
                conn.close()
                return True
            
            self.log(f"📊 Found {unmigrated_count} records needing conversation migration")
            
            # Group existing messages by user and time proximity
            cursor.execute("""
                SELECT id, user_id, message, response, timestamp
                FROM chat_history 
                WHERE conversation_id IS NULL OR conversation_id = ''
                ORDER BY user_id, timestamp
            """)
            
            all_records = cursor.fetchall()
            conversation_groups = []
            current_group = []
            current_user = None
            last_timestamp = None
            
            # Group messages into conversations (within 1 hour of each other)
            for record in all_records:
                record_id, user_id, message, response, timestamp = record
                
                # Parse timestamp
                try:
                    if isinstance(timestamp, str):
                        timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        timestamp_dt = timestamp
                except:
                    timestamp_dt = datetime.now()
                
                if (current_user != user_id or 
                    (last_timestamp and timestamp_dt - last_timestamp > timedelta(hours=1))):
                    # Start new conversation
                    if current_group:
                        conversation_groups.append(current_group)
                    current_group = []
                    current_user = user_id
                
                current_group.append(record)
                last_timestamp = timestamp_dt
            
            # Add the last group
            if current_group:
                conversation_groups.append(current_group)
            
            self.log(f"📊 Grouped {len(all_records)} records into {len(conversation_groups)} conversations")
            
            # Create conversation IDs and update records
            for i, group in enumerate(conversation_groups):
                if not group:
                    continue
                    
                first_record = group[0]
                user_id = first_record[1]
                conversation_id = f"conv_{user_id}_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
                
                # Generate title from first message
                first_message = first_record[2]
                title = first_message[:50] + "..." if len(first_message) > 50 else first_message
                
                # Update all records in this conversation
                for record in group:
                    record_id = record[0]
                    cursor.execute("""
                        UPDATE chat_history 
                        SET conversation_id = ?, message_type = 'user', title = ?
                        WHERE id = ?
                    """, (conversation_id, title, record_id))
                
                self.log(f"✅ Updated conversation {conversation_id}: {len(group)} records")
            
            conn.commit()
            
            # Verify migration
            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE conversation_id IS NULL")
            remaining_null = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT conversation_id) FROM chat_history WHERE conversation_id IS NOT NULL")
            total_conversations = cursor.fetchone()[0]
            
            self.log(f"✅ Data migration completed: {total_conversations} conversations, {remaining_null} records still null")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log(f"❌ Data migration failed: {e}", "ERROR")
            traceback.print_exc()
            return False
    
    def generate_backend_code(self):
        """Step 5: Generate backend code for conversation management"""
        self.log("=== STEP 5: BACKEND CODE GENERATION ===")
        
        # Generate the auth.py additions
        auth_additions = '''
# ============================================
# ADD THESE METHODS TO AuthDatabase CLASS IN auth.py
# ============================================

def save_chat_message_with_conversation(self, user_id, message, response, conversation_id=None):
    """Save chat message to history with conversation support"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # If no conversation_id provided, create a new one
        if not conversation_id:
            import uuid
            conversation_id = f"conv_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Generate title from message
            title = message[:50] + "..." if len(message) > 50 else message
        else:
            # Get existing title
            cursor.execute("SELECT title FROM chat_history WHERE conversation_id = ? LIMIT 1", (conversation_id,))
            result = cursor.fetchone()
            title = result[0] if result else message[:50]
        
        # Save user message
        cursor.execute("""
            INSERT INTO chat_history (user_id, conversation_id, message_type, title, message, response, timestamp)
            VALUES (?, ?, 'user', ?, ?, '', datetime('now'))
        """, (user_id, conversation_id, title, message))
        
        # Save bot response
        cursor.execute("""
            INSERT INTO chat_history (user_id, conversation_id, message_type, title, message, response, timestamp)
            VALUES (?, ?, 'bot', ?, '', ?, datetime('now'))
        """, (user_id, conversation_id, title, response))
        
        conn.commit()
        conn.close()
        print(f"Chat message saved with conversation {conversation_id} for user ID {user_id}")
        return conversation_id
        
    except Exception as e:
        print(f"Chat save error: {e}")
        return None

def get_user_conversations(self, user_id):
    """Get all conversations for a user"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, title, 
                   MIN(timestamp) as first_message,
                   MAX(timestamp) as last_message,
                   COUNT(*) as message_count
            FROM chat_history
            WHERE user_id = ? AND conversation_id IS NOT NULL AND conversation_id != ''
            GROUP BY conversation_id, title
            ORDER BY last_message DESC
        """, (user_id,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        formatted_conversations = []
        for conv_id, title, first_msg, last_msg, msg_count in conversations:
            formatted_conversations.append({
                'id': conv_id,
                'title': title,
                'first_message': first_msg,
                'last_message': last_msg,
                'message_count': msg_count
            })
        
        print(f"Retrieved {len(formatted_conversations)} conversations for user {user_id}")
        return formatted_conversations
        
    except Exception as e:
        print(f"Get conversations error: {e}")
        return []

def get_conversation_messages(self, conversation_id, user_id):
    """Get all messages in a specific conversation"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message, response, timestamp, message_type
            FROM chat_history
            WHERE conversation_id = ? AND user_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id, user_id))
        
        messages = cursor.fetchall()
        conn.close()
        
        formatted_messages = []
        for message, response, timestamp, msg_type in messages:
            if message and message.strip():
                formatted_messages.append({
                    'content': message,
                    'isUser': True,
                    'timestamp': timestamp
                })
            if response and response.strip():
                formatted_messages.append({
                    'content': response,
                    'isUser': False,
                    'timestamp': timestamp
                })
        
        print(f"Retrieved {len(formatted_messages)} messages for conversation {conversation_id}")
        return formatted_messages
        
    except Exception as e:
        print(f"Get conversation messages error: {e}")
        return []

def delete_conversation(self, conversation_id, user_id):
    """Delete a specific conversation"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE conversation_id = ? AND user_id = ?", 
                      (conversation_id, user_id))
        
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
        
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Cleared all chats for user {user_id}: {deleted_count} messages deleted")
        return deleted_count
        
    except Exception as e:
        print(f"Clear chats error: {e}")
        return 0
'''
        
        # Generate the main.py API endpoints
        main_additions = '''
# ============================================
# ADD THESE API ENDPOINTS TO main.py
# ============================================

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
'''
        
        # Write the files
        auth_file = project_root / "auth_additions.py"
        with open(auth_file, 'w') as f:
            f.write(auth_additions)
        
        main_file = project_root / "main_additions.py"
        with open(main_file, 'w') as f:
            f.write(main_additions)
        
        self.log(f"✅ Backend code generated:")
        self.log(f"   - {auth_file}")
        self.log(f"   - {main_file}")
        
        return True
    
    def run_complete_fix(self):
        """Run the complete database fix process"""
        self.log("🚀 STARTING SQLITE CHAT DATABASE FIX")
        self.log("=" * 60)
        
        success = True
        
        # Step 1: Diagnose issues
        issues = self.diagnose_database()
        if issues:
            self.log(f"Found {len(issues)} issues to fix:")
            for issue in issues:
                self.log(f"  {issue}")
        
        # Step 2: Backup data
        if success:
            success = self.backup_existing_data()
        
        # Step 3: Migrate schema
        if success:
            success = self.migrate_schema()
        
        # Step 4: Migrate existing data
        if success:
            success = self.migrate_existing_data()
        
        # Step 5: Generate backend code
        if success:
            success = self.generate_backend_code()
        
        self.log("=" * 60)
        if success:
            self.log("🎉 SQLITE CHAT DATABASE FIX COMPLETED SUCCESSFULLY!")
            self.log("")
            self.log("📋 NEXT STEPS:")
            self.log("1. Apply the generated backend code to auth.py and main.py")
            self.log("2. Update the frontend to remove the 'not implemented' error")
            self.log("3. Fix the clear all chats function to call the backend API")
            self.log("4. Test the conversation functionality")
        else:
            self.log("❌ SQLITE CHAT DATABASE FIX FAILED!")
            if self.backup_created:
                self.log("✅ Your data backup is safe.")
        
        # Save migration log
        log_file = project_root / f"sqlite_migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w') as f:
            f.write("\n".join(self.migration_log))
        
        self.log(f"📄 Migration log saved: {log_file}")
        
        return success

def main():
    """Main function to run the SQLite chat database fix"""
    print("🏥 Medical Chatbot - SQLite Chat Database Fix Script")
    print("=" * 50)
    
    try:
        fixer = SQLiteChatDatabaseFixer()
        success = fixer.run_complete_fix()
        
        if success:
            print("\n✅ Database fix completed successfully!")
            print("See the generated files for next steps.")
        else:
            print("\n❌ Database fix failed!")
            
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
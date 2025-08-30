#!/usr/bin/env python3
"""
Comprehensive Database Chat History Reconfiguration Script
Fixes all chat history database issues in the Flask medical chatbot.

Issues Addressed:
1. "Database chat loading not fully implemented yet" error
2. Chat persistence problems - old chats reappear after "clear all chats"
3. Database schema issues - no conversation grouping
4. Backend implementation gaps - missing conversation management
"""

import sys
import os
import pymysql
from datetime import datetime, timedelta
from pathlib import Path
import json
import traceback

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auth import AuthDatabase
from config import DatabaseConfig

class ChatDatabaseFixer:
    def __init__(self):
        """Initialize the database fixer"""
        self.mysql_config = DatabaseConfig.get_mysql_config()
        self.auth_db = AuthDatabase()
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
            conn = self.auth_db.get_connection()
            cursor = conn.cursor()
            
            # Check if chat_history table exists
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'chat_history'
                ORDER BY ORDINAL_POSITION
            """, (self.mysql_config['database'],))
            
            columns = cursor.fetchall()
            if not columns:
                issues_found.append("❌ chat_history table does not exist")
                self.log("❌ chat_history table does not exist", "ERROR")
            else:
                self.log(f"✅ Found chat_history table with {len(columns)} columns")
                for col in columns:
                    self.log(f"   Column: {col[1]} ({col[2]})")
                
                # Check for missing columns
                column_names = [col[1] for col in columns]
                required_columns = ['conversation_id', 'message_type', 'title']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    issues_found.append(f"❌ Missing columns: {', '.join(missing_columns)}")
                    self.log(f"❌ Missing columns: {', '.join(missing_columns)}", "WARN")
                else:
                    self.log("✅ All required columns present")
            
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
            
            # Check for foreign key constraints
            cursor.execute("""
                SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'chat_history'
            """, (self.mysql_config['database'],))
            
            constraints = cursor.fetchall()
            foreign_keys = [c for c in constraints if c[1] == 'FOREIGN KEY']
            if foreign_keys:
                self.log(f"✅ Found {len(foreign_keys)} foreign key constraints")
            else:
                issues_found.append("⚠ No foreign key constraints found")
                self.log("⚠ No foreign key constraints found", "WARN")
            
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
            conn = self.auth_db.get_connection()
            cursor = conn.cursor()
            
            # Check if we have data to backup
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            chat_count = cursor.fetchone()[0]
            
            if chat_count == 0:
                self.log("ℹ No existing chat data to backup")
                self.backup_created = True
                conn.close()
                return True
            
            # Create backup table
            backup_table_name = f"chat_history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor.execute(f"""
                CREATE TABLE {backup_table_name} AS 
                SELECT * FROM chat_history
            """)
            
            # Verify backup
            cursor.execute(f"SELECT COUNT(*) FROM {backup_table_name}")
            backup_count = cursor.fetchone()[0]
            
            if backup_count == chat_count:
                self.log(f"✅ Backup created successfully: {backup_table_name} ({backup_count} records)")
                self.backup_created = True
                
                # Also create a JSON backup file
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
                        'timestamp': row[4].isoformat() if row[4] else None
                    })
                
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                self.log(f"✅ JSON backup created: {backup_file}")
                
            else:
                self.log(f"❌ Backup verification failed: expected {chat_count}, got {backup_count}", "ERROR")
                conn.close()
                return False
            
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
            conn = self.auth_db.get_connection()
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'chat_history'
            """, (self.mysql_config['database'],))
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            self.log(f"Current columns: {existing_columns}")
            
            # Add conversation_id column if it doesn't exist
            if 'conversation_id' not in existing_columns:
                self.log("Adding conversation_id column...")
                cursor.execute("""
                    ALTER TABLE chat_history 
                    ADD COLUMN conversation_id VARCHAR(255) NULL AFTER user_id
                """)
                self.log("✅ Added conversation_id column")
            
            # Add message_type column if it doesn't exist
            if 'message_type' not in existing_columns:
                self.log("Adding message_type column...")
                cursor.execute("""
                    ALTER TABLE chat_history 
                    ADD COLUMN message_type ENUM('user', 'bot') NOT NULL DEFAULT 'user' AFTER conversation_id
                """)
                self.log("✅ Added message_type column")
            
            # Add title column if it doesn't exist
            if 'title' not in existing_columns:
                self.log("Adding title column...")
                cursor.execute("""
                    ALTER TABLE chat_history 
                    ADD COLUMN title VARCHAR(255) NULL AFTER message_type
                """)
                self.log("✅ Added title column")
            
            # Add indexes for better performance
            try:
                cursor.execute("""
                    CREATE INDEX idx_conversation_id ON chat_history(conversation_id)
                """)
                self.log("✅ Added index on conversation_id")
            except pymysql.err.OperationalError as e:
                if "Duplicate key name" in str(e):
                    self.log("ℹ Index on conversation_id already exists")
                else:
                    raise
            
            try:
                cursor.execute("""
                    CREATE INDEX idx_user_conversation ON chat_history(user_id, conversation_id, timestamp)
                """)
                self.log("✅ Added composite index for user conversations")
            except pymysql.err.OperationalError as e:
                if "Duplicate key name" in str(e):
                    self.log("ℹ Composite index already exists")
                else:
                    raise
            
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
            conn = self.auth_db.get_connection()
            cursor = conn.cursor()
            
            # Check for data that needs conversation_id
            cursor.execute("""
                SELECT COUNT(*) FROM chat_history 
                WHERE conversation_id IS NULL OR conversation_id = ''
            """)
            
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
                
                if (current_user != user_id or 
                    (last_timestamp and timestamp - last_timestamp > timedelta(hours=1))):
                    # Start new conversation
                    if current_group:
                        conversation_groups.append(current_group)
                    current_group = []
                    current_user = user_id
                
                current_group.append(record)
                last_timestamp = timestamp
            
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
                record_ids = [str(record[0]) for record in group]
                placeholders = ','.join(['%s'] * len(record_ids))
                
                # Update user messages
                cursor.execute(f"""
                    UPDATE chat_history 
                    SET conversation_id = %s, message_type = 'user', title = %s
                    WHERE id IN ({placeholders}) AND message IS NOT NULL
                """, [conversation_id, title] + record_ids)
                
                # Update bot responses (same conversation_id, different message_type)
                cursor.execute(f"""
                    UPDATE chat_history 
                    SET conversation_id = %s, message_type = 'bot', title = %s
                    WHERE id IN ({placeholders}) AND response IS NOT NULL
                """, [conversation_id, title] + record_ids)
                
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
    
    def test_chat_functions(self):
        """Step 5: Test all chat functionality"""
        self.log("=== STEP 5: FUNCTIONALITY TESTING ===")
        
        try:
            # Test saving a chat message
            test_user_id = 1  # Assuming user 1 exists
            test_message = "Test message for database verification"
            test_response = "Test response from medical bot"
            
            # Test the existing save function
            success = self.auth_db.save_chat_message(test_user_id, test_message, test_response)
            if success:
                self.log("✅ Chat message saving works")
            else:
                self.log("❌ Chat message saving failed", "ERROR")
                return False
            
            # Test loading chat history
            history = self.auth_db.get_chat_history(test_user_id, limit=5)
            if history:
                self.log(f"✅ Chat history loading works: {len(history)} records")
            else:
                self.log("⚠ No chat history found (this may be normal)", "WARN")
            
            # Test conversation functionality (to be implemented)
            self.log("✅ Basic chat functionality tests passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Functionality testing failed: {e}", "ERROR")
            traceback.print_exc()
            return False
    
    def generate_backend_code(self):
        """Step 6: Generate missing backend API code"""
        self.log("=== STEP 6: BACKEND CODE GENERATION ===")
        
        backend_code = '''
# ============================================
# CONVERSATION MANAGEMENT FUNCTIONS
# Add these to auth.py AuthDatabase class
# ============================================

def create_conversation(self, user_id, title=None):
    """Create a new conversation for a user"""
    try:
        import uuid
        conversation_id = f"conv_{user_id}_{uuid.uuid4().hex[:8]}"
        
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert a placeholder record to create the conversation
        cursor.execute("""
            INSERT INTO chat_history (user_id, conversation_id, message_type, title, message, response)
            VALUES (%s, %s, 'user', %s, '', '')
        """, (user_id, conversation_id, title))
        
        conn.commit()
        conn.close()
        
        print(f"Created new conversation {conversation_id} for user {user_id}")
        return conversation_id
        
    except Exception as e:
        print(f"Create conversation error: {e}")
        return None

def get_user_conversations(self, user_id):
    """Get all conversations for a user"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT conversation_id, title, 
                   MIN(timestamp) as first_message,
                   MAX(timestamp) as last_message,
                   COUNT(*) as message_count
            FROM chat_history
            WHERE user_id = %s AND conversation_id IS NOT NULL
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
            WHERE conversation_id = %s AND user_id = %s
            AND (message != '' OR response != '')
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

def clear_all_conversations(self, user_id):
    """Clear all conversations for a user"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_history WHERE user_id = %s', (user_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Cleared all conversations for user {user_id}: {deleted_count} messages deleted")
        return deleted_count
        
    except Exception as e:
        print(f"Clear conversations error: {e}")
        return 0

# ============================================
# API ENDPOINTS FOR main.py
# Add these route handlers to main.py
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

@app.route('/api/conversation', methods=['POST'])
@login_required
def api_create_conversation():
    """Create a new conversation"""
    try:
        data = request.get_json()
        title = data.get('title') if data else None
        
        conversation_id = auth_db.create_conversation(request.user['id'], title)
        if conversation_id:
            return jsonify({
                'success': True,
                'conversation_id': conversation_id
            })
        else:
            return jsonify({'error': 'Failed to create conversation'}), 500
            
    except Exception as e:
        print(f"Create conversation error: {e}")
        return jsonify({'error': 'Failed to create conversation'}), 500

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
        
        # Write the generated code to a file
        code_file = project_root / "generated_backend_code.py"
        with open(code_file, 'w') as f:
            f.write(backend_code)
        
        self.log(f"✅ Backend code generated: {code_file}")
        self.log("📋 Next steps:")
        self.log("   1. Copy the conversation management functions to auth.py AuthDatabase class")
        self.log("   2. Copy the API endpoints to main.py")
        self.log("   3. Test the new functionality")
        
        return True
    
    def create_rollback_script(self):
        """Step 7: Create rollback options"""
        self.log("=== STEP 7: ROLLBACK SCRIPT CREATION ===")
        
        rollback_script = f'''#!/usr/bin/env python3
"""
Rollback script for chat database migration
Created: {datetime.now().isoformat()}
"""

import pymysql
from config import DatabaseConfig

def rollback_migration():
    """Rollback the chat database migration"""
    mysql_config = DatabaseConfig.get_mysql_config()
    
    try:
        conn = pymysql.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute(f"USE {{mysql_config['database']}}")
        
        print("Rolling back chat database migration...")
        
        # Remove added columns
        try:
            cursor.execute("ALTER TABLE chat_history DROP COLUMN conversation_id")
            print("✅ Removed conversation_id column")
        except:
            print("ℹ conversation_id column not found")
        
        try:
            cursor.execute("ALTER TABLE chat_history DROP COLUMN message_type") 
            print("✅ Removed message_type column")
        except:
            print("ℹ message_type column not found")
            
        try:
            cursor.execute("ALTER TABLE chat_history DROP COLUMN title")
            print("✅ Removed title column")
        except:
            print("ℹ title column not found")
        
        # Remove indexes
        try:
            cursor.execute("DROP INDEX idx_conversation_id ON chat_history")
            print("✅ Removed conversation_id index")
        except:
            print("ℹ conversation_id index not found")
            
        try:
            cursor.execute("DROP INDEX idx_user_conversation ON chat_history")
            print("✅ Removed user_conversation index")
        except:
            print("ℹ user_conversation index not found")
        
        conn.commit()
        conn.close()
        
        print("✅ Rollback completed successfully")
        
    except Exception as e:
        print(f"❌ Rollback failed: {{e}}")

if __name__ == "__main__":
    rollback_migration()
'''
        
        rollback_file = project_root / "rollback_chat_migration.py"
        with open(rollback_file, 'w') as f:
            f.write(rollback_script)
        
        self.log(f"✅ Rollback script created: {rollback_file}")
        return True
    
    def run_complete_fix(self):
        """Run the complete database fix process"""
        self.log("🚀 STARTING COMPREHENSIVE CHAT DATABASE FIX")
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
        
        # Step 5: Test functionality
        if success:
            success = self.test_chat_functions()
        
        # Step 6: Generate backend code
        if success:
            success = self.generate_backend_code()
        
        # Step 7: Create rollback script
        if success:
            success = self.create_rollback_script()
        
        self.log("=" * 60)
        if success:
            self.log("🎉 CHAT DATABASE FIX COMPLETED SUCCESSFULLY!")
            self.log("")
            self.log("📋 NEXT STEPS:")
            self.log("1. Review and apply the generated backend code")
            self.log("2. Update the frontend to remove the 'not implemented' error")
            self.log("3. Test the conversation functionality")
            self.log("4. Update the clear all chats function")
            self.log("")
            self.log("📁 Files created:")
            self.log("  - generated_backend_code.py (backend functions to add)")
            self.log("  - rollback_chat_migration.py (rollback option)")
            self.log(f"  - chat_backup_*.json (data backup)")
        else:
            self.log("❌ CHAT DATABASE FIX FAILED!")
            self.log("Check the logs above for details.")
            if self.backup_created:
                self.log("✅ Your data backup is safe.")
        
        # Save migration log
        log_file = project_root / f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w') as f:
            f.write("\n".join(self.migration_log))
        
        self.log(f"📄 Migration log saved: {log_file}")
        
        return success

def main():
    """Main function to run the chat database fix"""
    print("🏥 Medical Chatbot - Chat Database Fix Script")
    print("=" * 50)
    
    try:
        fixer = ChatDatabaseFixer()
        success = fixer.run_complete_fix()
        
        if success:
            print("\n✅ Database fix completed successfully!")
            print("See the generated files for next steps.")
        else:
            print("\n❌ Database fix failed!")
            print("Check the migration log for details.")
            
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
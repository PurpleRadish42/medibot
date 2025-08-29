#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to MySQL
"""
import sqlite3
import pymysql
import os
from datetime import datetime
from config import DatabaseConfig

def migrate_sqlite_to_mysql(sqlite_db_path="users.db"):
    """Migrate data from SQLite to MySQL"""
    
    print("🔄 Starting SQLite to MySQL migration...")
    
    # Check if SQLite database exists
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database '{sqlite_db_path}' not found!")
        return False
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to MySQL
        mysql_config = DatabaseConfig.get_mysql_config()
        mysql_conn = pymysql.connect(**mysql_config)
        mysql_cursor = mysql_conn.cursor()
        
        # Select MySQL database
        mysql_cursor.execute(f"USE {mysql_config['database']}")
        
        print("✅ Connected to both databases")
        
        # Migrate users table
        print("\n📋 Migrating users...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        # Get column names from SQLite
        sqlite_cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in sqlite_cursor.fetchall()]
        
        migrated_users = 0
        for user in users:
            try:
                # Create user dict
                user_dict = dict(zip(columns, user))
                
                # Check if user already exists in MySQL
                mysql_cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                                   (user_dict['username'], user_dict['email']))
                if mysql_cursor.fetchone():
                    print(f"⚠️  User {user_dict['username']} already exists, skipping...")
                    continue
                
                # Insert user into MySQL
                mysql_cursor.execute('''
                    INSERT INTO users (username, email, password_hash, salt, full_name, 
                                     created_at, last_login, is_active, failed_login_attempts, locked_until)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    user_dict['username'], user_dict['email'], user_dict['password_hash'],
                    user_dict['salt'], user_dict['full_name'], user_dict['created_at'],
                    user_dict['last_login'], user_dict['is_active'], 
                    user_dict['failed_login_attempts'], user_dict['locked_until']
                ))
                
                migrated_users += 1
                print(f"✅ Migrated user: {user_dict['username']}")
                
            except Exception as e:
                print(f"❌ Error migrating user {user_dict.get('username', 'unknown')}: {e}")
        
        print(f"📊 Migrated {migrated_users} users")
        
        # Migrate user_sessions table
        print("\n🔑 Migrating user sessions...")
        sqlite_cursor.execute("SELECT * FROM user_sessions")
        sessions = sqlite_cursor.fetchall()
        
        # Get column names from SQLite
        sqlite_cursor.execute("PRAGMA table_info(user_sessions)")
        session_columns = [column[1] for column in sqlite_cursor.fetchall()]
        
        migrated_sessions = 0
        for session in sessions:
            try:
                session_dict = dict(zip(session_columns, session))
                
                # Find corresponding MySQL user ID
                mysql_cursor.execute("SELECT id FROM users WHERE id = %s", (session_dict['user_id'],))
                mysql_user = mysql_cursor.fetchone()
                
                if not mysql_user:
                    print(f"⚠️  User ID {session_dict['user_id']} not found in MySQL, skipping session...")
                    continue
                
                # Insert session into MySQL
                mysql_cursor.execute('''
                    INSERT INTO user_sessions (user_id, session_token, created_at, expires_at, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    session_dict['user_id'], session_dict['session_token'],
                    session_dict['created_at'], session_dict['expires_at'],
                    session_dict['is_active']
                ))
                
                migrated_sessions += 1
                
            except Exception as e:
                print(f"❌ Error migrating session: {e}")
        
        print(f"📊 Migrated {migrated_sessions} sessions")
        
        # Migrate chat_history table
        print("\n💬 Migrating chat history...")
        sqlite_cursor.execute("SELECT * FROM chat_history")
        chats = sqlite_cursor.fetchall()
        
        # Get column names from SQLite
        sqlite_cursor.execute("PRAGMA table_info(chat_history)")
        chat_columns = [column[1] for column in sqlite_cursor.fetchall()]
        
        migrated_chats = 0
        for chat in chats:
            try:
                chat_dict = dict(zip(chat_columns, chat))
                
                # Find corresponding MySQL user ID
                mysql_cursor.execute("SELECT id FROM users WHERE id = %s", (chat_dict['user_id'],))
                mysql_user = mysql_cursor.fetchone()
                
                if not mysql_user:
                    print(f"⚠️  User ID {chat_dict['user_id']} not found in MySQL, skipping chat...")
                    continue
                
                # Insert chat into MySQL
                mysql_cursor.execute('''
                    INSERT INTO chat_history (user_id, message, response, timestamp)
                    VALUES (%s, %s, %s, %s)
                ''', (
                    chat_dict['user_id'], chat_dict['message'],
                    chat_dict['response'], chat_dict['timestamp']
                ))
                
                migrated_chats += 1
                
            except Exception as e:
                print(f"❌ Error migrating chat: {e}")
        
        print(f"📊 Migrated {migrated_chats} chat messages")
        
        # Commit all changes
        mysql_conn.commit()
        
        # Close connections
        sqlite_conn.close()
        mysql_conn.close()
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"   Users: {migrated_users}")
        print(f"   Sessions: {migrated_sessions}")
        print(f"   Chat messages: {migrated_chats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def backup_sqlite_database(sqlite_db_path="users.db", backup_path=None):
    """Create a backup of the SQLite database before migration"""
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database '{sqlite_db_path}' not found!")
        return False
    
    if backup_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"users_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2(sqlite_db_path, backup_path)
        print(f"✅ SQLite database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 SQLite to MySQL Migration Tool")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"   export {var}=your_value")
        exit(1)
    
    # Backup SQLite database
    if backup_sqlite_database():
        print("✅ Backup completed")
    else:
        print("❌ Backup failed, stopping migration")
        exit(1)
    
    # Run migration
    if migrate_sqlite_to_mysql():
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the application with MySQL")
        print("2. If everything works, you can remove the SQLite database")
        print("3. Update your production environment with MySQL credentials")
    else:
        print("❌ Migration failed!")
        exit(1)
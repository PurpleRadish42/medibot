#!/usr/bin/env python3
"""
MySQL Database Viewer Script
"""
import pymysql
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import configuration
try:
    from config import DatabaseConfig
    mysql_config = DatabaseConfig.get_mysql_config()
    print("✅ Using config.py for database configuration")
except ImportError:
    print("⚠️  config.py not found, using environment variables directly")
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USERNAME', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'medibot'),
        'charset': 'utf8mb4'
    }

# Add SSL configuration for online databases like DigitalOcean
ssl_enabled = os.getenv('MYSQL_SSL_ENABLED', 'true').lower() == 'true'
if ssl_enabled:
    mysql_config['ssl'] = {'ssl_disabled': False}
    ssl_ca = os.getenv('MYSQL_SSL_CA')
    if ssl_ca:
        mysql_config['ssl']['ca'] = ssl_ca
    print("🔒 SSL connection enabled")

def check_env_variables():
    """Check if required environment variables are set"""
    required_vars = ['MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease add the following to your .env file:")
        print("MYSQL_HOST=your_mysql_host")
        print("MYSQL_USERNAME=your_username")
        print("MYSQL_PASSWORD=your_password")
        print("MYSQL_DATABASE=your_database")
        print("MYSQL_PORT=3306")
        print("MYSQL_SSL_ENABLED=true")
        return False
    
    return True

def show_database_info():
    """Show database connection information"""
    print("📋 Database Configuration:")
    print(f"   Host: {mysql_config['host']}")
    print(f"   Port: {mysql_config['port']}")
    print(f"   Database: {mysql_config['database']}")
    print(f"   Username: {mysql_config['user']}")
    print(f"   SSL: {'Enabled' if ssl_enabled else 'Disabled'}")

def main():
    print("🗃️ MySQL Database Contents")
    print("="*50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found in current directory")
        print("Please create a .env file with your MySQL database credentials")
        return
    
    # Check required environment variables
    if not check_env_variables():
        return
    
    # Show database configuration
    show_database_info()
    print()
    
    try:
        # Connect to MySQL
        conn = pymysql.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Select the database
        cursor.execute(f"USE {mysql_config['database']}")
        print("✅ Connected to MySQL database")
        print()
        
        # Show all tables
        print("📊 TABLES:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f" - {table[0]}: {count} records")
        print("-" * 40)
        
        # Show all users
        print("\n👥 USERS:")
        try:
            cursor.execute("SELECT id, username, email, full_name, created_at FROM users ORDER BY created_at DESC")
            users = cursor.fetchall()
            
            if users:
                for user in users:
                    print(f" ID: {user[0]} | Username: {user[1]} | Email: {user[2]}")
                    print(f" Name: {user[3]} | Created: {user[4]}")
                    print("-" * 40)
            else:
                print(" No users found")
        except Exception as e:
            print(f" Error fetching users: {e}")
        
        # Show chat count by user
        print(f"\n💬 CHAT MESSAGES:")
        try:
            cursor.execute("""
                SELECT u.username, COUNT(ch.id) as message_count 
                FROM users u 
                LEFT JOIN chat_history ch ON u.id = ch.user_id 
                GROUP BY u.id, u.username 
                ORDER BY message_count DESC
            """)
            chat_stats = cursor.fetchall()
            
            total_messages = 0
            if chat_stats:
                for stat in chat_stats:
                    print(f" {stat[0]}: {stat[1]} messages")
                    total_messages += stat[1]
                print(f" Total messages: {total_messages}")
            else:
                print(" No chat messages found")
        except Exception as e:
            print(f" Error fetching chat stats: {e}")
        
        # Show active sessions
        print(f"\n🔑 USER SESSIONS:")
        try:
            cursor.execute("""
                SELECT u.username, us.created_at, us.expires_at, us.is_active
                FROM user_sessions us
                JOIN users u ON us.user_id = u.id
                ORDER BY us.created_at DESC
            """)
            sessions = cursor.fetchall()
            
            active_count = 0
            total_count = 0
            
            if sessions:
                for session in sessions:
                    status = "🟢 Active" if session[3] else "🔴 Inactive"
                    print(f" {session[0]}: {status} | Created: {session[1]} | Expires: {session[2]}")
                    if session[3]:
                        active_count += 1
                    total_count += 1
                
                print("-" * 40)
                print(f" Active sessions: {active_count}/{total_count}")
            else:
                print(" No sessions found")
        except Exception as e:
            print(f" Error fetching sessions: {e}")
        
        # Show recent activity
        print(f"\n📈 RECENT ACTIVITY:")
        try:
            cursor.execute("""
                SELECT u.username, ch.message, ch.timestamp
                FROM chat_history ch
                JOIN users u ON ch.user_id = u.id
                ORDER BY ch.timestamp DESC
                LIMIT 5
            """)
            recent_chats = cursor.fetchall()
            
            if recent_chats:
                for chat in recent_chats:
                    message_preview = chat[1][:50] + "..." if len(chat[1]) > 50 else chat[1]
                    print(f" {chat[0]}: '{message_preview}' - {chat[2]}")
            else:
                print(" No recent activity found")
        except Exception as e:
            print(f" Error fetching recent activity: {e}")
        
        conn.close()
        print(f"\n✅ Database inspection completed!")
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure:")
        print("1. MySQL server is running")
        print("2. Environment variables in .env are correct")
        print("3. Database exists and you have proper permissions")
        print("4. SSL is properly configured for online databases")

if __name__ == "__main__":
    main()
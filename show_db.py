import pymysql
from pathlib import Path
import os

# Import configuration
try:
    from config import DatabaseConfig
    mysql_config = DatabaseConfig.get_mysql_config()
except ImportError:
    print("Warning: config.py not found, using environment variables directly")
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USERNAME', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'medibot'),
        'charset': 'utf8mb4'
    }

print("🗃️ MySQL Database Contents")
print("="*50)

try:
    conn = pymysql.connect(**mysql_config)
    cursor = conn.cursor()
    
    # Select the database
    cursor.execute(f"USE {mysql_config['database']}")
    
    # Show all users
    print("\n👥 USERS:")
    cursor.execute("SELECT id, username, email, full_name, created_at FROM users")
    users = cursor.fetchall()
    
    for user in users:
        print(f"  ID: {user[0]} | Username: {user[1]} | Email: {user[2]}")
        print(f"  Name: {user[3]} | Created: {user[4]}")
        print("-" * 40)
    
    # Show chat count
    print(f"\n💬 CHAT MESSAGES:")
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    chat_count = cursor.fetchone()[0]
    print(f"  Total messages: {chat_count}")
    
    # Show sessions count
    print(f"\n🔑 ACTIVE SESSIONS:")
    cursor.execute("SELECT COUNT(*) FROM user_sessions WHERE is_active = 1")
    session_count = cursor.fetchone()[0]
    print(f"  Active sessions: {session_count}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure MySQL is running and environment variables are set correctly.")
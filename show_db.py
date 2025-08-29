import sqlite3
from pathlib import Path

# Your database path
db_path = "users.db"

print("🗃️ SQLite Database Contents")
print("="*50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
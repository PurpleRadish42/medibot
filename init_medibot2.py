#!/usr/bin/env python3
"""
Database initialization script for medibot2 MySQL database
Run this script to set up the new database and tables
"""

import os
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def init_medibot2_database():
    """Initialize medibot2 MySQL database and tables"""
    
    print("🔧 Initializing medibot2 MySQL database...")
    
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USERNAME', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'charset': 'utf8mb4',
        'autocommit': False
    }
    
    database_name = os.getenv('MYSQL_DATABASE', 'medibot2')
    
    try:
        # Connect to MySQL server (without selecting database)
        conn = pymysql.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"✅ Database '{database_name}' created/verified")
        
        # Use the database
        cursor.execute(f"USE {database_name}")
        
        # Create users table
        print("📋 Creating users table...")
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
        print("📋 Creating user_sessions table...")
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
        print("📋 Creating chat_history table...")
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
        
        # Create doctors table
        print("📋 Creating doctors table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                speciality VARCHAR(100) NOT NULL,
                profile_url TEXT,
                name VARCHAR(200) NOT NULL,
                degree VARCHAR(100),
                year_of_experience INT,
                location VARCHAR(200),
                dp_score DECIMAL(3,1),
                npv INT,
                consultation_fee INT,
                google_map_link TEXT,
                scraped_at DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_city (city),
                INDEX idx_speciality (speciality),
                INDEX idx_name (name),
                INDEX idx_city_speciality (city, speciality)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Doctors table created/verified")
        
        # Show table information
        print("\n📊 Database Schema Information:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   📋 Table: {table[0]}")
        
        # Show table counts
        print("\n📈 Table Statistics:")
        for table in ['users', 'user_sessions', 'chat_history', 'doctors']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ medibot2 database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_medibot2_connection():
    """Test medibot2 database connection"""
    print("\n🧪 Testing medibot2 database connection...")
    
    try:
        from medibot2_auth import MedibotAuthDatabase
        
        # Initialize the auth database
        auth_db = MedibotAuthDatabase()
        print("✅ medibot2 connection successful")
        
        # Test basic functionality
        print("🧪 Testing basic functionality...")
        
        # Try to get user conversations for a non-existent user
        conversations = auth_db.get_user_conversations(999)
        print(f"✅ Get conversations test: {len(conversations)} conversations")
        
        return True
        
    except Exception as e:
        print(f"❌ medibot2 connection failed: {e}")
        return False

def show_database_info():
    """Show database configuration info"""
    
    print("📋 medibot2 Database Configuration:")
    
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'database': os.getenv('MYSQL_DATABASE', 'medibot2'),
        'user': os.getenv('MYSQL_USERNAME', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
    }
    
    print(f"   Host: {mysql_config['host']}")
    print(f"   Port: {mysql_config['port']}")
    print(f"   Database: {mysql_config['database']}")
    print(f"   Username: {mysql_config['user']}")
    print(f"   Password: {'*' * len(mysql_config['password']) if mysql_config['password'] else 'Not set'}")

def check_env_variables():
    """Check if all required environment variables are loaded"""
    
    required_vars = ['MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_DATABASE']
    optional_vars = ['MYSQL_PASSWORD', 'MYSQL_PORT']
    
    print("🔍 Checking environment variables:")
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            all_good = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if var == 'MYSQL_PASSWORD':
                print(f"   ✅ {var}: {'*' * len(value)}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚠️  {var}: Using default")
    
    return all_good

if __name__ == "__main__":
    print("🔧 medibot2 Database Initialization")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found in current directory")
        print("Please create a .env file with your database credentials")
        print("\nExample .env file:")
        print("MYSQL_HOST=your_mysql_host")
        print("MYSQL_USERNAME=your_username")
        print("MYSQL_PASSWORD=your_password")
        print("MYSQL_DATABASE=medibot2")
        exit(1)
    
    # Check environment variables
    env_ok = check_env_variables()
    if not env_ok:
        print("\n❌ Missing required environment variables")
        print("Please check your .env file")
        exit(1)
    
    # Show configuration
    show_database_info()
    
    # Initialize database
    success = init_medibot2_database()
    
    if success:
        # Test connection
        test_success = test_medibot2_connection()
        
        if test_success:
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Run the main application: python main.py")
            print("2. Register a new user account")
            print("3. Start chatting with the medical AI!")
        else:
            print("\n⚠️  Database created but connection test failed")
            print("Please check your configuration")
    else:
        print("\n❌ Database initialization failed")
        print("Please check your MySQL server and credentials")
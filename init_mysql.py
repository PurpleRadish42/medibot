#!/usr/bin/env python3
"""
Database initialization script for MySQL
"""
import os
import pymysql
from dotenv import load_dotenv
from config import DatabaseConfig

# Load environment variables from .env file
load_dotenv()

def init_mysql_database():
    """Initialize MySQL database and tables"""
    
    print("🔧 Initializing MySQL database...")
    
    mysql_config = DatabaseConfig.get_mysql_config()
    
    try:
        # Connect to MySQL server (without selecting database)
        server_config = mysql_config.copy()
        database_name = server_config.pop('database')
        
        # Add SSL configuration for online databases
        ssl_enabled = os.getenv('MYSQL_SSL_ENABLED', 'true').lower() == 'true'
        if ssl_enabled:
            server_config['ssl'] = {
                'ssl_disabled': False
            }
            # Add custom SSL cert if provided
            ssl_ca = os.getenv('MYSQL_SSL_CA')
            if ssl_ca:
                server_config['ssl']['ca'] = ssl_ca
        
        conn = pymysql.connect(**server_config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"✅ Database '{database_name}' created/verified")
        
        # Create user if needed (optional)
        try:
            username = mysql_config['user']
            password = mysql_config['password']
            
            if username != 'root' and password:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{password}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'%'")
                cursor.execute("FLUSH PRIVILEGES")
                print(f"✅ User '{username}' created/verified with privileges")
        except Exception as e:
            print(f"⚠️  User creation skipped: {e}")
        
        cursor.close()
        conn.close()
        
        # Now initialize tables using AuthDatabase
        print("🔧 Initializing tables...")
        from auth import AuthDatabase
        auth_db = AuthDatabase()
        print("✅ All tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_mysql_connection():
    """Test MySQL connection"""
    
    print("🧪 Testing MySQL connection...")
    
    try:
        mysql_config = DatabaseConfig.get_mysql_config()
        
        # Add SSL configuration for online databases
        ssl_enabled = os.getenv('MYSQL_SSL_ENABLED', 'true').lower() == 'true'
        if ssl_enabled:
            mysql_config['ssl'] = {
                'ssl_disabled': False
            }
            # Add custom SSL cert if provided
            ssl_ca = os.getenv('MYSQL_SSL_CA')
            if ssl_ca:
                mysql_config['ssl']['ca'] = ssl_ca
        
        conn = pymysql.connect(**mysql_config)
        
        cursor = conn.cursor()
        cursor.execute(f"USE {mysql_config['database']}")
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ MySQL connection successful")
            return True
        else:
            print("❌ MySQL connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("Please check your MySQL server and credentials")
        return False

def show_database_info():
    """Show database configuration info"""
    
    print("📋 Database Configuration:")
    mysql_config = DatabaseConfig.get_mysql_config()
    
    print(f"   Host: {mysql_config['host']}")
    print(f"   Port: {mysql_config['port']}")
    print(f"   Database: {mysql_config['database']}")
    print(f"   Username: {mysql_config['user']}")
    print(f"   Password: {'*' * len(mysql_config['password']) if mysql_config['password'] else 'Not set'}")

def check_env_variables():
    """Check if all required environment variables are loaded"""
    
    # Try different common variable name patterns
    env_patterns = {
        'host': ['MYSQL_HOST', 'DB_HOST', 'DATABASE_HOST'],
        'username': ['MYSQL_USERNAME', 'MYSQL_USER', 'DB_USERNAME', 'DB_USER', 'DATABASE_USER'],
        'password': ['MYSQL_PASSWORD', 'DB_PASSWORD', 'DATABASE_PASSWORD'],
        'database': ['MYSQL_DATABASE', 'DB_NAME', 'DATABASE_NAME'],
        'port': ['MYSQL_PORT', 'DB_PORT', 'DATABASE_PORT'],
        'ssl_enabled': ['MYSQL_SSL_ENABLED', 'DB_SSL_ENABLED'],
        'ssl_ca': ['MYSQL_SSL_CA', 'DB_SSL_CA']
    }
    
    found_vars = {}
    missing_vars = []
    
    for var_type, possible_names in env_patterns.items():
        found = False
        for name in possible_names:
            if os.getenv(name):
                found_vars[var_type] = (name, os.getenv(name))
                found = True
                break
        
        if not found and var_type not in ['port', 'ssl_enabled', 'ssl_ca']:  # These are optional
            missing_vars.append(var_type)
    
    return found_vars, missing_vars

if __name__ == "__main__":
    print("🔧 MySQL Database Initialization")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found in current directory")
        print("Please create a .env file with your database credentials")
        print("\nExample .env file:")
        print("MYSQL_HOST=your_mysql_host")
        print("MYSQL_USERNAME=your_username")
        print("MYSQL_PASSWORD=your_password")
        print("MYSQL_DATABASE=your_database_name")
        print("MYSQL_PORT=3306")
        print("MYSQL_SSL_ENABLED=true")
        print("# MYSQL_SSL_CA=/path/to/ca-cert.pem  # Optional, only if your provider requires it")
        exit(1)
    else:
        print("✅ Found .env file")
    
    # Check environment variables with flexible naming
    found_vars, missing_vars = check_env_variables()
    
    if missing_vars:
        print(f"❌ Missing environment variables for: {', '.join(missing_vars)}")
        print("\nPlease add the following to your .env file:")
        
        suggestions = {
            'host': 'MYSQL_HOST=your_mysql_host',
            'username': 'MYSQL_USERNAME=your_username',
            'password': 'MYSQL_PASSWORD=your_password',
            'database': 'MYSQL_DATABASE=your_database_name'
        }
        
        for var_type in missing_vars:
            print(f"   {suggestions.get(var_type, f'{var_type.upper()}=your_value')}")
        exit(1)
    
    print("✅ All required environment variables found:")
    for var_type, (name, value) in found_vars.items():
        if var_type == 'password':
            print(f"   {name}: {'*' * len(value) if value else 'Not set'}")
        else:
            print(f"   {name}: {value}")
    print()
    
    # Show configuration
    try:
        show_database_info()
        print()
    except Exception as e:
        print(f"❌ Error getting database config: {e}")
        print("Please check your config.py file")
        exit(1)
    
    # Test connection
    if not test_mysql_connection():
        # If connection fails, try to initialize database
        print("🔧 Connection failed, attempting to initialize database...")
        if init_mysql_database():
            print("✅ Database initialization completed")
            if test_mysql_connection():
                print("✅ Connection now working")
            else:
                print("❌ Connection still failing")
                exit(1)
        else:
            print("❌ Database initialization failed")
            exit(1)
    else:
        print("✅ Database connection already working")
        
    print("\n🎉 MySQL database is ready!")
    print("\nYou can now:")
    print("1. Run the main application")
    print("2. Run migration script if you have SQLite data to transfer")
    print("3. Start using the application with MySQL backend")
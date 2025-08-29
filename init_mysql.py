#!/usr/bin/env python3
"""
Database initialization script for MySQL
"""
import os
import pymysql
from config import DatabaseConfig

def init_mysql_database():
    """Initialize MySQL database and tables"""
    
    print("🔧 Initializing MySQL database...")
    
    mysql_config = DatabaseConfig.get_mysql_config()
    
    try:
        # Connect to MySQL server (without selecting database)
        server_config = mysql_config.copy()
        database_name = server_config.pop('database')
        
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

if __name__ == "__main__":
    print("🔧 MySQL Database Initialization")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"   export {var}=your_value")
        exit(1)
    
    # Show configuration
    show_database_info()
    print()
    
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
#!/usr/bin/env python3
"""
Verification script for MongoDB migration
Run this script to verify that your MongoDB migration is working correctly
"""

import os
import sys
from dotenv import load_dotenv

def check_dependencies():
    """Check if required Python packages are installed"""
    print("🔍 Checking Python dependencies...")
    
    required_packages = {
        'pymongo': 'pip install pymongo==4.6.1',
        'pymysql': 'pip install PyMySQL==1.1.1', 
        'dotenv': 'pip install python-dotenv==1.1.1',
        'flask': 'pip install Flask==3.1.2'
    }
    
    missing_packages = []
    
    for package, install_cmd in required_packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - run: {install_cmd}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking .env file...")
    
    env_file = '.env'
    if not os.path.exists(env_file):
        print("   ❌ .env file not found")
        print("   📝 Copy .env.example to .env and update with your credentials")
        return False
    
    print("   ✅ .env file exists")
    
    # Load and check environment variables
    load_dotenv()
    
    required_vars = {
        'MONGODB_URI': 'MongoDB connection string',
        'MONGODB_DATABASE': 'MongoDB database name', 
        'MYSQL_HOST': 'MySQL host for user authentication',
        'MYSQL_USERNAME': 'MySQL username',
        'MYSQL_DATABASE': 'MySQL database name'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'MONGODB_URI' and '@' in value:
                # Mask credentials
                display_value = value.split('@')[0].split('//')[0] + '//***:***@' + value.split('@')[1]
                print(f"   ✅ {var}: {display_value}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set ({description})")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB connection...")
    
    try:
        from mongodb_chat import MongoDBChatHistory
        
        mongo_chat = MongoDBChatHistory()
        
        if mongo_chat.db_available:
            print("   ✅ MongoDB connection successful")
            print(f"   📊 Database: {mongo_chat.database_name}")
            
            # Test basic operation
            collections = mongo_chat.db.list_collection_names()
            print(f"   📋 Collections: {collections}")
            
            mongo_chat.close_connection()
            return True
        else:
            print("   ❌ MongoDB connection failed")
            print("   💡 Check your MONGODB_URI in .env file")
            return False
            
    except Exception as e:
        print(f"   ❌ MongoDB error: {e}")
        return False

def test_mysql_connection():
    """Test MySQL connection"""
    print("\n🔍 Testing MySQL connection...")
    
    try:
        from medibot2_auth import MedibotAuthDatabase
        
        auth_db = MedibotAuthDatabase()
        
        if auth_db.db_available:
            print("   ✅ MySQL connection successful")
            print("   📊 User authentication database ready")
            return True
        else:
            print("   ❌ MySQL connection failed")
            print("   💡 Check your MySQL credentials in .env file")
            return False
            
    except Exception as e:
        print(f"   ❌ MySQL error: {e}")
        return False

def test_application_import():
    """Test that the application can import all modules"""
    print("\n🔍 Testing application modules...")
    
    try:
        # Test main imports
        from mongodb_chat import MongoDBChatHistory
        from medibot2_auth import MedibotAuthDatabase
        
        print("   ✅ Core modules import successfully")
        
        # Test initialization
        mongo_chat = MongoDBChatHistory()
        auth_db = MedibotAuthDatabase()
        
        print("   ✅ Database modules initialize correctly")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def main():
    """Main verification function"""
    print("🔧 MongoDB Migration Verification")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file), 
        ("Application", test_application_import),
        ("MongoDB", test_mongodb_connection),
        ("MySQL", test_mysql_connection)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ {check_name} check failed: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Verification Summary:")
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! Your MongoDB migration is ready!")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Login and test chat functionality")
        print("3. Verify chat history is saved to MongoDB")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help, see MONGODB_MIGRATION.md")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
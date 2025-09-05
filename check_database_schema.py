"""
Check the existing database schema and fix column name mismatch
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USERNAME'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'charset': 'utf8mb4',
        'autocommit': True
    }

def check_table_schema():
    """Check the existing table schema"""
    try:
        db_config = get_db_config()
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("✅ Connected to MySQL database")
            
            cursor = connection.cursor()
            
            # Check if doctors table exists
            cursor.execute("SHOW TABLES LIKE 'doctors'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Doctors table exists")
                
                # Get table structure
                cursor.execute("DESCRIBE doctors")
                columns = cursor.fetchall()
                
                print("\n📋 Current table structure:")
                for column in columns:
                    print(f"  • {column[0]} - {column[1]} - {column[2]} - {column[3]}")
                
                # Check if we have 'specialty' or 'speciality'
                column_names = [col[0] for col in columns]
                
                if 'specialty' in column_names:
                    print("✅ Found 'specialty' column (without 'i')")
                    return 'specialty'
                elif 'speciality' in column_names:
                    print("✅ Found 'speciality' column (with 'i')")
                    return 'speciality'
                else:
                    print("❌ Neither 'specialty' nor 'speciality' column found")
                    return None
            else:
                print("❌ Doctors table does not exist")
                return None
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return None

def main():
    """Main function"""
    print("🔍 Checking Database Schema")
    print("=" * 40)
    
    column_name = check_table_schema()
    
    if column_name:
        print(f"\n✅ The database uses column name: '{column_name}'")
        print(f"💡 We need to update our code to use '{column_name}' instead of 'speciality'")
    else:
        print("\n❌ Could not determine the correct column name")

if __name__ == "__main__":
    main()

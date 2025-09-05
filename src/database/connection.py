# src/database/connection.py
"""
Database connection utilities for MySQL and fallback handling
"""
import os
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """MySQL database connection with fallback handling"""
    
    def __init__(self):
        self.connection = None
        self.db_config = {
            'host': os.getenv('MYSQL_HOST'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USERNAME'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            if not all([self.db_config['host'], self.db_config['user'], self.db_config['database']]):
                print("❌ Missing database credentials in environment variables")
                return False
            
            self.connection = mysql.connector.connect(**self.db_config)
            
            if self.connection.is_connected():
                print(f"✅ Connected to MySQL database: {self.db_config['database']}")
                return True
            
        except Error as e:
            print(f"❌ MySQL Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected database error: {e}")
        
        return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connection and self.connection.is_connected()
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """Execute a query and return results"""
        if not self.is_connected():
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"❌ Query execution error: {e}")
            return None
    
    def save_conversation(self, user_id: str, conversation: list):
        """Save conversation to database (placeholder for future implementation)"""
        # This can be implemented later for chat history
        pass
    
    def get_conversation_history(self, user_id: str) -> Optional[list]:
        """Get conversation history from database (placeholder for future implementation)"""
        # This can be implemented later for chat history
        return None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        result = {
            'connected': False,
            'database': self.db_config['database'],
            'host': self.db_config['host'],
            'error': None
        }
        
        try:
            if self.connect():
                result['connected'] = True
                
                # Test doctors table
                cursor = self.connection.cursor()
                cursor.execute("SHOW TABLES LIKE 'doctors'")
                table_exists = cursor.fetchone() is not None
                
                if table_exists:
                    cursor.execute("SELECT COUNT(*) FROM doctors")
                    doctor_count = cursor.fetchone()[0]
                    result['doctors_count'] = doctor_count
                else:
                    result['doctors_count'] = 0
                    result['error'] = "Doctors table not found"
                
                cursor.close()
                self.disconnect()
            
        except Exception as e:
            result['error'] = str(e)
        
        return result

# config.py
"""
Configuration settings for the MediBot application
"""
import os
from urllib.parse import quote_plus

class DatabaseConfig:
    """Database configuration settings"""
    
    @staticmethod
    def get_mysql_url():
        """Get MySQL database URL from environment variables"""
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = os.getenv('MYSQL_PORT', '3306')
        username = os.getenv('MYSQL_USERNAME', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        database = os.getenv('MYSQL_DATABASE', 'medibot')
        
        # URL encode password to handle special characters
        encoded_password = quote_plus(password) if password else ''
        
        if encoded_password:
            return f"mysql+pymysql://{username}:{encoded_password}@{host}:{port}/{database}?charset=utf8mb4"
        else:
            return f"mysql+pymysql://{username}@{host}:{port}/{database}?charset=utf8mb4"
    
    @staticmethod
    def get_mysql_config():
        """Get MySQL connection configuration as dictionary"""
        return {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USERNAME', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'medibot'),
            'charset': 'utf8mb4',
            'autocommit': False
        }

class Config:
    """Main application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # Database settings
    DATABASE_URL = DatabaseConfig.get_mysql_url()
    MYSQL_CONFIG = DatabaseConfig.get_mysql_config()
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Development settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
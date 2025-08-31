# medibot2 Database Setup Guide

This document provides step-by-step instructions for setting up the new **medibot2** MySQL database system.

## Overview

The new medibot2 database has been completely redesigned from scratch with a proper MySQL architecture that includes:

- **users** table: Stores user account details and authentication information
- **user_sessions** table: Manages user sessions and conversation tracking  
- **chat_history** table: Stores complete chat history including both user prompts and AI responses

## Prerequisites

1. **MySQL Server**: Ensure MySQL 5.7+ or MariaDB 10.2+ is installed and running
2. **Python Dependencies**: The required packages are already in requirements.txt

```bash
pip install -r requirements.txt
```

## Step 1: Environment Configuration

Copy the provided `.env` file and configure your MySQL settings:

```bash
# The .env file should already exist with these settings:
cp .env .env.backup  # Optional: backup if you want to modify
```

Edit `.env` file with your MySQL credentials:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production

# MySQL Database Configuration for medibot2
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medibot2

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 2: Initialize medibot2 Database

Run the database initialization script:

```bash
python init_medibot2.py
```

This script will:
- Create the **medibot2** database if it doesn't exist
- Create all necessary tables (users, user_sessions, chat_history)
- Set up proper indexes and foreign key relationships
- Test the database connection
- Display database statistics

Expected output:
```
🔧 medibot2 Database Initialization
==================================================
🔍 Checking environment variables:
   ✅ MYSQL_HOST: localhost
   ✅ MYSQL_USERNAME: root
   ✅ MYSQL_DATABASE: medibot2
📋 medibot2 Database Configuration:
   Host: localhost
   Port: 3306
   Database: medibot2
🔧 Initializing medibot2 MySQL database...
✅ Database 'medibot2' created/verified
✅ Users table created/verified
✅ User sessions table created/verified  
✅ Chat history table created/verified
🎉 Setup completed successfully!
```

## Step 3: Remove Old SQLite Files

**⚠️ IMPORTANT: The following SQLite files have been completely removed as requested:**

- `auth.py` (old SQLite authentication system)
- `sqlite_auth.py` (SQLite implementation)
- `users.db` (SQLite database file)  
- `fix_sqlite_chat_database.py`
- `test_database_fixes.py`
- Any other SQLite-related authentication files

## Step 4: Start the Application

Run the main application with the new medibot2 system:

```bash
python main.py
```

The application will now:
- Connect to MySQL medibot2 database instead of SQLite
- Use the new authentication system from `medibot2_auth.py`
- Store all user sessions and chat history in the new database structure

## Database Schema Details

### users table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### user_sessions table
```sql
CREATE TABLE user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(128) UNIQUE NOT NULL,
    conversation_id VARCHAR(36) NOT NULL,
    session_title VARCHAR(200) DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### chat_history table
```sql
CREATE TABLE chat_history (
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
    FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## Files Modified/Created

### New Files Created:
1. **`medibot2_auth.py`** - New MySQL authentication system for medibot2
2. **`init_medibot2.py`** - Database initialization script  
3. **`newdb.md`** - This documentation file
4. **`.env`** - Environment configuration file

### Files That Will Be Updated:
1. **`main.py`** - Updated to use new medibot2_auth system
2. **`config.py`** - Updated MySQL configuration for medibot2

### Files Removed:
- All SQLite-related authentication files as requested

## Key Features of New System

1. **Proper Session Management**: Each user session is tracked with unique conversation IDs
2. **Complete Chat History**: Both user prompts and AI responses are stored together
3. **Conversation Tracking**: Each conversation has a unique ID and title
4. **User Management**: Comprehensive user registration and authentication
5. **MySQL Performance**: Proper indexes and foreign keys for optimal performance
6. **Security**: Password hashing with salts, session token management

## Testing the Setup

To verify everything is working:

1. **Test database connection:**
   ```bash
   python init_medibot2.py
   ```

2. **Test authentication system:**
   ```bash
   python medibot2_auth.py
   ```

3. **Start the application:**
   ```bash
   python main.py
   ```

4. **Register a new user and test chat functionality**

## Troubleshooting

### Common Issues:

1. **MySQL Connection Error:**
   - Verify MySQL server is running
   - Check credentials in `.env` file
   - Ensure database user has proper permissions

2. **Permission Denied:**
   ```sql
   -- Create dedicated database user if needed
   CREATE USER 'medibot_user'@'%' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON medibot2.* TO 'medibot_user'@'%';
   FLUSH PRIVILEGES;
   ```

3. **Module Import Error:**
   - Ensure all required packages are installed: `pip install -r requirements.txt`
   - Check Python path and file locations

### Database Commands:

```sql
-- Connect to MySQL and check the database
USE medibot2;
SHOW TABLES;
DESCRIBE users;
DESCRIBE user_sessions;  
DESCRIBE chat_history;

-- Check data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM user_sessions;
SELECT COUNT(*) FROM chat_history;
```

## Production Deployment

For production use:

1. **Update environment variables** with production MySQL credentials
2. **Enable SSL/TLS** for database connections
3. **Set strong passwords** and restrict database user permissions
4. **Configure proper firewall rules**
5. **Set up database backups**

## Migration Notes

This is a **complete replacement** of the old SQLite system. The new medibot2 database:

- Uses proper relational database design
- Supports concurrent users and sessions  
- Provides better data integrity and performance
- Enables advanced features like conversation management
- Maintains complete chat history with proper relationships

The old SQLite files have been completely removed as requested, and all functionality has been migrated to the new MySQL-based system.
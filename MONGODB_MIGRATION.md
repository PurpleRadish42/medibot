# MongoDB Migration Guide for Medibot Chat History

This document explains how to migrate from MySQL-based chat history to MongoDB while keeping user authentication in MySQL.

## Overview

**What's Changed:**
- ✅ **User Authentication**: Still uses MySQL (no changes needed)
- 🔄 **Chat History**: Now uses MongoDB for better performance and scalability
- ✅ **User Sessions**: Still managed in MySQL
- ✅ **EHR Features**: Still use MySQL

**Benefits of MongoDB for Chat History:**
- Better performance for large conversation datasets
- Flexible document structure for complex message types
- Easier chat retrieval and search capabilities
- Better scalability for high-volume chat data

## Prerequisites

1. **MongoDB Instance**: You need access to a MongoDB instance (DigitalOcean or other)
2. **Python Dependencies**: pymongo package (already added to requirements.txt)
3. **Environment Variables**: MongoDB connection details in .env file

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the new `pymongo==4.6.1` dependency.

### Step 2: Configure Environment Variables

Create or update your `.env` file with MongoDB credentials:

```env
# Existing MySQL configuration (keep as-is for user authentication)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medibot

# NEW: MongoDB configuration for chat history
MONGODB_URI=mongodb://username:password@your-mongodb-host:27017/medibot_chats?authSource=admin
MONGODB_DATABASE=medibot_chats
```

**How to fill in MongoDB credentials:**

For DigitalOcean MongoDB:
1. Go to your DigitalOcean control panel
2. Navigate to your MongoDB cluster
3. Click "Connection Details" or "Connect"
4. Copy the connection string
5. Replace `username`, `password`, and `your-mongodb-host` with your actual values

Example:
```env
MONGODB_URI=mongodb://doadmin:AVNS_abc123def456@medibot-mongodb-cluster-do-user-123456-0.c.db.ondigitalocean.com:25060/medibot_chats?authSource=admin&tls=true
MONGODB_DATABASE=medibot_chats
```

### Step 3: Setup MongoDB Database

Run the MongoDB setup script to create the database and collections:

```bash
python setup_mongodb.py
```

This script will:
- ✅ Test your MongoDB connection
- ✅ Create the `medibot_chats` database
- ✅ Create required collections (`chat_messages`, `chat_sessions`)
- ✅ Create performance indexes
- ✅ Verify everything is working correctly

Expected output:
```
🔧 MongoDB Chat History Setup for Medibot
==================================================
🔍 Checking MongoDB environment variables:
   ✅ MONGODB_URI: mongodb://***:***@your-host:27017/medibot_chats?authSource=admin
   ✅ MONGODB_DATABASE: medibot_chats

🏗️  Setting up MongoDB database...
✅ Connected to MongoDB: medibot_chats
✅ Created chat_messages collection
✅ Created chat_sessions collection
✅ MongoDB indexes created
✅ MongoDB database setup completed successfully

🔗 Testing MongoDB connection...
✅ MongoDB connection successful
📋 Available collections: ['chat_messages', 'chat_sessions']
🧪 Testing sample operations...
✅ Test message saved successfully
✅ Test message retrieved successfully
✅ Test data cleaned up (1 messages deleted)

🎉 MongoDB setup completed successfully!
```

### Step 4: Verify Migration is Working

Run the verification script to check your setup:

```bash
python verify_mongodb_migration.py
```

This will check:
- ✅ Required Python dependencies
- ✅ .env file configuration
- ✅ MongoDB connection
- ✅ MySQL connection (for user auth)
- ✅ Application module imports

Expected output for successful setup:
```
🔧 MongoDB Migration Verification
==================================================
🔍 Checking Python dependencies...
   ✅ pymongo
   ✅ pymysql
   ✅ dotenv
   ✅ flask

🔍 Checking .env file...
   ✅ .env file exists
   ✅ MONGODB_URI: mongodb://***:***@your-host:27017/medibot_chats
   ✅ MONGODB_DATABASE: medibot_chats
   ✅ MYSQL_HOST: localhost
   ✅ MYSQL_USERNAME: root
   ✅ MYSQL_DATABASE: medibot

🔍 Testing application modules...
   ✅ Core modules import successfully
   ✅ Database modules initialize correctly

🔍 Testing MongoDB connection...
   ✅ MongoDB connection successful
   📊 Database: medibot_chats
   📋 Collections: ['chat_messages', 'chat_sessions']

🔍 Testing MySQL connection...
   ✅ MySQL connection successful
   📊 User authentication database ready

==================================================
📊 Verification Summary:
   ✅ PASS Dependencies
   ✅ PASS Environment
   ✅ PASS Application
   ✅ PASS MongoDB
   ✅ PASS MySQL

==================================================
🎉 All checks passed! Your MongoDB migration is ready!
```

Then start the application:

```bash
python main.py
```

You should see:
```
✅ MongoDB chat history initialized successfully
🚀 Starting medibot2 Application...
==================================================
✅ Features Available:
  📱 Authentication System: ✅ Ready (medibot2 MySQL)
  💬 Chat History: ✅ Ready (MongoDB)
  🤖 Medical AI: ✅ Ready
  🗄️  User Database: medibot2 (MySQL)
  🗄️  Chat Database: medibot_chats (MongoDB)
```

## Data Structure

### MongoDB Collections

#### 1. `chat_messages` Collection
```javascript
{
  "_id": ObjectId("..."),
  "user_id": 123,
  "conversation_id": "uuid-string",
  "message_type": "user" | "assistant",
  "message": "The actual message content",
  "response": "Response content (for assistant messages)",
  "timestamp": ISODate("2024-01-01T12:00:00Z"),
  "message_order": 1
}
```

#### 2. `chat_sessions` Collection
```javascript
{
  "_id": ObjectId("..."),
  "user_id": 123,
  "conversation_id": "uuid-string",
  "session_title": "Generated from first message",
  "created_at": ISODate("2024-01-01T12:00:00Z"),
  "updated_at": ISODate("2024-01-01T12:30:00Z"),
  "is_active": true,
  "message_count": 10
}
```

### Indexes Created
- `chat_messages`: `(user_id, timestamp)`, `(conversation_id, message_order)`
- `chat_sessions`: `(user_id, updated_at)`, `(conversation_id)`

## API Changes

All chat-related API endpoints now use MongoDB:

### Existing Endpoints (Updated)
- `GET /api/chat-history` - Now reads from MongoDB
- `DELETE /api/chat-history/clear-all` - Now clears MongoDB data
- `POST /api/chat` - Now saves to MongoDB

### New Endpoints
- `GET /api/conversations` - Get user's conversation list
- `GET /api/conversation/<id>/messages` - Get specific conversation messages  
- `DELETE /api/conversation/<id>` - Delete specific conversation

## Migration Process

### For Existing Users

**Important**: This migration does NOT automatically transfer existing MySQL chat history to MongoDB. Here's what happens:

1. **New chats**: All new conversations will be saved to MongoDB
2. **Old chats**: Existing MySQL chat history remains accessible until you're ready to migrate
3. **User accounts**: No impact - users can log in normally

### Optional: Manual Data Migration

If you want to migrate existing chat history from MySQL to MongoDB, you can create a custom migration script:

```python
# Example migration script (create as migrate_chat_data.py)
from medibot2_auth import MedibotAuthDatabase
from mongodb_chat import MongoDBChatHistory

def migrate_user_chats(user_id):
    mysql_db = MedibotAuthDatabase()
    mongo_db = MongoDBChatHistory()
    
    # Get old chat history
    old_history = mysql_db.get_chat_history(user_id, limit=1000)
    
    # Migrate each conversation
    for message, response, timestamp in old_history:
        mongo_db.save_chat_message(user_id, message, response)
    
    print(f"Migrated {len(old_history)} messages for user {user_id}")
```

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```
⚠️  MongoDB initialization failed: [Errno 111] Connection refused
```
**Solutions:**
- Check MongoDB server is running
- Verify connection string in `.env`
- Check firewall settings
- For DigitalOcean: Ensure your IP is whitelisted

#### 2. Authentication Failed
```
⚠️  MongoDB initialization failed: Authentication failed
```
**Solutions:**
- Verify username/password in connection string
- Check if `authSource=admin` is included
- Ensure database user has proper permissions

#### 3. Environment Variables Not Found
```
❌ MONGODB_URI: Not set
```
**Solutions:**
- Create `.env` file in project root
- Add required MongoDB variables
- Restart the application

### Fallback Behavior

If MongoDB is unavailable, the application will:
- ✅ Continue running (user authentication still works)
- ⚠️ Log warnings about chat history not being saved
- ⚠️ Return empty chat history
- ✅ Still allow new conversations (but they won't persist)

## Testing

### Manual Testing

1. **Start the application**:
   ```bash
   python main.py
   ```

2. **Login and start a chat**:
   - Go to http://localhost:5000
   - Login with existing account
   - Start a new conversation
   - Send several messages

3. **Verify data is saved**:
   ```bash
   python mongodb_chat.py  # Run the test script
   ```

4. **Check conversation history**:
   - Reload the chat page
   - Previous messages should appear in sidebar
   - Click on previous conversations to load them

### Database Verification

Connect to your MongoDB instance and verify data:

```javascript
// MongoDB shell commands
use medibot_chats

// Check collections exist
show collections

// Count documents
db.chat_messages.count()
db.chat_sessions.count()

// View sample data
db.chat_messages.findOne()
db.chat_sessions.findOne()
```

## Security Considerations

1. **Connection Security**: Always use TLS/SSL for MongoDB connections in production
2. **Authentication**: Use strong passwords and proper database user permissions
3. **Network Security**: Whitelist only necessary IP addresses
4. **Data Encryption**: Consider encryption at rest for sensitive medical data

## Backup and Recovery

### MongoDB Backup
```bash
# Backup entire database
mongodump --uri="your_mongodb_uri" --db=medibot_chats

# Restore from backup
mongorestore --uri="your_mongodb_uri" --db=medibot_chats dump/medibot_chats/
```

### Backup Strategy
- **Daily**: Automated database dumps
- **Weekly**: Full backup including indexes
- **Before Updates**: Manual backup before application updates

## Performance Monitoring

Monitor these metrics:
- MongoDB connection pool size
- Query response times
- Collection sizes
- Index usage

## Next Steps

After successful migration:

1. **Monitor Performance**: Check chat loading speeds and response times
2. **User Feedback**: Ensure users don't experience any issues
3. **Data Cleanup**: After confident in MongoDB stability, consider archiving old MySQL chat data
4. **Optimization**: Add more indexes if specific query patterns emerge

## Quick Verification

Use the included verification script to check your setup:

```bash
python verify_mongodb_migration.py
```

This script will:
- Check all required dependencies are installed
- Verify .env file configuration  
- Test MongoDB and MySQL connections
- Confirm application modules can be imported
- Provide specific guidance for any issues found

## Support

If you encounter issues:
1. **Run the verification script first**: `python verify_mongodb_migration.py`
2. Check the application logs for specific error messages
3. Verify MongoDB connection using `setup_mongodb.py`
4. Test with a fresh user account to isolate issues
5. Check MongoDB server logs for connection/authentication issues

---

**Migration Summary:**
- ✅ User authentication: MySQL (unchanged)
- ✅ Chat history: MongoDB (new)
- ✅ Backward compatibility: Maintained
- ✅ Performance: Improved for chat operations
- ✅ Scalability: Better for large chat datasets
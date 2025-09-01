# MediBot Chat History and EHR System - Running Instructions

## Overview

This document provides instructions on how to run the fixed MediBot application after the chat history and EHR system improvements have been implemented.

## What Was Fixed

### 1. Chat History Issues ✅
- **Problem**: Chat history was not loading correctly, users couldn't see previous conversations
- **Solution**: Fixed SQL JOIN query to properly pair user messages with assistant responses using `message_order`
- **Result**: Chat history now loads correctly in the sidebar and can be continued

### 2. EHR System Issues ✅
- **Problem**: EHR system wasn't detecting or storing user symptoms
- **Solution**: 
  - Enhanced keyword extraction with comprehensive medical terms (including plurals)
  - Fixed conversation_id generation for proper symptom tracking
  - Added database schema for `patient_symptoms` table
- **Result**: Symptoms are now automatically detected and stored for medical record tracking

### 3. Database Availability ✅
- **Problem**: Application would crash if MySQL database was unavailable
- **Solution**: Added graceful degradation - app starts even without database connection
- **Result**: Application is more robust and can handle temporary database outages

## Prerequisites

### Required Software
1. **Python 3.8+**
2. **MySQL Server** (recommended) or **MariaDB**
3. **Git** (for cloning the repository)

### Required Packages
All packages are listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Setup Instructions

### 1. Clone and Setup
```bash
git clone https://github.com/PurpleRadish42/medibot.git
cd medibot
pip install -r requirements.txt
```

### 2. Database Configuration

#### Option A: With MySQL (Recommended)
1. Install and start MySQL server
2. Create a database:
   ```sql
   CREATE DATABASE medibot;
   CREATE USER 'medibot_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON medibot.* TO 'medibot_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Copy and configure environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` file:
   ```bash
   # Database Configuration
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USERNAME=medibot_user
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=medibot
   
   # Application Configuration
   SECRET_KEY=your-secure-secret-key-here
   DEBUG=True
   
   # OpenAI Configuration (required for AI responses)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Email Configuration (optional)
   SMTP_SERVER=mail.smtp2go.com
   SMTP_PORT=587
   SMTP_USERNAME=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   FROM_EMAIL=noreply@yourdomain.com
   ```

#### Option B: Without MySQL (Limited Functionality)
The application will now start even without MySQL, but with limited functionality:
- No chat history persistence
- No EHR symptom storage
- Authentication features unavailable

Simply create a `.env` file with minimal configuration:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

### 1. Start the Application
```bash
python main.py
```

### 2. Expected Output
You should see output similar to:
```
Environment variables loaded from .env file
✅ Doctor database loaded: 2046 doctors
✅ MedicalRecommender initialized successfully
✅ Database initialized successfully  # (or warning if MySQL unavailable)
======================================================================
🚀 FLASK WEB SERVER STARTING
======================================================================
✅ Features Available:
  📱 Authentication System: ✅ Ready (medibot2 MySQL)
  🤖 Medical AI: ✅ Ready
  🏥 Doctor Database: ✅ Ready
  🗄️  Database: medibot2 (MySQL)

🌐 Access URLs:
  📱 Main app: http://localhost:5000
  🔐 Login: http://localhost:5000/login
  📝 Register: http://localhost:5000/register
  💬 Chat (after login): http://localhost:5000/chat
======================================================================
 * Running on http://127.0.0.1:5000
```

### 3. Access the Application
Open your browser and go to: **http://localhost:5000**

## Testing the Fixes

### 1. Automated Verification
Run the verification script to ensure everything is working:
```bash
python verify_fixes.py
```

Expected output:
```
🎉 ALL VERIFICATION TESTS PASSED!
The chat history and EHR fixes have been successfully implemented.
```

### 2. Manual Testing

#### Testing Chat History:
1. **Register/Login** at http://localhost:5000/register
2. **Start a conversation** by going to http://localhost:5000/chat
3. **Send multiple medical questions** like:
   - "I have a headache"
   - "It's been bothering me for 2 days"
   - "Should I see a doctor?"
4. **Refresh the page** - your conversation should appear in the sidebar
5. **Click on the conversation** in the sidebar - it should reload correctly
6. **Continue the conversation** - context should be maintained

#### Testing EHR System:
1. **Send messages with symptoms**:
   - "I have severe headaches and feel dizzy"
   - "My stomach hurts after eating"
   - "I feel weak and tired lately"
   - "I have chest pain when I exercise"

2. **Check the EHR modal** by clicking the medical records icon (📋)
3. **Verify symptoms appear** with:
   - Extracted keywords (headaches, stomach, weak, chest, pain, etc.)
   - Severity levels (mild, moderate, severe)
   - Timestamps
   - Original symptom descriptions

#### Testing Database Resilience:
1. **Stop MySQL** (if running): `sudo service mysql stop`
2. **Restart the application**: `python main.py`
3. **Verify** the app starts with warnings but doesn't crash
4. **Restart MySQL**: `sudo service mysql start`
5. **Restart the application** - full functionality should return

## Database Schema

The application automatically creates these tables:

### `chat_history`
```sql
- id: Primary key
- user_id: Links to user
- session_id: Links to session
- conversation_id: Groups related messages
- message_type: 'user' or 'assistant'
- message: The actual message content
- response: For assistant messages, contains the response
- timestamp: When the message was sent
- message_order: Ensures proper pairing (1, 2, 3, 4...)
```

### `patient_symptoms`
```sql
- id: Primary key
- user_id: Links to user
- conversation_id: Links to the conversation where symptoms were mentioned
- symptoms_text: Original user message
- keywords: Extracted medical keywords (comma-separated)
- severity: Detected severity level (mild/moderate/severe)
- category: Medical category (future use)
- created_at: Timestamp
```

## API Endpoints

The fixed application includes these key endpoints:

### Chat History
- `GET /api/chat-history` - Get user's chat history
- `DELETE /api/chat-history/clear-all` - Clear all user chats

### EHR System  
- `POST /api/ehr/symptoms` - Save new symptoms
- `GET /api/ehr/symptoms` - Get user's symptom history
- `POST /api/ehr/symptoms/similar` - Find similar historical symptoms

### Core Chat
- `POST /api/chat` - Send message and get AI response (includes EHR integration)

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
**Error**: `Can't connect to MySQL server`
**Solution**: 
- Ensure MySQL is running: `sudo service mysql start`
- Check credentials in `.env` file
- Verify database exists and user has permissions

#### 2. OpenAI API Errors
**Error**: `The api_key client option must be set`
**Solution**: 
- Add valid OpenAI API key to `.env` file
- Ensure the key has sufficient credits

#### 3. Missing Dependencies
**Error**: Module import errors
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 4. Chat History Not Loading
**Check**:
- Database connection is working
- User is logged in
- Browser console for JavaScript errors
- Server logs for backend errors

#### 5. Symptoms Not Being Detected
**Check**:
- Message contains medical keywords (headache, pain, sick, etc.)
- Check server logs for EHR integration messages:
  ```
  🏥 Detected potential symptoms in message: ...
  ✅ Symptoms saved with ID: 123
  ```

### Debug Mode
Enable detailed logging by setting in `.env`:
```
DEBUG=True
```

## Performance Notes

- **Chat History**: Optimized with database indexes on `user_id`, `conversation_id`, and `message_order`
- **Symptom Detection**: Runs in-memory and is efficient for typical message lengths
- **Database Impact**: Minimal - only one additional query per message when symptoms are detected
- **Memory Usage**: Conversation history is limited to last 20 exchanges per user to prevent memory issues

## Security Notes

- Never commit `.env` file to version control
- Use strong `SECRET_KEY` in production
- Ensure MySQL user has minimal required privileges
- Consider using environment variables instead of `.env` file in production

## Production Deployment

For production deployment:

1. **Use a production WSGI server** (like Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 main:app
   ```

2. **Set environment variables** instead of `.env` file
3. **Use HTTPS** with SSL certificates
4. **Configure MySQL** for production workloads
5. **Set up monitoring** for database and application health
6. **Enable proper logging** and error tracking

## Support

If you encounter issues:

1. **Check the logs** - both application and database logs
2. **Run the verification script** - `python verify_fixes.py`
3. **Check database connectivity** - `python medibot2_auth.py`
4. **Review this documentation** for common solutions

The fixes implemented ensure robust operation and clear error messages to help with troubleshooting.
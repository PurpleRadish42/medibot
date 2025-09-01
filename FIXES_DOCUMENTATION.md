# MediBot Chat History and EHR System Fixes

## Overview

This document details the fixes implemented to resolve issues with chat history not functioning properly and the EHR system not storing user symptoms correctly.

## Issues Fixed

### 1. Chat History Not Functioning Properly

**Problem**: The chat history was not loading correctly in the frontend, and users could not see their previous conversations.

**Root Cause**: The `get_chat_history` method in `medibot2_auth.py` was incorrectly structured. It was trying to retrieve both user messages and AI responses from single database rows, but the system stores them as separate rows with different `message_type` values.

**Solution**: 
- Rewrote the SQL query to properly JOIN user messages with their corresponding assistant responses
- Used `message_order` to correctly pair user messages with AI responses
- Added fallback handling for cases where responses might be missing

**Files Modified**: 
- `medibot2_auth.py` (lines 538-572)

### 2. EHR System Not Storing Symptoms

**Problem**: User symptoms were not being detected and saved to the EHR system, preventing the medical history from building up.

**Root Causes**:
1. **Conversation ID Issue**: The system was generating new conversation IDs instead of using the session's existing conversation_id
2. **Keyword Extraction Problems**: The symptom keyword extraction was too restrictive and had issues with partial matching
3. **Missing Error Handling**: Limited logging made it difficult to diagnose issues

**Solutions**:

#### A. Fixed Conversation ID Handling
- Modified the symptom saving logic to retrieve `conversation_id` from the user's active session
- Added fallback logic when conversation_id is missing
- Enhanced error logging throughout the process

#### B. Improved Keyword Extraction
- Enhanced the `extract_symptom_keywords` method with a more comprehensive medical keyword list
- Fixed partial matching issues that were causing false positives
- Added support for common symptom phrases like "feel sick", "under the weather"

#### C. Enhanced Error Handling
- Added detailed logging at each step of the symptom detection process
- Improved error messages for debugging
- Added verification that symptoms are actually saved to the database

**Files Modified**:
- `main.py` (lines 338-378) - Symptom detection and saving logic
- `medibot2_auth.py` (lines 680-714) - Keyword extraction method

## Technical Details

### Chat History Fix

**Before**:
```sql
SELECT message, response, timestamp
FROM chat_history
WHERE user_id = %s AND message_type = 'user'
ORDER BY timestamp DESC
LIMIT %s
```

**After**:
```sql
SELECT 
    u.message as user_message,
    a.message as assistant_response,
    u.timestamp,
    u.conversation_id
FROM chat_history u
LEFT JOIN chat_history a ON (
    u.conversation_id = a.conversation_id 
    AND u.message_order + 1 = a.message_order 
    AND a.message_type = 'assistant'
)
WHERE u.user_id = %s AND u.message_type = 'user'
ORDER BY u.timestamp DESC
LIMIT %s
```

### EHR Symptom Detection Fix

**Enhanced Keyword List**: Added medical terms including:
- Body parts: `chest`, `stomach`, `back`, `neck`, `throat`
- Symptoms: `headache`, `fever`, `cough`, `pain`, `ache`, `dizzy`, `weak`
- Descriptors: `sick`, `ill`, `hurt`, `uncomfortable`, `tender`
- Phrases: `feel sick`, `feel bad`, `not well`, `under weather`

**Improved Detection Logic**:
```python
# Get conversation_id from the user's session data
conversation_id = request.user.get('conversation_id')
if not conversation_id:
    # Fallback: create a conversation ID if none exists
    conversation_id = f"user-{user_id}-{int(time.time())}"
```

## Testing

### Automated Tests Created

1. **Logic Tests** (`/tmp/test_logic_only.py`):
   - Tests symptom detection with various message types
   - Verifies keyword extraction accuracy
   - Tests chat history pairing logic

2. **Database Tests** (`/tmp/test_sqlite_adapter.py`):
   - Tests SQL queries with SQLite adapter
   - Verifies chat history retrieval
   - Tests EHR symptom storage and retrieval

### Test Results
```
✅ All SQLite database tests PASSED
✅ The SQL queries and logic appear to be working correctly
✅ Chat history pairing logic works as expected
✅ EHR symptom storage and retrieval works correctly
```

## How to Verify the Fixes

### 1. Chat History Functionality

1. **Start the application**: `python main.py`
2. **Login** as a user
3. **Send several chat messages** with medical content
4. **Refresh the page** or check the chat history section
5. **Verify**: Previous conversations should now appear in the sidebar
6. **Click on old conversations**: Should load the complete message history

### 2. EHR System Functionality

1. **Send messages with symptoms** like:
   - "I have a headache"
   - "My stomach hurts"
   - "I feel sick and tired"
   - "I'm experiencing chest pain"

2. **Check the EHR modal** (click the medical records icon)
3. **Verify**: Symptoms should appear in the health records with:
   - Extracted keywords
   - Severity levels
   - Timestamps
   - Symptom descriptions

### 3. Backend Logging

Monitor the console output for:
```
🏥 Detected potential symptoms in message: I have a headache...
✅ Symptoms saved with ID: 123
💾 Chat saved to database
```

## Database Schema

The fixes work with the existing schema:

### chat_history table
```sql
- user_id: Links to user
- session_id: Links to session  
- conversation_id: Groups related messages
- message_type: 'user' or 'assistant'
- message: The actual message content
- response: For assistant messages, contains the response
- message_order: Ensures proper pairing
```

### patient_symptoms table
```sql
- user_id: Links to user
- conversation_id: Links to the conversation where symptoms were mentioned
- symptoms_text: Original user message
- keywords: Extracted medical keywords
- severity: Detected severity level
- created_at: Timestamp
```

## Performance Considerations

- **Chat History**: The JOIN query is optimized with proper indexes on `conversation_id`, `message_order`, and `user_id`
- **Symptom Detection**: Keyword extraction runs in-memory and is efficient for typical message lengths
- **Database Calls**: Minimal impact - only one additional query per message when symptoms are detected

## Future Enhancements

1. **Advanced NLP**: Replace simple keyword matching with more sophisticated medical NLP
2. **Symptom Categorization**: Automatically categorize symptoms by medical specialty
3. **Severity Detection**: Improve severity detection using context and modifiers
4. **Similar Symptoms**: The `find_similar_symptoms` method is already implemented for historical matching

## Troubleshooting

### Chat History Not Loading
1. Check database connection
2. Verify user has active session
3. Check console for database errors
4. Ensure `conversation_id` is being set correctly

### Symptoms Not Being Saved
1. Check that messages contain medical keywords
2. Verify symptom detection logging in console
3. Ensure database has `patient_symptoms` table
4. Check user permissions for database writes

### Database Connection Issues
1. Verify MySQL server is running
2. Check environment variables in `.env` file
3. Ensure database user has proper permissions
4. Test connection with: `python medibot2_auth.py`

# ============================================
# ADD THESE METHODS TO AuthDatabase CLASS IN auth.py
# ============================================

def save_chat_message_with_conversation(self, user_id, message, response, conversation_id=None):
    """Save chat message to history with conversation support"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # If no conversation_id provided, create a new one
        if not conversation_id:
            import uuid
            conversation_id = f"conv_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Generate title from message
            title = message[:50] + "..." if len(message) > 50 else message
        else:
            # Get existing title
            cursor.execute("SELECT title FROM chat_history WHERE conversation_id = ? LIMIT 1", (conversation_id,))
            result = cursor.fetchone()
            title = result[0] if result else message[:50]
        
        # Save user message
        cursor.execute("""
            INSERT INTO chat_history (user_id, conversation_id, message_type, title, message, response, timestamp)
            VALUES (?, ?, 'user', ?, ?, '', datetime('now'))
        """, (user_id, conversation_id, title, message))
        
        # Save bot response
        cursor.execute("""
            INSERT INTO chat_history (user_id, conversation_id, message_type, title, message, response, timestamp)
            VALUES (?, ?, 'bot', ?, '', ?, datetime('now'))
        """, (user_id, conversation_id, title, response))
        
        conn.commit()
        conn.close()
        print(f"Chat message saved with conversation {conversation_id} for user ID {user_id}")
        return conversation_id
        
    except Exception as e:
        print(f"Chat save error: {e}")
        return None

def get_user_conversations(self, user_id):
    """Get all conversations for a user"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, title, 
                   MIN(timestamp) as first_message,
                   MAX(timestamp) as last_message,
                   COUNT(*) as message_count
            FROM chat_history
            WHERE user_id = ? AND conversation_id IS NOT NULL AND conversation_id != ''
            GROUP BY conversation_id, title
            ORDER BY last_message DESC
        """, (user_id,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        formatted_conversations = []
        for conv_id, title, first_msg, last_msg, msg_count in conversations:
            formatted_conversations.append({
                'id': conv_id,
                'title': title,
                'first_message': first_msg,
                'last_message': last_msg,
                'message_count': msg_count
            })
        
        print(f"Retrieved {len(formatted_conversations)} conversations for user {user_id}")
        return formatted_conversations
        
    except Exception as e:
        print(f"Get conversations error: {e}")
        return []

def get_conversation_messages(self, conversation_id, user_id):
    """Get all messages in a specific conversation"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message, response, timestamp, message_type
            FROM chat_history
            WHERE conversation_id = ? AND user_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id, user_id))
        
        messages = cursor.fetchall()
        conn.close()
        
        formatted_messages = []
        for message, response, timestamp, msg_type in messages:
            if message and message.strip():
                formatted_messages.append({
                    'content': message,
                    'isUser': True,
                    'timestamp': timestamp
                })
            if response and response.strip():
                formatted_messages.append({
                    'content': response,
                    'isUser': False,
                    'timestamp': timestamp
                })
        
        print(f"Retrieved {len(formatted_messages)} messages for conversation {conversation_id}")
        return formatted_messages
        
    except Exception as e:
        print(f"Get conversation messages error: {e}")
        return []

def delete_conversation(self, conversation_id, user_id):
    """Delete a specific conversation"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE conversation_id = ? AND user_id = ?", 
                      (conversation_id, user_id))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Deleted conversation {conversation_id}: {deleted_count} messages")
        return deleted_count > 0
        
    except Exception as e:
        print(f"Delete conversation error: {e}")
        return False

def clear_all_user_chats(self, user_id):
    """Clear all chat history for a user"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Cleared all chats for user {user_id}: {deleted_count} messages deleted")
        return deleted_count
        
    except Exception as e:
        print(f"Clear chats error: {e}")
        return 0

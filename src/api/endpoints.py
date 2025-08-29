

# src/api/endpoints.py
"""
API endpoints for the medical chatbot
"""
from typing import List, Tuple, Dict
from llm.recommender import MedicalRecommender

# Initialize recommender
recommender = MedicalRecommender()

def process_message(message: str, history: List[Tuple[str, str]]) -> str:
    """
    Process a message and return the chatbot response
    
    Args:
        message: User's message
        history: Conversation history
        
    Returns:
        Chatbot's response
    """
    return recommender.generate_response(history, message)

def reset_conversation():
    """Reset the conversation state"""
    global recommender
    recommender = MedicalRecommender()

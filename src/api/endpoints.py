

# src/api/endpoints.py
"""
API endpoints for the medical chatbot
"""
from typing import List, Tuple, Dict
from llm.recommender import MedicalRecommender

# Initialize recommender
recommender = MedicalRecommender()

def process_message(message: str, history: List[Tuple[str, str]], user_city: str = "Bangalore", sort_preference: str = "rating", user_location: dict = None) -> str:
    """
    Process a message and return the chatbot response
    
    Args:
        message: User's message
        history: Conversation history
        user_city: User's city for doctor recommendations
        sort_preference: Sorting preference for doctors (rating, experience, location)
        user_location: User's location dict with latitude/longitude
        
    Returns:
        Chatbot's response
    """
    return recommender.generate_response(
        history=history, 
        message=message, 
        user_city=user_city, 
        sort_preference=sort_preference, 
        user_location=user_location
    )

def reset_conversation():
    """Reset the conversation state"""
    global recommender
    recommender = MedicalRecommender()

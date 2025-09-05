#!/usr/bin/env python3
"""
Debug the exact conversation scenario from the user
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "llm"))

from recommender import MedicalRecommender

def test_conversation_debug():
    print("🐛 Debugging User's Exact Conversation Scenario")
    print("=" * 60)
    
    # Initialize the recommender
    recommender = MedicalRecommender()
    
    # Simulate the exact conversation from the user
    history = [
        ("my leg hurts a lot", "I'm sorry to hear that you're experiencing leg pain. To assist you better, could you please share how long you've been experiencing this pain and if there was any specific incident that caused it? Additionally, can you describe the severity of the pain on a scale of 1 to 10 and whether you have any swelling, bruising, or difficulty moving your leg?"),
        ("8", "Thank you for letting me know that the pain is quite severe at an 8. Given this level of pain, it's important to address it properly. Since I recommend seeing an Orthopedist, here are some tips to prepare for your visit: 1. **Pain Diary**: Keep track of when the pain occurs, its intensity, and any activities that worsen or alleviate it. 2. **Medical History**: Be prepared to discuss any previous injuries, surgeries, or conditions that may be relevant. 3. **Describe the Pain**: Note whether the pain is sharp, aching, or throbbing, and if it's localized to one area or more widespread. 4. **Imaging or Tests**: If you have had any X-rays or other imaging done, bring those results with you. 5. **Questions**: Write down any questions you might have for the Orthopedist regarding your injury and treatment options. If you have any more questions or if there's anything else I can assist you with, feel free to ask!"),
        ("can you tell me which doctor to see?", "Based on the severity of your leg pain and the fact that you mentioned it may be related to an injury, I recommend that you see an Orthopedist. They will be able to evaluate your condition and provide the necessary treatment. If you have any further questions or need assistance on how to prepare for your appointment, feel free to ask!"),
        ("can you show me the list of doctors", "I'm sorry, but I can only assist in determining which medical specialist you should see based on your symptoms. Since I've recommended that you see an Orthopedist for your leg pain, it would be best to look for local Orthopedic specialists in your area. If you have any other questions or need more guidance regarding your visit, feel free to ask!"),
    ]
    
    print("📊 Testing conversation state analysis...")
    state = recommender.analyze_conversation_state(history)
    print(f"Conversation state: {state}")
    print()
    
    print("🔍 Testing specialist extraction from each response...")
    for i, (user_msg, assistant_msg) in enumerate(history, 1):
        print(f"\nMessage {i}:")
        print(f"Assistant: {assistant_msg[:100]}...")
        specialist = recommender.extract_specialist_recommendation(assistant_msg)
        print(f"Extracted specialist: {specialist}")
    
    print("\n" + "="*60)
    print("🎯 Testing the latest user message...")
    
    # Test the latest message that should trigger doctor recommendations
    latest_message = "list of orthopedists"
    print(f"User message: {latest_message}")
    
    # Test what response would be generated
    try:
        response = recommender.generate_response(
            history=history,
            message=latest_message,
            user_city="Bangalore",
            sort_preference="rating"
        )
        
        print("\n📝 Generated response:")
        print(response)
        print("\n" + "="*60)
        
        # Check if the response contains doctor recommendations
        if "Dr." in response or "Doctor" in response or "<table" in response:
            print("✅ Response contains doctor recommendations!")
        else:
            print("❌ Response does NOT contain doctor recommendations!")
            
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversation_debug()

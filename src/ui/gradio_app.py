# src/ui/gradio_app.py
"""
Gradio UI for the medical chatbot
"""
import gradio as gr
from typing import List, Tuple
from api.endpoints import process_message, reset_conversation
from models.doctor import SPECIALISTS

def respond(message: str, history: List[Tuple[str, str]]) -> str:
    """Gradio response function"""
    return process_message(message, history)

def create_interface() -> gr.ChatInterface:
    """Create and configure the Gradio interface"""
    
    # Create examples from specialist conditions
    examples = [
        "I've been having chest pain for the past week",
        "I have frequent headaches and dizziness",
        "My knee hurts when I walk",
        "I've been experiencing stomach pain and nausea",
        "I'm feeling very anxious and can't sleep",
        "I have a persistent cough and breathing difficulties"
    ]
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    .message-wrap {
        border-radius: 10px;
        margin: 5px;
    }
    """
    
    # Create the interface
    demo = gr.ChatInterface(
        fn=respond,
        title="🏥 Medical Specialist Recommendation Assistant",
        description="""
        Welcome! I'm here to help you determine which medical specialist you should visit based on your symptoms. 
        
        Please describe what you're experiencing, and I'll ask you a few questions to better understand your condition.
        
        **Note:** This is a triage tool only. Always consult with a healthcare professional for proper diagnosis and treatment.
        """,
        examples=examples,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
        ),
        css=custom_css
    )
    
    return demo

def launch_app():
    """Launch the Gradio application"""
    # Reset conversation on startup
    reset_conversation()
    
    # Create and launch interface
    demo = create_interface()
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        favicon_path=None,
    )
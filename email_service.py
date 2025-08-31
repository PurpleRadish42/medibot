"""
Email Service for MediBot
Handles sending doctor recommendations via email using SMTP2GO
"""
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
import re
from datetime import datetime


class EmailService:
    """Email service using SMTP2GO for sending doctor recommendations"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'mail.smtp2go.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@medibot.ai')
        
    def send_doctor_recommendations(self, to_email: str, doctor_table_html: str, user_query: str = "") -> bool:
        """
        Send doctor recommendations via email
        
        Args:
            to_email: Recipient email address
            doctor_table_html: HTML content of the doctor recommendations table
            user_query: Original user query/symptoms (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Validate email address
            if not self._is_valid_email(to_email):
                print(f"❌ Invalid email address: {to_email}")
                return False
                
            # Create email content
            subject = "🏥 Your Doctor Recommendations from MediBot AI"
            html_content = self._create_email_template(doctor_table_html, user_query)
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Create HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            return self._send_email(message, to_email)
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def _create_email_template(self, doctor_table_html: str, user_query: str = "") -> str:
        """Create fancy HTML email template"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Extract just the table and important notes from the HTML
        table_content = doctor_table_html
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Doctor Recommendations - MediBot AI</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }}
                .header {{
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px;
                    line-height: 1.6;
                }}
                .query-box {{
                    background: #f8f9fa;
                    border-left: 4px solid #4facfe;
                    padding: 15px 20px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .query-box h3 {{
                    margin-top: 0;
                    color: #495057;
                    font-size: 16px;
                }}
                .recommendations {{
                    margin: 30px 0;
                }}
                .recommendations h2 {{
                    color: #495057;
                    border-bottom: 3px solid #4facfe;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 25px 30px;
                    text-align: center;
                    border-top: 1px solid #dee2e6;
                    color: #6c757d;
                }}
                .footer p {{
                    margin: 5px 0;
                    font-size: 14px;
                }}
                .disclaimer {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                /* Override table styles for email */
                table {{
                    width: 100% !important;
                    border-collapse: collapse !important;
                    margin: 20px 0 !important;
                    font-size: 14px !important;
                    background: white !important;
                    border-radius: 8px !important;
                    overflow: hidden !important;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
                }}
                th {{
                    background: linear-gradient(45deg, #4facfe, #00f2fe) !important;
                    color: white !important;
                    padding: 12px 8px !important;
                    text-align: left !important;
                    font-weight: bold !important;
                    font-size: 13px !important;
                    border: 1px solid #dee2e6 !important;
                }}
                td {{
                    padding: 10px 8px !important;
                    border: 1px solid #dee2e6 !important;
                    font-size: 13px !important;
                    vertical-align: top !important;
                }}
                tr:nth-child(even) {{
                    background-color: #f8f9fa !important;
                }}
                tr:nth-child(odd) {{
                    background-color: #ffffff !important;
                }}
                a {{
                    color: #4facfe !important;
                    text-decoration: none !important;
                    font-weight: bold !important;
                }}
                a:hover {{
                    text-decoration: underline !important;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MediBot AI</h1>
                    <p>Your Personalized Doctor Recommendations</p>
                </div>
                
                <div class="content">
                    <p>Dear Patient,</p>
                    <p>Thank you for using MediBot AI. Based on your consultation, we have prepared personalized doctor recommendations for you.</p>
                    
                    {f'<div class="query-box"><h3>📝 Your Query:</h3><p>{user_query}</p></div>' if user_query else ''}
                    
                    <div class="recommendations">
                        <h2>👨‍⚕️ Recommended Doctors</h2>
                        {table_content}
                    </div>
                    
                    <div class="disclaimer">
                        <strong>⚠️ Important Disclaimer:</strong><br>
                        This information is for educational purposes only and should not replace professional medical advice. 
                        Please consult with a qualified healthcare provider for proper diagnosis and treatment.
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>MediBot AI</strong> - Your AI Medical Assistant</p>
                    <p>Generated on {current_date}</p>
                    <p>This email was sent because you requested doctor recommendations through our platform.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _send_email(self, message: MIMEMultipart, to_email: str) -> bool:
        """Send email via SMTP2GO"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
                
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP Error: {e}")
            return False
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
            print("✅ SMTP connection test successful")
            return True
        except Exception as e:
            print(f"❌ SMTP connection test failed: {e}")
            return False
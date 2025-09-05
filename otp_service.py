#!/usr/bin/env python3
"""
OTP (One-Time Password) service for user authentication
Handles OTP generation, validation, and email sending
"""

import random
import string
import hashlib
import time
from datetime import datetime, timedelta
from email_service import EmailService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OTPService:
    def __init__(self):
        """Initialize OTP service with email service"""
        self.email_service = EmailService()
        self.otp_expiry_minutes = 10  # OTP expires in 10 minutes
        self.otp_length = 6  # 6-digit OTP
        
        # In-memory storage for OTPs (in production, use Redis or database)
        self.otp_storage = {}
    
    def generate_otp(self) -> str:
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    def hash_otp(self, otp: str) -> str:
        """Hash OTP for secure storage"""
        return hashlib.sha256(otp.encode()).hexdigest()
    
    def store_otp(self, email: str, otp: str, purpose: str = "registration") -> bool:
        """Store OTP with expiry time"""
        try:
            hashed_otp = self.hash_otp(otp)
            expiry_time = datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
            
            self.otp_storage[email] = {
                'otp_hash': hashed_otp,
                'expiry': expiry_time,
                'purpose': purpose,
                'attempts': 0,
                'created_at': datetime.now()
            }
            
            print(f"📧 OTP stored for {email} (purpose: {purpose})")
            print(f"📧 OTP value: {otp}")
            print(f"📧 Current storage keys: {list(self.otp_storage.keys())}")
            return True
        except Exception as e:
            print(f"❌ Error storing OTP: {e}")
            return False
    
    def verify_otp(self, email: str, otp: str) -> dict:
        """Verify OTP and return result"""
        try:
            print(f"🔍 Verifying OTP for email: {email}")
            print(f"🔍 Current OTP storage keys: {list(self.otp_storage.keys())}")
            print(f"🔍 OTP provided: {otp}")
            
            if email not in self.otp_storage:
                print(f"❌ No OTP found for email: {email}")
                return {
                    'success': False,
                    'message': 'No OTP found for this email. Please request a new verification code.',
                    'remaining_attempts': 0
                }
            
            stored_data = self.otp_storage[email]
            
            # Check if OTP has expired
            if datetime.now() > stored_data['expiry']:
                del self.otp_storage[email]
                return {
                    'success': False,
                    'message': 'OTP has expired. Please request a new one.',
                    'remaining_attempts': 0
                }
            
            # Check attempt limit (max 3 attempts)
            if stored_data['attempts'] >= 3:
                del self.otp_storage[email]
                return {
                    'success': False,
                    'message': 'Too many failed attempts. Please request a new OTP.',
                    'remaining_attempts': 0
                }
            
            # Verify OTP
            hashed_input = self.hash_otp(otp)
            if hashed_input == stored_data['otp_hash']:
                # OTP is correct, remove it from storage
                del self.otp_storage[email]
                return {
                    'success': True,
                    'message': 'OTP verified successfully',
                    'purpose': stored_data['purpose']
                }
            else:
                # Wrong OTP, increment attempts
                stored_data['attempts'] += 1
                remaining_attempts = 3 - stored_data['attempts']
                
                return {
                    'success': False,
                    'message': f'Invalid OTP. {remaining_attempts} attempts remaining.',
                    'remaining_attempts': remaining_attempts
                }
                
        except Exception as e:
            print(f"❌ Error verifying OTP: {e}")
            return {
                'success': False,
                'message': 'Error verifying OTP. Please try again.',
                'remaining_attempts': 0
            }
    
    def send_otp_email(self, email: str, otp: str, purpose: str = "registration") -> bool:
        """Send OTP via email"""
        try:
            print(f"📧 send_otp_email called with email: {email}, purpose: {purpose}")
            
            if purpose == "registration":
                subject = "🔐 Verify Your Email - MediGuide Registration"
                html_content = self._create_registration_otp_template(otp)
            elif purpose == "password_reset":
                subject = "🔐 Reset Your Password - MediGuide"
                html_content = self._create_password_reset_otp_template(otp)
            else:
                subject = "🔐 Your Verification Code - MediGuide"
                html_content = self._create_generic_otp_template(otp)
            
            print(f"📧 Subject: {subject}")
            print(f"📧 Calling email_service.send_email...")
            success = self.email_service.send_email(email, subject, html_content)
            print(f"📧 Email service returned: {success}")
            
            if success:
                print(f"✅ OTP email sent to {email}")
            else:
                print(f"❌ Failed to send OTP email to {email}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending OTP email: {e}")
            return False
    
    def _create_registration_otp_template(self, otp: str) -> str:
        """Create HTML template for registration OTP email"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification - MediGuide</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
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
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .otp-code {{
                    background: #f8f9fa;
                    border: 2px solid #4facfe;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 30px 0;
                    font-size: 32px;
                    font-weight: bold;
                    color: #4facfe;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .instructions {{
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MediGuide</h1>
                    <p>Email Verification</p>
                </div>
                
                <div class="content">
                    <h2>Welcome to MediGuide!</h2>
                    <p class="instructions">
                        Thank you for registering with MediGuide. To complete your registration, 
                        please verify your email address using the code below:
                    </p>
                    
                    <div class="otp-code">{otp}</div>
                    
                    <p class="instructions">
                        Enter this code in the verification form to activate your account.
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This code will expire in 10 minutes. 
                        If you didn't request this verification, please ignore this email.
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from MediGuide. Please do not reply to this email.</p>
                    <p>© 2025 MediGuide. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_password_reset_otp_template(self, otp: str) -> str:
        """Create HTML template for password reset OTP email"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - MediGuide</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
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
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .otp-code {{
                    background: #f8f9fa;
                    border: 2px solid #4facfe;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 30px 0;
                    font-size: 32px;
                    font-weight: bold;
                    color: #4facfe;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .instructions {{
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MediGuide</h1>
                    <p>Password Reset</p>
                </div>
                
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p class="instructions">
                        You requested to reset your password for MediGuide. 
                        Use the code below to verify your identity and reset your password:
                    </p>
                    
                    <div class="otp-code">{otp}</div>
                    
                    <p class="instructions">
                        Enter this code in the password reset form to continue.
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This code will expire in 10 minutes. 
                        If you didn't request this password reset, please ignore this email and 
                        consider changing your password for security.
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from MediGuide. Please do not reply to this email.</p>
                    <p>© 2025 MediGuide. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_generic_otp_template(self, otp: str) -> str:
        """Create generic HTML template for OTP email"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verification Code - MediGuide</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
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
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .otp-code {{
                    background: #f8f9fa;
                    border: 2px solid #4facfe;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 30px 0;
                    font-size: 32px;
                    font-weight: bold;
                    color: #4facfe;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .instructions {{
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MediGuide</h1>
                    <p>Verification Code</p>
                </div>
                
                <div class="content">
                    <h2>Your Verification Code</h2>
                    <p class="instructions">
                        Use the code below to verify your identity:
                    </p>
                    
                    <div class="otp-code">{otp}</div>
                    
                    <p class="instructions">
                        Enter this code in the verification form to continue.
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This code will expire in 10 minutes. 
                        If you didn't request this verification, please ignore this email.
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from MediGuide. Please do not reply to this email.</p>
                    <p>© 2025 MediGuide. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def cleanup_expired_otps(self):
        """Clean up expired OTPs from storage"""
        try:
            current_time = datetime.now()
            expired_emails = [
                email for email, data in self.otp_storage.items()
                if current_time > data['expiry']
            ]
            
            for email in expired_emails:
                del self.otp_storage[email]
            
            if expired_emails:
                print(f"🧹 Cleaned up {len(expired_emails)} expired OTPs")
                
        except Exception as e:
            print(f"❌ Error cleaning up expired OTPs: {e}")
    
    def get_otp_info(self, email: str) -> dict:
        """Get OTP information for debugging"""
        if email in self.otp_storage:
            data = self.otp_storage[email]
            return {
                'exists': True,
                'expiry': data['expiry'].isoformat(),
                'purpose': data['purpose'],
                'attempts': data['attempts'],
                'created_at': data['created_at'].isoformat()
            }
        else:
            return {'exists': False}

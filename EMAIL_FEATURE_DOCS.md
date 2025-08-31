# MediBot Email Feature Documentation

## Overview
A new email feature has been added to MediBot that allows users to send doctor recommendations directly to their email inbox after receiving recommendations from the AI chatbot.

## Features

### 🎯 What's New
- **Email Button**: A "Send via Email" button appears automatically after doctor recommendations are displayed
- **Email Modal**: A beautiful popup modal for entering email addresses
- **Fancy Email Template**: Professional HTML email template with the complete doctor recommendations table
- **SMTP2GO Integration**: Reliable email delivery using SMTP2GO service
- **Email Validation**: Client-side and server-side email validation
- **Responsive Design**: Works perfectly on desktop and mobile devices

### 📧 Email Content
The email includes:
- Complete doctor recommendations table with all links (Profile and Maps)
- User's original query/symptoms for context
- Professional MediBot AI branding
- Important medical disclaimers
- Responsive HTML design that works in all email clients

## Setup Instructions

### 1. Environment Configuration
Add the following variables to your `.env` file:

```env
# SMTP2GO Email Configuration
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp2go_username
SMTP_PASSWORD=your_smtp2go_password
FROM_EMAIL=noreply@yourdomain.com
```

### 2. SMTP2GO Setup
1. Sign up for an account at [SMTP2GO](https://www.smtp2go.com/)
2. Create SMTP credentials in your SMTP2GO dashboard
3. Add the username and password to your `.env` file
4. Configure your sending domain (optional but recommended)

### 3. Domain Configuration (Optional)
For better email deliverability:
- Add SPF record: `v=spf1 include:smtp2go.com ~all`
- Add DKIM records provided by SMTP2GO
- Set up a custom FROM_EMAIL address from your domain

## Technical Implementation

### Files Added/Modified

#### New Files:
- `email_service.py` - Email service module with SMTP2GO integration

#### Modified Files:
- `main.py` - Added `/api/send-email` API endpoint
- `templates/chat.html` - Added email button, modal, and JavaScript functions
- `.env.example` - Added SMTP configuration variables

### API Endpoint
```
POST /api/send-email
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "doctor_html": "<html>...</html>",
  "user_query": "I have chest pain"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Doctor recommendations sent successfully to user@example.com"
}
```

### Frontend Integration
The email button is automatically added to bot messages that contain doctor recommendations. The detection logic looks for:
- Presence of `<table>` element (doctor recommendations table)
- Presence of "Important Notes:" text (the disclaimer section)

## User Experience

### 1. Receiving Recommendations
After chatting with MediBot and receiving doctor recommendations, users will see a green "Send via Email" button below the Important Notes section.

### 2. Email Modal
Clicking the button opens a modal with:
- Clean, professional design
- Email input field with validation
- Cancel and Send buttons
- Focus on email input for quick typing
- Enter key support for quick sending

### 3. Email Delivery
- Instant validation of email format
- Loading state during sending
- Success/error feedback
- Email delivered within seconds

## Email Template Features

### Design Elements
- **Professional Header**: MediBot AI branding with gradient background
- **User Query Section**: Displays the original symptoms/question for context
- **Doctor Table**: Fully formatted table with all links and information
- **Important Disclaimer**: Medical disclaimers and legal information
- **Responsive Design**: Works on desktop and mobile email clients
- **Cross-client Compatibility**: Tested with major email providers

### Sample Email Content
The email includes:
- Professional MediBot AI header
- User's original query in a highlighted box
- Complete doctor recommendations table
- All doctor profile and map links
- Important medical disclaimers
- Timestamp and branding footer

## Security & Validation

### Email Validation
- Client-side format validation using regex
- Server-side validation before sending
- Protection against injection attacks
- Sanitized HTML content

### Error Handling
- Connection errors to SMTP server
- Invalid email format errors
- Missing or malformed data errors
- Graceful error messages to users

## Testing

### Email Service Tests
Run the test script to verify functionality:
```bash
python /tmp/test_email.py
```

This tests:
- Email template generation
- Email validation functions
- Doctor recommendation detection
- HTML template creation

### Manual Testing
1. Start the MediBot application
2. Chat with the bot to get doctor recommendations
3. Click the "Send via Email" button
4. Enter a valid email address
5. Verify email delivery and formatting

## Troubleshooting

### Common Issues

#### Email Not Sending
1. Check SMTP credentials in `.env` file
2. Verify SMTP2GO account is active
3. Check server logs for error messages
4. Test SMTP connection with `EmailService.test_connection()`

#### Email Formatting Issues
1. Verify HTML template is properly formatted
2. Check for missing CSS styles
3. Test with different email clients
4. Validate HTML using online validators

#### Button Not Appearing
1. Ensure doctor recommendations contain both `<table>` and "Important Notes:"
2. Check JavaScript console for errors
3. Verify the detection function logic
4. Test with sample doctor HTML content

## Future Enhancements

Potential improvements for future versions:
- Email templates for different specialties
- PDF attachment generation
- Email scheduling/reminders
- Email analytics and tracking
- Multiple recipient support
- Email template customization
- Integration with calendar applications

## Support

For technical support or questions about the email feature:
1. Check the server logs for detailed error messages
2. Verify SMTP2GO account status and limits
3. Test email functionality with the provided test scripts
4. Review the email service configuration

---

**Note**: This feature requires an active SMTP2GO account for email delivery. Free accounts have sending limits, so consider upgrading for production use.
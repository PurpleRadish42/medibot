# MediBot - AI-Powered Medical Assistant Platform

MediBot is a comprehensive AI-powered medical assistance platform that combines intelligent medical image analysis, conversational AI, and real doctor recommendations to provide users with professional healthcare guidance.

## Key Features

### Medical Image Analysis
- AI-Powered Analysis using OpenAI GPT-4 Vision API
- Multi-Specialty Support: dermatological, radiological, ophthalmological, dental, and wound images
- Automatic specialist recommendations based on analysis

### Intelligent Chat System
- AI-powered symptom triage
- Intelligent follow-up questions
- Specialist matching from 29 medical specialties

### Doctor Database
- 3,643+ verified medical professionals
- 29 specialties across major medical fields
- Location-based search with distance calculations
- Smart filtering by rating, experience, or proximity
- Direct profile links and Google Maps integration

### Security & Privacy
- Secure authentication with OTP verification
- Session management with MySQL
- Medical data privacy compliance
- Encrypted storage

### Data Management
- MySQL for user authentication and doctor database
- MongoDB for chat history and conversation tracking
- Persistent sessions across logins

## Quick Start

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- MongoDB Server
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/PurpleRadish42/medibot.git
cd medibot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medibot

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=medibot_chats

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
```

4. **Set up databases**

**MySQL Setup:**
```bash
# Create MySQL database and import doctor data
python scripts/setup_mysql_database.py
```

**MongoDB Setup:**
```bash
# Initialize MongoDB collections
python scripts/setup_mongodb.py
```

5. **Run the application**
```bash
python main.py
```

6. **Access the application**
Open your browser and navigate to:
- Main App: http://localhost:5000
- Login: http://localhost:5000/login
- Register: http://localhost:5000/register

## Project Structure

```
medibot/
├── main.py                      # Main Flask application
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
├── .env.example                 # Environment template
├── doctor_recommender.py        # Doctor recommendation logic
├── medibot2_auth.py            # Authentication system
├── mongodb_chat.py             # Chat history management
├── email_service.py            # Email functionality
├── otp_service.py              # OTP verification
│
├── src/                         # Source code (see src/README.md)
├── templates/                   # HTML templates
├── static/                      # Static assets
├── data/                        # Data files (see data/README.md)
├── scripts/                     # Setup scripts (see scripts/README.md)
├── config/                      # Configuration files
└── i18n/                        # Internationalization
```

Each folder contains its own README with specific details.

## 🎯 Usage Guide

### For Patients

1. **Register/Login**
   - Create an account or login
   - Verify email with OTP

2. **Chat with AI**
   - Describe your symptoms
   - Answer follow-up questions
   - Get specialist recommendations
   - View recommended doctors

3. **Analyze Medical Images**
   - Upload medical images (skin conditions, X-rays, etc.)
   - Select image category
   - Get AI analysis
   - Receive specialist recommendations

4. **Find Doctors**
   - Filter by specialty
   - Sort by rating, experience, or location
   - View doctor profiles
   - Get directions via Google Maps
   - Email recommendations to yourself

### For Developers

**Running in Development Mode:**
```bash
export FLASK_ENV=development
python main.py
```

**Running in Production:**
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## Configuration

### Database Configuration

**MySQL:**
- Database: `medibot`
- Tables: `users`, `doctors`, `user_sessions`, `chat_history`, `patient_symptoms`

**MongoDB:**
- Database: `medibot_chats`
- Collections: `chat_messages`, `chat_sessions`

### API Configuration

**OpenAI API:**
- Models: GPT-3.5-turbo, GPT-4, GPT-4-Vision
- Use case: Medical image analysis and chat conversations

## Technology Stack

- **Backend**: Flask 3.1.2
- **AI/ML**: OpenAI GPT-4 Vision, GPT-3.5-turbo
- **Databases**: MySQL 8.0+, MongoDB 4.0+
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Session-based with OTP
- **Image Processing**: Pillow (PIL)
- **Data Processing**: Pandas
- **Email**: SMTP (Gmail)

## Features in Detail

### Medical Image Analyzer
- Supports JPEG, PNG, WEBP formats
- Maximum file size: 20MB
- Automatic image optimization
- Base64 encoding for API transmission
- Real-time analysis with OpenAI Vision
- Detailed medical observations
- Severity assessment
- Urgency evaluation

### Chat System
- Context-aware conversations
- Medical history tracking
- Multi-turn dialogue support
- Specialty detection from symptoms
- Automatic doctor matching
- Interactive HTML tables with doctor info

### Doctor Recommendation Engine
- Location-based filtering
- Distance calculation (Haversine formula)
- Multi-factor sorting (rating, experience, distance)
- Real-time availability
- Contact information
- Profile links

## Security Features

- Password hashing with bcrypt
- Secure session management
- OTP-based verification
- Protected API endpoints
- Input validation
- SQL injection prevention
- XSS protection

## Responsive Design

- Mobile-friendly interface
- Touch-optimized controls
- Adaptive layouts
- Camera integration for mobile
- Progressive web app capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

**IMPORTANT MEDICAL DISCLAIMER:**

MediBot is designed to provide general medical information and guidance. It is NOT a substitute for professional medical advice, diagnosis, or treatment. 

- Always seek the advice of qualified healthcare providers
- Never disregard professional medical advice
- Do not delay seeking medical attention
- In case of emergency, call your local emergency services immediately

The AI-powered analysis is meant to assist in identifying potential specialists to consult, not to diagnose conditions.

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Email: support@medibot.com (if applicable)

## Acknowledgments

- OpenAI for GPT-4 Vision API
- Flask framework
- MongoDB and MySQL communities
- All contributors and testers

## Roadmap

- [ ] Multi-language support (i18n)
- [ ] Telemedicine integration
- [ ] Prescription management
- [ ] Appointment scheduling
- [ ] Lab report analysis
- [ ] Medication reminders
- [ ] Health tracking dashboard
- [ ] Integration with wearable devices

## Version History

### v1.0.0 (Current)
- Initial release
- Medical image analysis
- AI chat system
- Doctor recommendations
- User authentication
- Session management

---

Made for better healthcare accessibility

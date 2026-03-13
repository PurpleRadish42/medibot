# MediBot — AI-Powered Medical Assistant Platform

> **An end-to-end intelligent healthcare platform combining GPT-4 Vision medical image analysis, AI-driven symptom triage, and a curated database of 3,644 verified doctors — all delivered through a secure, multilingual web application.**

---

## Table of Contents

1. [Project Summary](#1-project-summary)
2. [Key Metrics at a Glance](#2-key-metrics-at-a-glance)
3. [Architecture Overview](#3-architecture-overview)
4. [Feature Deep-Dive](#4-feature-deep-dive)
5. [Technology Stack](#5-technology-stack)
6. [Dataset & Database](#6-dataset--database)
7. [AI & Model Details](#7-ai--model-details)
8. [API Reference](#8-api-reference)
9. [Security Design](#9-security-design)
10. [Internationalization](#10-internationalization)
11. [Project Structure](#11-project-structure)
12. [Quick Start](#12-quick-start)
13. [Configuration Reference](#13-configuration-reference)
14. [Roadmap](#14-roadmap)
15. [Disclaimer](#15-disclaimer)

---

## 1. Project Summary

**MediBot** is a full-stack, AI-powered medical assistance platform built with Python/Flask. It solves the problem of healthcare accessibility by providing patients with three core capabilities in one application:

1. **AI Symptom Triage** — A conversational AI assistant that gathers symptoms through contextual follow-up questions (powered by GPT-3.5-turbo/GPT-4), identifies the most appropriate medical specialty, and recommends verified local doctors.

2. **Medical Image Analysis** — Upload skin photos, X-rays, eye images, dental images, or wound photos to receive a GPT-4 Vision-powered analysis covering observations, severity, and urgency, with an automatic specialist referral.

3. **Doctor Discovery Engine** — Search, filter, and sort from a database of **3,644 verified Bangalore doctors** across **29 medical specialties** using location-aware ranking (Haversine-based distance), ratings, and years of experience.

MediBot targets patients who need guidance on *which specialist to see* before committing to a consultation — bridging the gap between "I have symptoms" and "I found the right doctor."

---

## 2. Key Metrics at a Glance

### Application Scale

| Metric | Value |
|---|---|
| Total API routes | **40+** |
| HTML templates | **14** |
| Python source files | **30+** |
| Total core code size | **~165 KB** |
| Python dependencies | **33 packages** |
| Supported languages (i18n) | **10** |

### Doctor Database

| Metric | Value |
|---|---|
| Total doctor records | **3,644** |
| Supported medical specialties | **29** |
| Data file size | **1.5 MB** (CSV) |
| Data columns per record | **12** |
| Location data | Latitude/Longitude for all records |
| Profile links | Practo profile + Google Maps per doctor |

### AI Capabilities

| Metric | Value |
|---|---|
| OpenAI models integrated | **3** (GPT-3.5-turbo, GPT-4, GPT-4 Vision) |
| Medical image categories supported | **5** (Skin, X-ray, Eye, Dental, Wound) |
| Max image upload size | **20 MB** |
| Supported image formats | JPEG, PNG, WebP |
| Conversation context window | **20 exchanges** (trimmed for memory efficiency) |
| Specialty-specific AI prompts | **6** custom prompt templates |
| Symptom follow-up questions | **3–5** per session |

### Database & Infrastructure

| Metric | Value |
|---|---|
| Primary databases | **2** (MySQL + MongoDB) |
| Fallback databases | **2** (SQLite — chat & doctors) |
| MySQL tables | **5** (users, doctors, user_sessions, chat_history, patient_symptoms) |
| MongoDB collections | **2** (chat_messages, chat_sessions) |
| Database indexes | **6** (optimized for specialty, city, rating, user_id, timestamp) |
| OTP attempt limit | **3** attempts per session |

### Medical Specialties Covered (29 Total)

General Physician · Cardiologist · Dermatologist · Gastroenterologist · Gynecologist · Neurologist · Orthopedist · Pediatrician · Psychiatrist · Pulmonologist · Rheumatologist · Urologist · ENT Specialist · Endocrinologist · Nephrologist · Oncologist · Dentist · Radiologist · Pathologist · Anesthesiologist · Neurosurgeon · Ayurveda · Unani · Trichologist · Sexologist · Surgeon · Plastic Surgeon · Cardiac Surgeon · Vascular Surgeon

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                             │
│               HTML5 / CSS3 / Vanilla JavaScript                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST (JSON)
┌──────────────────────────▼──────────────────────────────────────┐
│                    Flask Application (main.py)                  │
│                     40+ API Routes · Session Auth               │
├────────────┬────────────┬───────────────┬───────────────────────┤
│  Auth      │  Chat      │ Image Analysis│  Doctor Recommender   │
│  Module    │  Module    │  Module       │  Module               │
│(medibot2_  │(mongodb_   │(src/ai/*)     │(doctor_recommender.py)│
│ auth.py)   │ chat.py)   │               │                       │
└────────────┴──────┬─────┴───────┬───────┴──────────┬────────────┘
                    │             │                   │
         ┌──────────▼──┐  ┌───────▼──────┐  ┌────────▼──────────┐
         │  MongoDB    │  │  OpenAI API  │  │  MySQL / SQLite   │
         │ (chat logs) │  │  GPT-4 Vision│  │  (doctors, users) │
         └─────────────┘  │  GPT-3.5/4  │  └───────────────────┘
                          └─────────────┘
```

### Design Principles

- **Microservices-style modules** — authentication, chat, image analysis, and doctor search are completely decoupled.
- **Dual-database strategy** — MySQL handles structured data (users, doctors); MongoDB handles unstructured/flexible chat history.
- **Graceful degradation** — SQLite fallbacks activate automatically when MySQL or MongoDB are unavailable.
- **API-first design** — All business logic is exposed via JSON REST endpoints; the HTML templates are thin consumers of those APIs.
- **Lazy loading** — Heavy AI and medical analysis modules are imported only when needed.

---

## 4. Feature Deep-Dive

### 4.1 AI Symptom Triage Chat

The chat module uses a multi-turn conversation architecture:

1. User describes symptoms in free text.
2. The AI (GPT-3.5-turbo/GPT-4) asks **3–5 targeted follow-up questions** to narrow down the probable specialty.
3. Once sufficient context is gathered, the system emits a structured `SPECIALIST_RECOMMENDATION: [TYPE]` signal.
4. The doctor recommendation engine immediately queries the database and returns a formatted HTML table of the top matching doctors.

**Technical highlights:**
- Conversation history trimmed to the last 20 exchanges to stay within token limits.
- Chat sessions are persisted in MongoDB so users can resume previous conversations.
- Full conversation export (email) via SMTP2GO integration.
- Chat history accessible across logins with per-conversation delete and clear-all actions.

### 4.2 Medical Image Analyzer

Supports five medical image categories with specialty-specific GPT-4 Vision prompts:

| Category | Analysis Focus |
|---|---|
| **Skin / Dermatological** | Color, texture, pattern, lesion size, type, distribution |
| **Radiological (X-ray)** | Bone density, fractures, shadows, opacity, abnormalities |
| **Ophthalmological (Eye)** | Redness, clarity, pupil response, surface irregularities |
| **Dental** | Decay, alignment, gum condition, structural damage |
| **Wound Assessment** | Healing stage, infection signs, depth, wound edges |
| **General Medical** | Overall visual health indicators |

Each analysis returns:
- Detailed visual observations
- Probable condition(s)
- Severity level
- Urgency assessment
- Recommended specialist type
- Disclaimer and next-step guidance

### 4.3 Doctor Recommendation Engine

The engine combines three layers of intelligence:

1. **Specialty matching** — AI-determined specialty from chat or image analysis maps directly to the 29-specialty database.
2. **Location-aware ranking** — Uses the **Haversine formula** to calculate real-world distances (km) from the user's city to each doctor.
3. **Multi-factor sorting** — Configurable sort by:
   - `rating` (dp_score, 0–5)
   - `experience` (years of practice)
   - `distance` (km from user)
   - `combined` (weighted composite score)

**Additional features:**
- Direct Practo profile links for every doctor.
- Google Maps link for directions.
- Email doctor shortlist to yourself via SMTP2GO.
- CSV fallback ensures the engine works even without a live database.

### 4.4 User Authentication & Session Management

- **Registration** → Email OTP verification → Account activation.
- **Login** → Session cookie → MySQL `user_sessions` table.
- **Password recovery** → Email OTP → Secure reset flow.
- Session persistence across logins.
- OTP rate-limited to **3 attempts per session**.

### 4.5 Electronic Health Record (EHR) Lite

Users can save and retrieve their symptom history:
- `POST /api/save-symptoms` — Stores structured symptom data per user.
- `GET /api/get-symptoms` — Retrieves the patient's full symptom history.
- `POST /api/find-similar-symptoms` — Fuzzy-matches current symptoms against historical records.

---

## 5. Technology Stack

### Backend

| Technology | Version | Role |
|---|---|---|
| **Python** | 3.8+ | Core language |
| **Flask** | 3.1.0 | Web framework |
| **Werkzeug** | ≥3.1.0 | WSGI utilities, routing |
| **Gunicorn** | 21.2.0 | Production WSGI server |

### AI & Machine Learning

| Technology | Version | Role |
|---|---|---|
| **OpenAI API** | 1.54.4 | GPT-3.5-turbo, GPT-4, GPT-4 Vision |
| **Gradio** | 4.44.0 | Alternative UI interface |
| **Hugging Face Hub** | 0.20.3 | Model hub integration |

### Databases & Storage

| Technology | Version | Role |
|---|---|---|
| **MySQL** | 8.0+ | Users, doctors, sessions |
| **MongoDB** | 4.0+ | Chat history, conversations |
| **SQLite** | Built-in | Fallback storage |
| **PyMySQL** | 1.1.0 | MySQL Python driver |
| **pymongo** | 4.6.1 | MongoDB Python driver |

### Data Processing & Utilities

| Technology | Version | Role |
|---|---|---|
| **Pandas** | 2.1.4 | CSV data handling, dataframes |
| **NumPy** | 1.26.3 | Numerical computations |
| **Pillow** | 10.2.0 | Image processing, base64 encoding |
| **geopy** | 2.4.1 | Haversine distance calculations |
| **bcrypt** | 4.1.2 | Password hashing |
| **httpx** | 0.27.2 | Async HTTP client |
| **requests** | 2.31.0 | HTTP requests |
| **python-dotenv** | 1.0.0 | Environment variable management |

### Frontend

| Technology | Role |
|---|---|
| **HTML5** | Page structure |
| **CSS3** | Styling and responsive layout |
| **Vanilla JavaScript** | Dynamic interactions, fetch API calls |

---

## 6. Dataset & Database

### Doctor Database (`data/bangalore_doctors_final.csv`)

**Overview:**

| Property | Value |
|---|---|
| Total records | **3,644** |
| File size | **1.5 MB** |
| Columns | **12** |
| Geographic coverage | Bangalore, India |
| Data source | Scraped via `src/scrapers/practo_scraper/` |

**Schema:**

| Column | Type | Description |
|---|---|---|
| `name` | string | Doctor's full name |
| `specialty` | string | Medical specialty (29 types) |
| `degree` | string | Educational qualifications |
| `city` | string | City of practice |
| `location` | string | Detailed area/address |
| `latitude` | float | Geographic latitude |
| `longitude` | float | Geographic longitude |
| `consultation_fee` | float | Consultation cost (INR) |
| `year_of_experience` | int | Years of practice |
| `dp_score` | float | Doctor rating (0–5 scale) |
| `profile_url` | string | Practo profile link |
| `google_map_link` | string | Google Maps directions link |

### MySQL Schema

**Tables:**
- `users` — Account details, hashed passwords, verification status.
- `doctors` — Full doctor records mirrored from CSV.
- `user_sessions` — Active login sessions with expiry.
- `chat_history` — Fallback chat storage.
- `patient_symptoms` — EHR-lite symptom records per user.

**Indexes (performance-optimized):**
- `(specialty)` on doctors table
- `(city)` on doctors table
- `(dp_score)` on doctors table
- `(user_id, timestamp)` on chat_history
- `(conversation_id, message_order)` on chat_messages
- `(user_id, updated_at)` on chat_sessions

### MongoDB Schema

**Collections:**
- `chat_messages` — Individual messages with `user_id`, `conversation_id`, `role`, `content`, `timestamp`, `message_order`.
- `chat_sessions` — Session metadata with `conversation_id`, `user_id`, `created_at`, `updated_at`, `title`.

---

## 7. AI & Model Details

### Models in Use

| Model | Use Case | Context Window |
|---|---|---|
| **GPT-3.5-turbo** | Symptom triage, conversation, specialist matching | 20-exchange rolling window |
| **GPT-4** | Complex/advanced medical scenarios | 20-exchange rolling window |
| **GPT-4 Vision (gpt-4-vision-preview)** | Medical image analysis | Single-turn with base64 image |

### System Prompt Architecture

The triage assistant follows a structured pipeline:

```
1. GATHER — Ask 3-5 follow-up questions about symptoms, duration, severity
2. ANALYSE — Match symptom pattern to one of 29 medical specialties
3. RECOMMEND — Emit "SPECIALIST_RECOMMENDATION: [TYPE]"
4. DISPLAY — Query doctor DB → render HTML table in chat
```

### Specialty-Specific Vision Prompts

Each image category has a custom analysis prompt optimized for that domain:

```
Dermatological:  skin color, texture, pattern, size, lesion classification
Radiological:    bone density, fractures, opacity, structural abnormalities
Ophthalmological: redness, clarity, pupil shape, surface irregularities
Dental:          decay, alignment, gum health, structural damage
Wound:           healing stage, infection indicators, depth, edge condition
General:         overall visual health markers
```

### Fallback Behavior

When OpenAI is unavailable:
- **Chat:** Returns a graceful error with a prompt to retry.
- **Image analysis:** Falls back to a mock skin condition analyzer with rule-based responses.
- **Doctor recommendations:** CSV-based keyword matching kicks in.

---

## 8. API Reference

### Authentication Endpoints

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/api/register` | Register new user account | No |
| POST | `/api/verify-otp` | Verify email OTP | No |
| POST | `/api/login` | Log in user | No |
| POST | `/api/logout` | Log out user | Yes |
| POST | `/api/forgot-password` | Request password reset OTP | No |
| POST | `/api/reset-password` | Reset password with OTP | No |

### Chat & Conversation Endpoints

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/api/chat` | Send a chat message | Yes |
| POST | `/api/reset` | Reset current conversation | Yes |
| POST | `/api/chat-history` | Retrieve chat history | Yes |
| POST | `/api/get-conversations` | List all user conversations | Yes |
| POST | `/api/get-conversation-messages/{id}` | Get messages in a conversation | Yes |
| POST | `/api/delete-conversation/{id}` | Delete a conversation | Yes |
| POST | `/api/clear-chat-history` | Clear user's chat history | Yes |
| POST | `/api/clear-all-chats` | Delete all user chats | Yes |

### Medical Analysis Endpoints

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/api/analyze-medical-image` | Analyze uploaded medical image | Yes |
| POST | `/api/analyze-skin` | Skin condition analysis | Yes |
| GET | `/medical-image-analyzer` | Image analyzer page | Yes |
| GET | `/skin-analyzer` | Skin analyzer page | Yes |

### Doctor Search & Recommendation Endpoints

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/api/doctor-stats` | System/doctor statistics | No |
| POST | `/api/sort-doctors` | Sort doctors by criteria | Yes |
| POST | `/api/send-email` | Email doctor recommendations | Yes |

### User & Health Record Endpoints

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/api/update-user-city` | Update user's city for geo-search | Yes |
| GET | `/api/user` | Get user profile | Yes |
| POST | `/api/save-symptoms` | Save symptom record (EHR) | Yes |
| GET | `/api/get-symptoms` | Retrieve symptom history | Yes |
| POST | `/api/find-similar-symptoms` | Find similar historical symptoms | Yes |

### Diagnostic / Testing Endpoints

| Method | Path | Description | Auth Required |
|---|---|---|---|
| GET | `/api/status` | Server health check | No |
| POST | `/api/test-chat` | Test chat (public) | No |
| GET | `/test-fixes` | Test fixes page | No |
| GET | `/doctor-test` | Doctor recommendation test page | No |
| GET | `/test-direct` | Debug test page | No |

**Total REST API Endpoints: 40+**

---

## 9. Security Design

| Feature | Implementation |
|---|---|
| **Password hashing** | bcrypt (salted, adaptive cost) |
| **Session management** | Server-side sessions in MySQL `user_sessions` |
| **Email verification** | OTP sent to registered email; 3-attempt rate limit |
| **Protected routes** | `@login_required` decorator on all sensitive endpoints |
| **SQL injection prevention** | Parameterized queries throughout |
| **XSS protection** | Jinja2 auto-escaping in all templates |
| **Secrets management** | `.env` file (excluded from version control) |
| **Graceful errors** | All API errors return JSON, never stack traces |

---

## 10. Internationalization

MediBot supports **10 languages** via a custom i18n system:

| Language | Code | Script Direction |
|---|---|---|
| English | `en` | LTR |
| Hindi | `hi` | LTR |
| Kannada | `kn` | LTR |
| Tamil | `ta` | LTR |
| Telugu | `te` | LTR |
| Malayalam | `ml` | LTR |
| Bengali | `bn` | LTR |
| Gujarati | `gu` | LTR |
| Marathi | `mr` | LTR |
| Punjabi | `pa` | LTR |

**i18n Architecture:**
- `i18n/translator.py` — General text translations.
- `i18n/medical_translator.py` — Medical terminology translations.
- `i18n/translations/en.json`, `hi.json`, `kn.json` — Translation files (extendable).
- `config/languages.py` — Language metadata, RTL support flags, specialty name translations.
- Language selector component in `templates/components/language_selector.html`.

---

## 11. Project Structure

```
medibot/
├── main.py                          # Flask app — 40+ routes, entry point (~65 KB)
├── config.py                        # Centralised configuration
├── doctor_recommender.py            # Doctor search & recommendation engine (~33 KB)
├── medibot2_auth.py                 # Auth, user management, sessions (~35 KB)
├── mongodb_chat.py                  # Chat history (MongoDB) (~15 KB)
├── email_service.py                 # SMTP2GO email integration (~15 KB)
├── otp_service.py                   # OTP generation & verification (~19 KB)
├── requirements.txt                 # 33 Python dependencies
├── .env.example                     # Environment variable template
│
├── src/
│   ├── ai/
│   │   ├── medical_image_analyzer.py    # GPT-4 Vision medical image analysis
│   │   ├── skin_analyzer.py             # Skin condition analysis
│   │   ├── medical_image_router.py      # Routes images to specialty analyzers
│   │   ├── advanced_medical_analyzer.py # Advanced specialty-specific analysis
│   │   ├── enhanced_medical_analysis.py # Extended image processing
│   │   ├── fast_medical_ai.py           # Lightweight AI (quick response)
│   │   ├── medical_ai_lite.py           # Minimal dependency fallback
│   │   ├── medical_llm_analyzer.py      # LLM-based text analysis
│   │   ├── medical_specialist_models.py # Specialty-specific models
│   │   ├── specialized_medical_models.py
│   │   └── medical_vlm_models.py        # Vision-Language Models
│   ├── llm/
│   │   └── recommender.py               # OpenAI-powered doctor recommendations
│   ├── models/
│   │   └── doctor.py                    # Doctor/specialist dataclasses
│   ├── database/
│   │   └── connection.py                # MySQL connection handler
│   ├── api/
│   │   └── endpoints.py                 # REST API definitions
│   ├── ui/
│   │   └── gradio_app.py                # Gradio alternative interface
│   └── scrapers/
│       └── practo_scraper/              # Practo data scraper
│
├── templates/                           # Jinja2 HTML templates (14 files)
│   ├── base.html                        # Base layout
│   ├── login.html / register.html       # Auth pages
│   ├── dashboard.html                   # User dashboard
│   ├── chat.html                        # Chat interface
│   ├── medical_image_analyzer.html      # Image upload & analysis
│   ├── skin_analyzer.html               # Skin analysis
│   ├── verify_otp.html                  # OTP verification
│   ├── forgot_password.html             # Password recovery
│   ├── reset_password.html              # Password reset
│   └── components/
│       └── language_selector.html       # Language picker
│
├── data/
│   ├── bangalore_doctors_final.csv      # 3,644 doctor records (1.5 MB)
│   ├── bangalore_doctors_cleaned.db     # SQLite fallback (doctors)
│   └── chat_history.db                  # SQLite fallback (chat)
│
├── scripts/
│   ├── setup_mysql_database.py          # MySQL DB initialisation
│   ├── setup_mongodb.py                 # MongoDB initialisation
│   ├── create_mysql_database.py         # Schema creation
│   ├── import_csv_to_existing_db.py     # CSV import utility
│   ├── init_medibot2.py                 # General initialisation
│   └── medical_models_advanced.py       # Advanced model setup
│
├── config/
│   └── languages.py                     # i18n language config (10 languages)
│
└── i18n/
    ├── translator.py                    # General translator
    ├── medical_translator.py            # Medical term translator
    └── translations/
        ├── en.json                      # English strings
        ├── hi.json                      # Hindi strings
        └── kn.json                      # Kannada strings
```

---

## 12. Quick Start

### Prerequisites

- Python 3.8+
- MySQL Server 8.0+
- MongoDB 4.0+
- OpenAI API Key

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/PurpleRadish42/medibot.git
cd medibot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Initialise databases
python scripts/setup_mysql_database.py
python scripts/setup_mongodb.py

# 5. Run (development)
python main.py

# 5b. Run (production)
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

Open **http://localhost:5000** in your browser.

### Access Points

| URL | Description |
|---|---|
| `http://localhost:5000/` | Dashboard (redirects to login) |
| `http://localhost:5000/login` | Login page |
| `http://localhost:5000/register` | Registration page |
| `http://localhost:5000/chat` | AI chat interface |
| `http://localhost:5000/medical-image-analyzer` | Image analysis tool |
| `http://localhost:5000/skin-analyzer` | Skin analysis tool |
| `http://localhost:5000/api/status` | Server health check |

---

## 13. Configuration Reference

### Environment Variables

```env
# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development         # or production

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=medibot2

# MongoDB
MONGODB_URI=mongodb://user:pass@host:27017/medibot_chats
MONGODB_DATABASE=medibot_chats

# OpenAI
OPENAI_API_KEY=sk-...

# Email (SMTP2GO)
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_user
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=noreply@yourdomain.com
```

---

## 14. Roadmap

- [x] AI symptom triage chat (GPT-3.5-turbo / GPT-4)
- [x] GPT-4 Vision medical image analysis
- [x] Doctor recommendation engine (3,644 records, 29 specialties)
- [x] Location-aware doctor ranking (Haversine formula)
- [x] Secure authentication (OTP email verification)
- [x] Persistent chat history (MongoDB)
- [x] EHR-lite symptom storage
- [x] Email doctor recommendations (SMTP2GO)
- [x] Multi-language support (10 languages, i18n ready)
- [x] Skin condition specialized analysis
- [ ] Telemedicine / video consultation integration
- [ ] Appointment scheduling system
- [ ] Lab report (PDF) analysis
- [ ] Medication reminders and tracking
- [ ] Wearable device data integration
- [ ] Mobile app (React Native)
- [ ] Doctor rating & review system
- [ ] Insurance / coverage filtering

---

## 15. Disclaimer

> **MediBot is NOT a substitute for professional medical advice, diagnosis, or treatment.**
>
> The AI-powered analysis and recommendations are intended solely to help users identify which type of medical specialist may be appropriate to consult. Always seek the advice of qualified healthcare providers with any questions about medical conditions. Never disregard professional medical advice or delay seeking it because of something produced by this application. In emergencies, call your local emergency services immediately.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m 'Add your feature'`.
4. Push: `git push origin feature/your-feature`.
5. Open a Pull Request.

## License

MIT License — see `LICENSE` for details.

## Acknowledgements

- [OpenAI](https://openai.com) — GPT-4 Vision & GPT-3.5-turbo APIs
- [Flask](https://flask.palletsprojects.com) — Web framework
- [Practo](https://practo.com) — Doctor data source
- MongoDB & MySQL communities

---

*Built to make quality healthcare guidance accessible to everyone.*

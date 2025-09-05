# Essential Files to Keep:

## Core Application Files:
- main.py                          # Main Flask application
- config.py                        # Configuration
- requirements.txt                 # Dependencies
- medibot2_auth.py                # Authentication
- doctor_recommender.py            # Doctor recommendation logic
- mongodb_chat.py                  # Chat history
- email_service.py                # Email functionality

## Source Code (src/):
- src/llm/recommender.py          # Medical recommender
- src/ai/fast_medical_ai.py       # Fast medical AI
- src/models/doctor.py            # Doctor model
- src/database/connection.py      # Database connection
- src/ui/gradio_app.py           # Gradio interface

## Templates:
- templates/index.html            # Main page
- templates/chat.html             # Chat interface
- templates/dashboard.html        # Dashboard
- templates/login.html            # Login page
- templates/register.html         # Register page
- templates/skin_analyzer.html    # Medical image analyzer

## Configuration:
- .env                           # Environment variables
- .gitignore                     # Git ignore

## Database:
- cleaned_doctors_full.csv       # Doctor data

# Files to Delete (Analysis, Test, Debug, Duplicate):

## Analysis Files:
- analyze_*.py (all analyze files)
- check_*.py (all check files)
- clean_*.py (all clean files)
- comprehensive_db_setup_filtered.py
- create_clean_doctor_database.py
- create_mysql_database.py
- debug_*.py (all debug files)
- find_errors.py
- final_*.py (all final files)
- import_csv_to_existing_db.py
- insert_*.py (all insert files)
- investigate_errors.py
- quick_*.py (all quick files)
- setup_*.py (all setup files)
- simple_*.py (all simple files)
- verify_*.py (all verify files)

## Test Files:
- test_*.py (all test files)
- test_*.html (all test files)

## Documentation/Temporary:
- *.md (markdown files - can be moved to docs folder)
- enhanced_table_test.html
- fixed_location_test.html
- cookies.txt

## Internationalization (if not needed):
- babel.cfg
- i18n/ (entire folder)
- flask_i18n_updates.py
- i18n_main_updates.py
- i18n_requirements.txt
- llm_i18n_updates.py
- simple_translator.py

## Old/Unused:
- init_medibot2.py
- main_additions.py
- medical_models_advanced.py
- Web_Scraping/ (if not needed)

## Requirements files (keep only main one):
- requirements_*.txt (all except requirements.txt)

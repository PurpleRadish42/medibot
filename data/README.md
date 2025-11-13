# Data Files

This directory contains data files used by the MediBot application.

## Files

- `bangalore_doctors_final.csv` - Primary doctor database
  - Contains 3,643 doctor records
  - 29 medical specialties
  - Includes: name, specialty, rating, experience, location, coordinates, contact info
  - Used for doctor recommendations and search

- `bangalore_doctors_cleaned.db` - SQLite database (fallback)
  - SQLite version of doctor data
  - Used when MySQL is unavailable
  - Contains same doctor information as CSV

- `chat_history.db` - SQLite chat storage (fallback)
  - Stores conversation history
  - Used when MongoDB is unavailable
  - Contains user chat messages and sessions

## Data Schema

### Doctor Records
```
- name: Doctor's full name
- specialty: Medical specialty
- rating: Average rating (0-5)
- experience: Years of experience
- location: City/area
- latitude: Geographic coordinate
- longitude: Geographic coordinate
- contact: Phone number
- email: Email address
- profile_link: Online profile URL
```

## Import

Doctor data is imported during setup using `scripts/setup_mysql_database.py`.

## Updates

To update doctor data, replace the CSV file and run the setup script again.

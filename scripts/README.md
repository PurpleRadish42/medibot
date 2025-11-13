# Setup Scripts

This directory contains database setup and utility scripts.

## Files

- `setup_mysql_database.py` - Initialize MySQL database and tables
  - Creates `medibot` database
  - Sets up user tables, doctor tables, session tables
  - Imports doctor data from CSV

- `setup_mongodb.py` - Initialize MongoDB collections
  - Creates `medibot_chats` database
  - Sets up chat message collections
  - Configures indexes for performance

- `create_mysql_database.py` - Alternative MySQL setup script
  - Creates database schema
  - Sets up initial data

## Usage

Run these scripts once during initial setup:

```bash
# Setup MySQL
python scripts/setup_mysql_database.py

# Setup MongoDB
python scripts/setup_mongodb.py
```

## Requirements

Ensure environment variables are configured in `.env` before running:
- MySQL credentials
- MongoDB connection URI
- Database names

## Note

These scripts are idempotent - safe to run multiple times without duplicating data.

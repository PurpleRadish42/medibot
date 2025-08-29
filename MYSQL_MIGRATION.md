# MySQL Migration Guide

This guide will help you migrate your MediBot application from SQLite to MySQL.

## Prerequisites

1. **MySQL Server**: Ensure MySQL 5.7+ or MariaDB 10.2+ is installed and running
2. **Python Dependencies**: Install the required MySQL driver

```bash
pip install -r requirements.txt
```

## Step 1: Set Environment Variables

Copy the example environment file and configure your MySQL settings:

```bash
cp .env.example .env
```

Edit `.env` file with your MySQL credentials:

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medibot

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
```

## Step 2: Initialize MySQL Database

Run the database initialization script:

```bash
python init_mysql.py
```

This script will:
- Create the database if it doesn't exist
- Create necessary tables (users, user_sessions, chat_history)
- Test the connection

## Step 3: Migrate Existing Data (Optional)

If you have existing SQLite data to migrate:

```bash
python migrate_to_mysql.py
```

This script will:
- Create a backup of your SQLite database
- Transfer all users, sessions, and chat history to MySQL
- Preserve all existing data and relationships

## Step 4: Test the Application

Start the application to verify everything works:

```bash
python main.py
```

The application should now:
- Connect to MySQL instead of SQLite
- Maintain all existing functionality
- Show "MySQL database initialized successfully" in the logs

## Step 5: Verify Migration

Check your data was migrated correctly:

```bash
python show_db.py
```

This will show:
- All users in the MySQL database
- Total chat messages
- Active sessions

## Configuration Details

### Database Schema Changes

The migration updates the SQLite schema to MySQL equivalents:

| SQLite | MySQL |
|--------|-------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT AUTO_INCREMENT PRIMARY KEY` |
| `TEXT` | `VARCHAR(255)` or `TEXT` |
| `BOOLEAN` | `BOOLEAN` |
| `TIMESTAMP` | `TIMESTAMP` |

### MySQL-Specific Features Added

- **Character Set**: UTF8MB4 for full Unicode support
- **Storage Engine**: InnoDB for ACID compliance and foreign keys
- **Indexes**: Added for better query performance
- **Foreign Key Constraints**: Proper CASCADE deletes

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_HOST` | MySQL server hostname | `localhost` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_USERNAME` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | _(empty)_ |
| `MYSQL_DATABASE` | Database name | `medibot` |

## Troubleshooting

### Connection Issues

1. **MySQL not running**: Start MySQL service
   ```bash
   # Ubuntu/Debian
   sudo systemctl start mysql
   
   # macOS with Homebrew
   brew services start mysql
   ```

2. **Access denied**: Check username/password in `.env` file

3. **Database doesn't exist**: Run `init_mysql.py` to create it

### Migration Issues

1. **SQLite file not found**: Ensure `users.db` exists in project root

2. **Duplicate users**: Migration skips existing users automatically

3. **Foreign key errors**: Ensure users are migrated before sessions/chats

### Performance Tips

1. **Connection Pooling**: For production, consider using connection pooling
2. **Indexes**: The migration adds indexes for common queries
3. **Regular Maintenance**: Run `OPTIMIZE TABLE` periodically

## Production Deployment

### Security Considerations

1. **Environment Variables**: Never commit real credentials to git
2. **MySQL User**: Create dedicated MySQL user with limited privileges
3. **SSL/TLS**: Enable encrypted connections for production
4. **Firewall**: Restrict MySQL port access

### Example Production Setup

```sql
-- Create dedicated database user
CREATE USER 'medibot_user'@'%' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON medibot.* TO 'medibot_user'@'%';
FLUSH PRIVILEGES;
```

Update `.env`:
```env
MYSQL_USERNAME=medibot_user
MYSQL_PASSWORD=secure_password
```

## Rollback Plan

If you need to rollback to SQLite:

1. The migration script creates a backup: `users_backup_YYYYMMDD_HHMMSS.db`
2. Restore this file as `users.db`
3. Update imports back to `sqlite3`
4. Revert database connection code

## Support

If you encounter issues:

1. Check MySQL error logs
2. Verify environment variables are set correctly
3. Ensure MySQL server is accessible
4. Test connection with `mysql` command line client

The migration maintains full backward compatibility with your existing application logic while providing the benefits of a production-ready MySQL database.
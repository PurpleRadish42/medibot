# Database Fallback Implementation

## Overview
This implementation modifies the MediBot application to load doctor data from a MySQL database with automatic fallback to CSV if the database connection fails.

## Changes Made

### 1. Modified `doctor_recommender.py`
- **Database Integration**: Added MySQL database connectivity using `mysql-connector-python`
- **Fallback Mechanism**: Automatic fallback to CSV file if database connection fails
- **Data Source Tracking**: Added `data_source` property to track whether data comes from 'database' or 'csv'
- **Enhanced Statistics**: Updated statistics to include data source information

### 2. Enhanced `src/database/connection.py`
- **MySQL Support**: Complete MySQL database connection handling
- **Connection Testing**: Added methods to test database connectivity
- **Error Handling**: Robust error handling for database operations

### 3. Database Setup Script (`setup_mysql_database.py`)
- **Table Creation**: Creates the `doctors` table with proper schema
- **Data Import**: Imports CSV data into MySQL database
- **Data Verification**: Verifies imported data integrity

### 4. Testing Scripts
- **`test_database_fallback.py`**: Comprehensive testing of database fallback functionality
- **`verify_implementation.py`**: Simple verification of implementation completeness

### 5. Configuration
- **Environment Variables**: Uses `.env` file for database credentials
- **Requirements**: Added `mysql-connector-python` to requirements.txt

## Database Schema

```sql
CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    speciality VARCHAR(255) NOT NULL,
    degree VARCHAR(500),
    city VARCHAR(100) NOT NULL,
    location VARCHAR(500),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    consultation_fee DECIMAL(10, 2),
    year_of_experience INT,
    dp_score DECIMAL(3, 2),
    profile_url TEXT,
    google_map_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speciality (speciality),
    INDEX idx_city (city),
    INDEX idx_dp_score (dp_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Environment Variables Required

```bash
# MySQL Database Configuration
MYSQL_HOST=your_database_host
MYSQL_PORT=3306
MYSQL_USERNAME=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database_name
```

## Usage

### 1. Setup Database (One-time)
```bash
python setup_mysql_database.py
```

### 2. Test Implementation
```bash
python verify_implementation.py
python test_database_fallback.py
```

### 3. Normal Operation
The `DoctorRecommender` class will now:
1. Try to connect to MySQL database first
2. If successful, load doctor data from database
3. If database connection fails, automatically fallback to CSV file
4. Continue operating normally regardless of data source

## Fallback Behavior

### Database Connection Success
- ✅ Loads data from MySQL database
- ✅ `data_source = 'database'`
- ✅ Full functionality available

### Database Connection Failure
- ⚠️ Logs database connection error
- ✅ Automatically loads from CSV file: `C:\Users\kmgs4\Documents\Christ Uni\trimester 4\nndl\project\medibot\data\bangalore_doctors_final.csv`
- ✅ `data_source = 'csv'`
- ✅ Full functionality available (no feature loss)

## Benefits

1. **High Availability**: Application continues working even if database is unavailable
2. **Performance**: Database queries are typically faster than CSV parsing
3. **Scalability**: Database can handle larger datasets and concurrent access
4. **Maintainability**: Data can be updated in database without code changes
5. **Monitoring**: Easy to track data source being used

## Files Modified/Created

### Modified Files:
- `doctor_recommender.py` - Added database connectivity with fallback
- `src/database/connection.py` - Enhanced database utilities
- `requirements.txt` - Added mysql-connector-python

### Created Files:
- `setup_mysql_database.py` - Database setup and data import
- `test_database_fallback.py` - Testing script
- `verify_implementation.py` - Implementation verification
- `DATABASE_FALLBACK_README.md` - This documentation

## Integration with Existing Code

The changes are backward compatible. Existing code using `DoctorRecommender` will work without modifications:

```python
# This code remains unchanged
from doctor_recommender import DoctorRecommender
dr = DoctorRecommender()
doctors = dr.recommend_doctors("cardiologist", "Bangalore", limit=3)
```

The only difference is that data will now come from the database (with CSV fallback) instead of CSV only.

## Monitoring Data Source

You can check which data source is being used:

```python
dr = DoctorRecommender()
info = dr.get_data_source_info()
print(f"Data source: {info['source']}")  # 'database' or 'csv'
print(f"Total records: {info['total_records']}")
```

## Troubleshooting

### Database Connection Issues
1. Verify `.env` file has correct database credentials
2. Check database server accessibility
3. Ensure `doctors` table exists in database
4. Application will automatically fallback to CSV

### CSV Fallback Issues
1. Ensure CSV file exists at the specified path
2. Verify CSV file format matches expected columns
3. Check file permissions

## Future Enhancements

1. **Connection Pooling**: Implement database connection pooling for better performance
2. **Caching**: Add data caching to reduce database load
3. **Sync Mechanism**: Automatic sync between CSV and database
4. **Health Checks**: API endpoints to monitor data source health

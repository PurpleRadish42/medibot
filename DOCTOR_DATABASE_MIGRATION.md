# Doctor Database Migration Guide

This guide explains how to migrate from the CSV-based doctor recommendation system to a MySQL database system.

## Overview

The system has been updated to support both MySQL database and CSV file as data sources for doctor recommendations. The database provides better performance, concurrent access, and scalability for production deployment.

## Migration Process

### Step 1: Database Setup

1. **Initialize the Database**
   ```bash
   python init_medibot2.py
   ```
   This creates the `doctors` table with the following schema:
   
   ```sql
   CREATE TABLE doctors (
       id INT AUTO_INCREMENT PRIMARY KEY,
       city VARCHAR(100) NOT NULL,
       speciality VARCHAR(100) NOT NULL,
       profile_url TEXT,
       name VARCHAR(200) NOT NULL,
       degree VARCHAR(100),
       year_of_experience INT,
       location VARCHAR(200),
       dp_score DECIMAL(3,1),
       npv INT,
       consultation_fee INT,
       google_map_link TEXT,
       scraped_at DATETIME,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       -- Indexes for performance
       INDEX idx_city (city),
       INDEX idx_speciality (speciality),
       INDEX idx_name (name),
       INDEX idx_city_speciality (city, speciality)
   )
   ```

### Step 2: Data Migration

1. **Run the Migration Script**
   ```bash
   python migrate_csv_to_db.py
   ```
   
   This script will:
   - Load data from `cleaned_doctors_full.csv`
   - Connect to your MySQL database
   - Create the doctors table if it doesn't exist
   - Migrate all 2046+ doctor records
   - Handle data type conversions and null values
   - Provide migration statistics

2. **Migration Features**
   - **Batch Processing**: Migrates data in batches of 100 for efficiency
   - **Data Validation**: Handles missing values and data type conversions
   - **Progress Tracking**: Shows real-time migration progress
   - **Safety Check**: Asks before overwriting existing data
   - **Verification**: Validates migration success with sample queries

### Step 3: Application Configuration

The `DoctorRecommender` class now supports both modes:

```python
# Use database (default)
recommender = DoctorRecommender(use_database=True)

# Use CSV fallback
recommender = DoctorRecommender(use_database=False)

# Automatic fallback if database is unavailable
recommender = DoctorRecommender()  # Will try database, fallback to CSV
```

## Database vs CSV Performance

### Database Advantages
- **Performance**: Direct SQL queries are faster than DataFrame operations
- **Memory Efficiency**: Loads only required data instead of entire dataset
- **Concurrent Access**: Supports multiple users simultaneously
- **Scalability**: Can handle larger datasets efficiently
- **Data Integrity**: ACID compliance and constraints
- **Filtering**: Database-level filtering reduces network traffic

### Example Performance Comparison

**Database Query (Optimized)**:
```sql
SELECT * FROM doctors 
WHERE speciality = 'Cardiologist' 
AND city LIKE '%Bangalore%' 
ORDER BY dp_score DESC 
LIMIT 5
```

**CSV Processing**:
```python
# Loads entire 2046-row dataset into memory
df = pd.read_csv('cleaned_doctors_full.csv')
filtered = df[df['speciality'] == 'Cardiologist']
filtered = filtered[filtered['city'].str.contains('Bangalore')]
sorted_df = filtered.sort_values('dp_score', ascending=False)
result = sorted_df.head(5)
```

## Environment Configuration

Update your `.env` file with database credentials:

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medibot2
```

## API Changes

The public API remains unchanged, but with improved functionality:

```python
from doctor_recommender import DoctorRecommender

# Initialize (will auto-detect best data source)
recommender = DoctorRecommender()

# Same API as before
doctors = recommender.recommend_doctors(
    specialist_type="cardiologist",
    city="Bangalore",
    limit=5,
    sort_by="rating"
)

# Enhanced statistics with data source info
stats = recommender.get_statistics()
print(f"Data source: {stats['data_source']}")  # 'database' or 'csv'
```

## Deployment for Digital Ocean

### Database Setup on Digital Ocean

1. **Create MySQL Database**
   - Use Digital Ocean's Managed Databases
   - Or set up MySQL on a Droplet

2. **Update Environment Variables**
   ```env
   MYSQL_HOST=your-database-host.db.ondigitalocean.com
   MYSQL_PORT=25060
   MYSQL_USERNAME=doadmin
   MYSQL_PASSWORD=your-secure-password
   MYSQL_DATABASE=medibot2
   ```

3. **Secure Connection**
   - Enable SSL/TLS for production
   - Use connection pooling for better performance
   - Set up database user with minimal required permissions

### Production Migration Steps

1. **Initialize Production Database**
   ```bash
   python init_medibot2.py
   ```

2. **Migrate Data**
   ```bash
   python migrate_csv_to_db.py
   ```

3. **Verify Migration**
   ```bash
   python -c "
   from doctor_recommender import DoctorRecommender
   dr = DoctorRecommender()
   print(dr.get_statistics())
   "
   ```

4. **Update Application**
   - Set `use_database=True` (default)
   - Remove or backup CSV files if desired
   - Monitor application logs for any issues

## Troubleshooting

### Common Issues

1. **MySQL Connection Failed**
   ```
   Error: (2003, "Can't connect to MySQL server")
   ```
   - Check MySQL server is running
   - Verify host, port, username, password in `.env`
   - Check firewall settings
   - Application will automatically fallback to CSV

2. **Table Not Found**
   ```
   Error: Table 'doctors' doesn't exist
   ```
   - Run `python init_medibot2.py` to create tables

3. **Migration Fails**
   ```
   Error: CSV file not found
   ```
   - Ensure `cleaned_doctors_full.csv` exists
   - Check file permissions

### Verification Commands

```bash
# Test database connection
python -c "
from doctor_recommender import DoctorRecommender
dr = DoctorRecommender()
if dr.use_database:
    print('✅ Database mode active')
    print(dr.get_statistics())
else:
    print('📂 CSV fallback mode')
"

# Test doctor search
python -c "
from doctor_recommender import DoctorRecommender
dr = DoctorRecommender()
doctors = dr.recommend_doctors('cardiologist', 'Bangalore', limit=3)
print(f'Found {len(doctors)} doctors')
for d in doctors:
    print(f'- Dr. {d[\"name\"]} ({d[\"specialty\"]})')
"
```

## Benefits of Database Migration

1. **Scalability**: Ready for production deployment
2. **Performance**: Faster queries and reduced memory usage
3. **Reliability**: Database backup and recovery capabilities
4. **Flexibility**: Easy to add new features (ratings, reviews, etc.)
5. **Integration**: Seamless integration with existing user/chat database
6. **Maintenance**: Easier data updates and corrections

## Rollback Plan

If you need to rollback to CSV-only mode:

1. **Force CSV Mode**
   ```python
   recommender = DoctorRecommender(use_database=False)
   ```

2. **Update Application Code**
   ```python
   # In main.py or wherever DoctorRecommender is initialized
   doctor_recommender = DoctorRecommender(use_database=False)
   ```

The CSV file (`cleaned_doctors_full.csv`) is preserved and can serve as a backup.
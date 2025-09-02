# Doctor Recommendation System - Database Migration

## Quick Start

The doctor recommendation system now supports both MySQL database and CSV file as data sources. Database mode provides better performance and scalability for production deployment.

### 1. Setup Database (Production)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your MySQL credentials
# Update MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE

# Initialize database schema
python init_medibot2.py

# Migrate CSV data to database
python migrate_csv_to_db.py

# Test the setup
python test_doctor_database.py
```

### 2. Quick Test (Development)

```bash
# Test with CSV fallback (no database required)
python doctor_recommender.py
```

## Usage

```python
from doctor_recommender import DoctorRecommender

# Initialize (auto-detects best data source)
recommender = DoctorRecommender()

# Find doctors
doctors = recommender.recommend_doctors(
    specialist_type="cardiologist",
    city="Bangalore", 
    limit=5,
    sort_by="rating"  # "rating", "experience", or "fee"
)

# Get statistics
stats = recommender.get_statistics()
print(f"Total doctors: {stats['total_doctors']}")
print(f"Data source: {stats['data_source']}")  # 'database' or 'csv'
```

## Data Sources

### Database Mode (Recommended)
- ✅ Better performance with direct SQL queries
- ✅ Supports concurrent users
- ✅ Memory efficient
- ✅ Production ready
- ✅ Automatic fallback to CSV if unavailable

### CSV Fallback Mode
- ✅ No database setup required
- ✅ Works offline
- ✅ Same API and functionality
- ⚠️ Loads entire dataset into memory
- ⚠️ Not suitable for concurrent users

## Available Data

- **2046 doctor records** from `cleaned_doctors_full.csv`
- **37 medical specialties** including:
  - Cardiologist, Dermatologist, Neurologist
  - Ophthalmologist, Orthopedist, Pediatrician
  - General Physician, ENT Specialist, etc.
- **Complete doctor information**:
  - Name, degree, experience, location
  - Consultation fees, ratings, contact info
  - Profile URLs and Google Maps links

## Files

- `doctor_recommender.py` - Main recommendation system
- `init_medibot2.py` - Database schema initialization  
- `migrate_csv_to_db.py` - CSV to database migration
- `test_doctor_database.py` - Functionality testing
- `DOCTOR_DATABASE_MIGRATION.md` - Detailed migration guide
- `cleaned_doctors_full.csv` - Source data (backup)

## Digital Ocean Deployment

1. **Create MySQL Database** (Managed Database recommended)
2. **Update Environment Variables** with production credentials
3. **Run Migration Scripts** on your droplet
4. **Enable SSL/TLS** for secure connections
5. **Configure Connection Pooling** for better performance

See `DOCTOR_DATABASE_MIGRATION.md` for detailed deployment instructions.

## Backward Compatibility

The system maintains full backward compatibility:
- Existing API remains unchanged
- CSV mode works exactly as before
- Automatic graceful fallback to CSV
- No breaking changes to existing code

## Performance Benefits

Database mode provides significant performance improvements:
- **Direct SQL filtering** instead of DataFrame operations
- **Memory efficiency** - only loads required data
- **Indexed queries** for fast specialty/city lookups
- **Concurrent access** support for multiple users
- **Scalable** for larger datasets
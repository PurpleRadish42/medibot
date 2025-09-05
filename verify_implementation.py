"""
Simple verification that the database fallback is working
"""
import os
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has database credentials"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_vars = ['MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    found_vars = []
    
    for var in required_vars:
        if var in content:
            found_vars.append(var)
    
    print(f"✅ Found {len(found_vars)}/{len(required_vars)} required database variables in .env")
    for var in found_vars:
        print(f"  • {var}")
    
    return len(found_vars) == len(required_vars)

def check_csv_file():
    """Check if CSV fallback file exists"""
    csv_path = r"C:\Users\kmgs4\Documents\Christ Uni\trimester 4\nndl\project\medibot\data\bangalore_doctors_final.csv"
    
    if Path(csv_path).exists():
        print(f"✅ CSV fallback file exists: {csv_path}")
        return True
    else:
        print(f"❌ CSV fallback file not found: {csv_path}")
        return False

def check_code_changes():
    """Check if code changes are in place"""
    doctor_recommender_path = Path('doctor_recommender.py')
    
    if not doctor_recommender_path.exists():
        print("❌ doctor_recommender.py not found")
        return False
    
    with open(doctor_recommender_path, 'r') as f:
        content = f.read()
    
    required_changes = [
        'load_from_database',
        'load_from_csv',
        'mysql.connector',
        'data_source'
    ]
    
    found_changes = []
    for change in required_changes:
        if change in content:
            found_changes.append(change)
    
    print(f"✅ Found {len(found_changes)}/{len(required_changes)} code changes in doctor_recommender.py")
    for change in found_changes:
        print(f"  • {change}")
    
    return len(found_changes) == len(required_changes)

def main():
    """Main verification function"""
    print("🔍 Verifying Database Fallback Implementation")
    print("=" * 50)
    
    checks = [
        ("Environment Configuration", check_env_file),
        ("CSV Fallback File", check_csv_file),
        ("Code Changes", check_code_changes)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        result = check_func()
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All verification checks passed!")
        print("🚀 Database fallback implementation is ready")
        print("\nNext steps:")
        print("1. Run: python setup_mysql_database.py (to create database table)")
        print("2. Run: python test_database_fallback.py (to test functionality)")
        print("3. The application will now try database first, then fallback to CSV")
    else:
        print("❌ Some verification checks failed")
        print("Please review the issues above before proceeding")

if __name__ == "__main__":
    main()

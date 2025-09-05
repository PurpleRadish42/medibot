#!/usr/bin/env python3
"""
Script to check coordinate data in the doctors database
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USERNAME'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4'
}

def check_coordinates():
    """Check the coordinate data in the database"""
    try:
        print("🔄 Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Sample coordinates for cardiologists
        cursor.execute('''
            SELECT name, latitude, longitude, bangalore_location 
            FROM doctors 
            WHERE specialty = 'cardiologist' 
            AND latitude IS NOT NULL 
            AND longitude IS NOT NULL 
            LIMIT 10
        ''')
        
        print("\n📍 Sample Cardiologist Coordinates:")
        print("=" * 70)
        print(f"{'Name':<30} {'Latitude':<12} {'Longitude':<12} {'Location'}")
        print("-" * 70)
        
        for row in cursor.fetchall():
            name, lat, lng, location = row
            print(f"{name[:29]:<30} {lat:<12} {lng:<12} {location}")
        
        # Check coordinate ranges
        cursor.execute('''
            SELECT 
                MIN(latitude) as min_lat, 
                MAX(latitude) as max_lat,
                MIN(longitude) as min_lng, 
                MAX(longitude) as max_lng,
                COUNT(*) as total_coords
            FROM doctors 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ''')
        
        result = cursor.fetchone()
        min_lat, max_lat, min_lng, max_lng, total_coords = result
        
        print(f"\n📊 Coordinate Ranges:")
        print("=" * 50)
        print(f"Total doctors with coordinates: {total_coords}")
        print(f"Latitude range: {min_lat} to {max_lat}")
        print(f"Longitude range: {min_lng} to {max_lng}")
        
        # Bangalore should have coordinates around:
        # Latitude: 12.8 to 13.2
        # Longitude: 77.4 to 77.8
        print(f"\n✅ Expected Bangalore ranges:")
        print(f"Latitude: 12.8 to 13.2")
        print(f"Longitude: 77.4 to 77.8")
        
        if min_lat < 10 or max_lat > 15 or min_lng < 75 or max_lng > 80:
            print("\n⚠️  WARNING: Coordinates appear to be outside Bangalore ranges!")
        else:
            print("\n✅ Coordinates appear to be in expected Bangalore ranges")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_coordinates()

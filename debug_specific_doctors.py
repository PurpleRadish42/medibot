#!/usr/bin/env python3
"""
Debug specific doctor coordinates that are showing wrong distances
"""

import mysql.connector
import os
import math
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USERNAME'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4'
}

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula (in kilometers)"""
    try:
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r
    except (TypeError, ValueError):
        return float('inf')

def debug_specific_doctors():
    print("🔍 Debugging Specific Doctor Distances")
    print("=" * 50)
    
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    # Get the exact doctors showing wrong distances
    problem_doctors = ["M Sudhakar Rao", "Anusha Buchade", "Ameet Oswal"]
    
    for doctor_name in problem_doctors:
        cursor.execute("""
            SELECT name, latitude, longitude 
            FROM doctors 
            WHERE name = %s 
            LIMIT 1
        """, (doctor_name,))
        
        result = cursor.fetchone()
        if result:
            name, lat, lng = result
            print(f"\n👨‍⚕️ {name}:")
            print(f"   📍 Database coordinates: ({lat}, {lng})")
            
            # Test distance to Koramangala
            user_lat, user_lng = 12.9352, 77.6245
            if lat is not None and lng is not None:
                distance = calculate_distance(user_lat, user_lng, lat, lng)
                print(f"   📏 Calculated distance: {distance:.2f} km")
                
                if distance > 1000:
                    print(f"   ⚠️  PROBLEM: Distance > 1000km suggests coordinate issue")
                    print(f"   🔍 Raw values - lat: {type(lat)} {lat}, lng: {type(lng)} {lng}")
                else:
                    print(f"   ✅ Distance looks reasonable")
            else:
                print(f"   ❌ NULL coordinates")
        else:
            print(f"\n❌ Doctor '{doctor_name}' not found")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    debug_specific_doctors()

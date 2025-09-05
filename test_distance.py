#!/usr/bin/env python3
"""
Test the distance calculation manually
"""

import math

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
        return float('inf')  # Return infinite distance for invalid coordinates

# Test with actual coordinates from the database
print("🧪 Testing Distance Calculations")
print("=" * 50)

# User location: Koramangala
user_lat, user_lon = 12.9352, 77.6245

# Doctor coordinates from database sample
doctors = [
    ("Mohan Kumar HN", 12.97708818, 77.60396075),
    ("A Naga Srinivaas", 12.99120000, 77.72320000),
    ("Ramnaresh Soudri", 12.91310700, 77.63663400),
    ("M Sudhakar Rao", 12.92397862, 77.64819119),
]

print(f"📍 User location: ({user_lat}, {user_lon}) - Koramangala")
print()

for name, doc_lat, doc_lon in doctors:
    distance = calculate_distance(user_lat, user_lon, doc_lat, doc_lon)
    print(f"👨‍⚕️ {name}")
    print(f"   📍 Doctor location: ({doc_lat}, {doc_lon})")
    print(f"   📏 Distance: {distance:.2f} km")
    print()

# Test with some known distances in Bangalore
print("🗺️ Known Distance Tests:")
print("-" * 30)

# Distance from Koramangala to Whitefield (should be ~15-20 km)
distance = calculate_distance(12.9352, 77.6245, 12.9698, 77.7500)
print(f"Koramangala to Whitefield: {distance:.2f} km (expected: ~15-20 km)")

# Distance from Koramangala to Electronic City (should be ~12-15 km)
distance = calculate_distance(12.9352, 77.6245, 12.8456, 77.6603)
print(f"Koramangala to Electronic City: {distance:.2f} km (expected: ~12-15 km)")

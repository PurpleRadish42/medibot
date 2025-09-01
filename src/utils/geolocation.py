"""
Geolocation utilities for distance calculation between coordinates
"""
import math
from typing import Tuple, Optional

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    specified in decimal degrees using the Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
        
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

def parse_coordinates(lat_str: str, lon_str: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse coordinate strings to float values.
    
    Args:
        lat_str: Latitude as string
        lon_str: Longitude as string
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if parsing fails
    """
    try:
        lat = float(lat_str)
        lon = float(lon_str)
        
        # Basic validation
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon
        else:
            return None, None
    except (ValueError, TypeError):
        return None, None

def get_city_coordinates(city: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Get approximate coordinates for major cities.
    This is a simple fallback - in production, you'd use a geocoding service.
    
    Args:
        city: City name
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if city not found
    """
    # Major Indian cities coordinates
    city_coords = {
        'delhi': (28.6139, 77.2090),
        'mumbai': (19.0760, 72.8777),
        'bangalore': (12.9716, 77.5946),
        'hyderabad': (17.3850, 78.4867),
        'ahmedabad': (23.0225, 72.5714),
        'chennai': (13.0827, 80.2707),
        'kolkata': (22.5726, 88.3639),
        'pune': (18.5204, 73.8567),
        'jaipur': (26.9124, 75.7873),
        'surat': (21.1702, 72.8311),
        'lucknow': (26.8467, 80.9462),
        'kanpur': (26.4499, 80.3319),
        'nagpur': (21.1458, 79.0882),
        'indore': (22.7196, 75.8577),
        'thane': (19.2183, 72.9781),
        'bhopal': (23.2599, 77.4126),
        'visakhapatnam': (17.6868, 83.2185),
        'pimpri': (18.6298, 73.7997),
        'patna': (25.5941, 85.1376),
        'vadodara': (22.3072, 73.1812),
        'ghaziabad': (28.6692, 77.4538),
        'ludhiana': (30.9010, 75.8573),
        'agra': (27.1767, 78.0081),
        'nashik': (19.9975, 73.7898),
        'faridabad': (28.4089, 77.3178),
        'meerut': (28.9845, 77.7064),
        'rajkot': (22.3039, 70.8022),
        'kalyan': (19.2437, 73.1355),
        'vasai': (19.4911, 72.8054),
        'varanasi': (25.3176, 82.9739),
        'srinagar': (34.0837, 74.7973),
        'aurangabad': (19.8762, 75.3433),
        'dhanbad': (23.7957, 86.4304),
        'amritsar': (31.6340, 74.8723),
        'navi mumbai': (19.0330, 73.0297),
        'allahabad': (25.4358, 81.8463),
        'ranchi': (23.3441, 85.3096),
        'howrah': (22.5958, 88.2636),
        'coimbatore': (11.0168, 76.9558),
        'jabalpur': (23.1815, 79.9864),
        'gwalior': (26.2183, 78.1828),
        'vijayawada': (16.5062, 80.6480),
        'jodhpur': (26.2389, 73.0243),
        'madurai': (9.9252, 78.1198),
        'raipur': (21.2514, 81.6296),
        'kota': (25.2138, 75.8648),
        'guwahati': (26.1445, 91.7362),
        'chandigarh': (30.7333, 76.7794),
        'solapur': (17.6599, 75.9064),
        'hubli': (15.3647, 75.1240),
        'tiruchirappalli': (10.7905, 78.7047),
        'bareilly': (28.3670, 79.4304),
        'mysore': (12.2958, 76.6394),
        'tiruppur': (11.1085, 77.3411),
        'gurgaon': (28.4595, 77.0266),
        'aligarh': (27.8974, 78.0880),
        'jalandhar': (31.3260, 75.5762),
        'bhubaneswar': (20.2961, 85.8245),
        'salem': (11.6643, 78.1460),
        'warangal': (17.9689, 79.5941),
        'mira': (19.2952, 72.8739),
        'thiruvananthapuram': (8.5241, 76.9366),
        'bhiwandi': (19.3002, 73.0635),
        'saharanpur': (29.9680, 77.5552),
        'guntur': (16.3067, 80.4365),
        'amravati': (20.9374, 77.7796),
        'bikaner': (28.0229, 73.3119),
        'noida': (28.5355, 77.3910),
        'jamshedpur': (22.8046, 86.2029),
        'bhilai nagar': (21.1938, 81.3509),
        'cuttack': (20.4625, 85.8830),
        'firozabad': (27.1592, 78.3957),
        'kochi': (9.9312, 76.2673),
        'bhavnagar': (21.7645, 72.1519),
        'dehradun': (30.3165, 78.0322),
        'durgapur': (23.5204, 87.3119),
        'asansol': (23.6739, 86.9524),
        'nanded': (19.1383, 77.2975),
        'kolhapur': (16.7050, 74.2433),
        'ajmer': (26.4499, 74.6399),
        'akola': (20.7002, 77.0082),
        'gulbarga': (17.3297, 76.8343),
        'jamnagar': (22.4707, 70.0577),
        'ujjain': (23.1765, 75.7885),
        'loni': (28.7489, 77.2953),
        'siliguri': (26.7271, 88.3953),
        'jhansi': (25.4484, 78.5685),
        'ulhasnagar': (19.2215, 73.1645),
        'nellore': (14.4426, 79.9865),
        'jammu': (32.7266, 74.8570),
        'sangli': (16.8524, 74.5815),
        'belgaum': (15.8497, 74.4977),
        'mangalore': (12.9141, 74.8560),
        'ambattur': (13.1143, 80.1548),
        'tirunelveli': (8.7139, 77.7567),
        'malegaon': (20.5579, 74.5287),
        'gaya': (24.7914, 85.0002),
        'jalgaon': (21.0077, 75.5626),
        'udaipur': (24.5854, 73.7125),
        'maheshtala': (22.4990, 88.2479)
    }
    
    city_lower = city.lower().strip()
    return city_coords.get(city_lower, (None, None))
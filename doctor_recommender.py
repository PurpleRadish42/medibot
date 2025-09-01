"""
Doctor recommendation system - FIXED for your exact CSV specialties
"""
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging
from markupsafe import Markup
import sys
import os

# Add src to path for geolocation utils
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from utils.geolocation import haversine_distance, get_city_coordinates, parse_coordinates
    GEOLOCATION_AVAILABLE = True
except ImportError:
    print("⚠ Geolocation utilities not available")
    GEOLOCATION_AVAILABLE = False

class DoctorRecommender:
    def __init__(self, csv_path: str = "cleaned_doctors_full.csv"):
        self.csv_path = csv_path
        self.doctors_df = None
        
        # EXACT MAPPING to your CSV specialties
        self.specialty_mapping = {
            # Map AI recommendations to your exact CSV specialties
            "ophthalmologist": "Ophthalmologist",
            "eye specialist": "Ophthalmologist", 
            "cardiologist": "Cardiologist",
            "dermatologist": "Dermatologist",
            "gastroenterologist": "Gastroenterologist",
            "gynecologist": "Gynecologist",
            "neurologist": "Neurologist",
            "orthopedist": "Orthopedist",
            "pediatrician": "Pediatrician",
            "psychiatrist": "Psychiatrist",
            "pulmonologist": "Pulmonologist",
            "rheumatologist": "Rheumatologist",
            "urologist": "Urologist",
            "general practitioner": "General Physician",
            "gp": "General Physician",
            "ent specialist": "ENT Specialist",
            "endocrinologist": "Endocrinologist",
            "nephrologist": "Nephrologist",
            "oncologist": "Oncologist",
            
            # Additional mappings
            "dentist": "Dentist",
            "chiropractor": "Chiropractor",
            "dietitian": "Dietitian/Nutritionist",
            "nutritionist": "Dietitian/Nutritionist",
            "infertility specialist": "Infertility Specialist",
            "neurosurgeon": "Neurosurgeon",
            "physiotherapist": "Physiotherapist",
            "radiologist": "Radiologist",
            "pathologist": "Pathologist",
            "anesthesiologist": "Anesthesiologist",
            "emergency medicine physician": "Emergency Medicine Physician",
            "geriatrician": "Geriatrician",
            "plastic surgeon": "Plastic Surgeon",
            "vascular surgeon": "Vascular Surgeon",
            "thoracic surgeon": "Thoracic Surgeon",
            "bariatric surgeon": "bariatric surgeon",
            "homeopath": "Homeopath",
            "ayurveda": "Ayurveda",
            "unani": "Unani",
            "sexologist": "Sexologist",
            "cosmetologist": "Cosmetologist"
        }
        
        self.load_doctors_data()
    
    def load_doctors_data(self):
        """Load and preprocess doctors data from CSV"""
        try:
            file_path = Path(self.csv_path)
            if not file_path.exists():
                print(f"❌ CSV file not found: {self.csv_path}")
                return False
            
            self.doctors_df = pd.read_csv(self.csv_path)
            print(f"📊 Loaded CSV with {len(self.doctors_df)} rows")
            
            # DON'T convert specialty to lowercase - keep original case
            self.doctors_df['speciality'] = self.doctors_df['speciality'].fillna('')
            self.doctors_df['name'] = self.doctors_df['name'].fillna('Unknown')
            self.doctors_df['city'] = self.doctors_df['city'].fillna('Unknown')
            self.doctors_df['consultation_fee'] = pd.to_numeric(self.doctors_df['consultation_fee'], errors='coerce')
            self.doctors_df['year_of_experience'] = pd.to_numeric(self.doctors_df['year_of_experience'], errors='coerce')
            self.doctors_df['dp_score'] = pd.to_numeric(self.doctors_df['dp_score'], errors='coerce')
            
            print(f"✅ Loaded {len(self.doctors_df)} doctors from CSV")
            print(f"📊 Unique specialties: {self.doctors_df['speciality'].nunique()}")
            
            # Show available specialties for debugging
            print("🔍 Available specialties in CSV:")
            unique_specialties = sorted(self.doctors_df['speciality'].unique())
            for specialty in unique_specialties:
                count = len(self.doctors_df[self.doctors_df['speciality'] == specialty])
                print(f"  • {specialty} ({count} doctors)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
    
    def find_specialty_match(self, recommended_specialist: str) -> str:
        """Find exact matching specialty in CSV - SIMPLIFIED"""
        recommended_lower = recommended_specialist.lower().strip()
        
        print(f"🔍 Looking for: '{recommended_specialist}'")
        
        # Direct mapping to exact CSV specialty
        if recommended_lower in self.specialty_mapping:
            exact_specialty = self.specialty_mapping[recommended_lower]
            print(f"✅ Found mapping: '{recommended_specialist}' → '{exact_specialty}'")
            return exact_specialty
        
        # Fallback: try partial matching
        available_specialties = self.doctors_df['speciality'].unique()
        for specialty in available_specialties:
            if recommended_lower in specialty.lower():
                print(f"✅ Found partial match: '{specialty}'")
                return specialty
        
        print(f"❌ No match found for '{recommended_specialist}'")
        return None
    
    def recommend_doctors(self, specialist_type: str, city: str = None, limit: int = 5) -> List[Dict]:
        """Recommend doctors based on specialist type - SIMPLIFIED"""
        if self.doctors_df is None:
            print("❌ No doctor data loaded")
            return []
        
        try:
            print(f"\n🏥 Searching for {specialist_type}" + (f" in {city}" if city else ""))
            
            # Find exact matching specialty
            exact_specialty = self.find_specialty_match(specialist_type)
            
            if not exact_specialty:
                print("❌ No matching specialty found")
                return []
            
            # Filter doctors by exact specialty match
            filtered_doctors = self.doctors_df[
                self.doctors_df['speciality'] == exact_specialty
            ].copy()
            
            print(f"🔍 Found {len(filtered_doctors)} {exact_specialty}s in database")
            
            # Filter by city if provided
            if city and len(filtered_doctors) > 0:
                city_filtered = filtered_doctors[
                    filtered_doctors['city'].str.contains(city, case=False, na=False)
                ]
                
                if len(city_filtered) > 0:
                    filtered_doctors = city_filtered
                    print(f"🏙️ Filtered to {len(filtered_doctors)} doctors in {city}")
                else:
                    print(f"⚠️ No {exact_specialty}s found in {city}, showing all locations")
            
            if len(filtered_doctors) == 0:
                print("❌ No doctors found after filtering")
                return []
            
            # Sort by score, experience, and fees
            # Fill NaN values for sorting
            filtered_doctors['dp_score'] = filtered_doctors['dp_score'].fillna(0)
            filtered_doctors['year_of_experience'] = filtered_doctors['year_of_experience'].fillna(0)
            filtered_doctors['consultation_fee'] = filtered_doctors['consultation_fee'].fillna(999999)
            
            # Sort: Best score first, most experience first, lowest fee first
            filtered_doctors = filtered_doctors.sort_values([
                'dp_score', 'year_of_experience', 'consultation_fee'
            ], ascending=[False, False, True])
            
            # Get top recommendations
            top_doctors = filtered_doctors.head(limit)
            print(f"👨‍⚕️ Returning top {len(top_doctors)} {exact_specialty}s")
            
            # Format recommendations
            recommendations = []
            for _, doctor in top_doctors.iterrows():
                # Only use dp_score as rating, skip problematic experience/fee data
                dp_score = doctor.get('dp_score', 0)
                
                recommendations.append({
                    'name': str(doctor['name']),
                    'specialty': str(doctor['speciality']),
                    'degree': str(doctor.get('degree', 'Not specified')),
                    'city': str(doctor['city']),
                    'location': str(doctor.get('location', 'Location not specified')),
                    'dp_score': f"{dp_score:.0f}" if pd.notna(dp_score) and dp_score > 0 else 'Not rated',
                    'profile_url': str(doctor.get('profile_url', '')),
                    'google_map_link': str(doctor.get('google_map_link', ''))
                })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in doctor recommendation: {e}")
            import traceback
            traceback.print_exc()
            return []

    def recommend_doctors_with_location(self, specialist_type: str, user_lat: float = None, 
                                       user_lon: float = None, city: str = None, 
                                       limit: int = 10, sort_by: str = 'distance') -> List[Dict]:
        """
        Recommend doctors based on specialist type with location-aware sorting.
        
        Args:
            specialist_type: Type of specialist to find
            user_lat: User's latitude 
            user_lon: User's longitude
            city: City filter (optional)
            limit: Maximum number of results
            sort_by: 'distance' or 'rating' for sorting preference
            
        Returns:
            List of doctor recommendations with distance information
        """
        if self.doctors_df is None:
            print("❌ No doctor data loaded")
            return []
        
        if not GEOLOCATION_AVAILABLE:
            print("⚠ Geolocation not available, falling back to basic recommendation")
            return self.recommend_doctors(specialist_type, city, limit)
        
        try:
            print(f"\n🏥 Location-aware search for {specialist_type}")
            if user_lat and user_lon:
                print(f"📍 User location: {user_lat:.4f}, {user_lon:.4f}")
            
            # Find exact matching specialty
            exact_specialty = self.find_specialty_match(specialist_type)
            
            if not exact_specialty:
                print("❌ No matching specialty found")
                return []
            
            # Filter doctors by exact specialty match
            filtered_doctors = self.doctors_df[
                self.doctors_df['speciality'] == exact_specialty
            ].copy()
            
            print(f"🔍 Found {len(filtered_doctors)} {exact_specialty}s in database")
            
            # Filter by city if provided
            if city and len(filtered_doctors) > 0:
                city_filtered = filtered_doctors[
                    filtered_doctors['city'].str.contains(city, case=False, na=False)
                ]
                
                if len(city_filtered) > 0:
                    filtered_doctors = city_filtered
                    print(f"🏙️ Filtered to {len(filtered_doctors)} doctors in {city}")
                else:
                    print(f"⚠️ No {exact_specialty}s found in {city}, showing all locations")
            
            if len(filtered_doctors) == 0:
                print("❌ No doctors found after filtering")
                return []
            
            # Calculate distances if user location provided
            if user_lat and user_lon:
                distances = []
                for _, doctor in filtered_doctors.iterrows():
                    doc_lat, doc_lon = get_city_coordinates(doctor['city'])
                    if doc_lat and doc_lon:
                        distance = haversine_distance(user_lat, user_lon, doc_lat, doc_lon)
                        distances.append(distance)
                    else:
                        distances.append(float('inf'))  # Unknown distance
                
                filtered_doctors['distance'] = distances
                print(f"📏 Calculated distances for {len(filtered_doctors)} doctors")
            else:
                filtered_doctors['distance'] = float('inf')
            
            # Prepare scores for sorting
            filtered_doctors['dp_score'] = filtered_doctors['dp_score'].fillna(0)
            
            # Sort based on preference
            if sort_by == 'distance' and user_lat and user_lon:
                # Sort by distance first, then by rating
                filtered_doctors = filtered_doctors.sort_values([
                    'distance', 'dp_score'
                ], ascending=[True, False])
                print(f"📊 Sorted by distance (closest first)")
            else:
                # Sort by rating first, then by distance
                filtered_doctors = filtered_doctors.sort_values([
                    'dp_score', 'distance'
                ], ascending=[False, True])
                print(f"📊 Sorted by rating (highest first)")
            
            # Get top recommendations
            top_doctors = filtered_doctors.head(limit)
            print(f"👨‍⚕️ Returning top {len(top_doctors)} {exact_specialty}s")
            
            # Format recommendations
            recommendations = []
            for _, doctor in top_doctors.iterrows():
                dp_score = doctor.get('dp_score', 0)
                distance = doctor.get('distance', float('inf'))
                
                # Format distance
                if distance == float('inf'):
                    distance_str = "Distance unknown"
                elif distance < 1:
                    distance_str = f"{distance*1000:.0f}m away"
                else:
                    distance_str = f"{distance:.1f}km away"
                
                recommendations.append({
                    'name': str(doctor['name']),
                    'specialty': str(doctor['speciality']),
                    'degree': str(doctor.get('degree', 'Not specified')),
                    'city': str(doctor['city']),
                    'location': str(doctor.get('location', 'Location not specified')),
                    'dp_score': f"{dp_score:.0f}" if pd.notna(dp_score) and dp_score > 0 else 'Not rated',
                    'rating': float(dp_score) if pd.notna(dp_score) else 0.0,
                    'distance': distance if distance != float('inf') else None,
                    'distance_str': distance_str,
                    'profile_url': str(doctor.get('profile_url', '')),
                    'google_map_link': str(doctor.get('google_map_link', ''))
                })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in recommend_doctors_with_location: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def format_doctor_recommendations(self, doctors: List[Dict], specialist_type: str) -> str:
        """Format doctor recommendations for chat response as HTML table"""
        if not doctors:
            return f"I recommend consulting a {specialist_type}. Unfortunately, I don't have specific doctor recommendations available in your area right now. Please consult your local healthcare directory or contact your nearest hospital."
        
        response = f"<p>Based on your symptoms, I recommend consulting a <strong>{specialist_type}</strong>. Here are {len(doctors)} qualified doctors I found:</p>\n\n"
        
        # Start the HTML table
        response += """
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-family: Arial, sans-serif; background: rgba(255, 255, 255, 0.9); border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; border-bottom: 2px solid #dee2e6;">
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">#</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Doctor Name</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Specialty</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Qualification</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Location</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">DP Score</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Profile</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Maps</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, doctor in enumerate(doctors, 1):
            # Handle profile URL
            profile_link = ""
            if doctor['profile_url'] and doctor['profile_url'] != 'nan':
                profile_link = f'<a href="{doctor["profile_url"]}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: bold;">View Profile</a>'
            else:
                profile_link = "Not available"
                
            # Handle Google Maps link
            maps_link = ""
            if doctor['google_map_link'] and doctor['google_map_link'] != 'nan':
                maps_link = f'<a href="{doctor["google_map_link"]}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: bold;">View Map</a>'
            else:
                maps_link = "Not available"
                
            # Add table row
            row_style = "background-color: #ffffff;" if i % 2 == 1 else "background-color: #f8f9fa;"
            response += f"""
                <tr style="{row_style}">
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center; font-weight: bold; color: #4facfe;">{i}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;"><strong>Dr. {doctor['name']}</strong></td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;">{doctor['specialty']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;">{doctor['degree']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;">{doctor['location']}, {doctor['city']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;"><strong style="color: #28a745;">{doctor['dp_score']}</strong></td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;">{profile_link}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;">{maps_link}</td>
                </tr>
            """
        
        # Close the table
        response += """
            </tbody>
        </table>
        """
        
        # Add important notes
        response += """
        <div style="margin-top: 20px; padding: 15px; background: linear-gradient(45deg, #e9ecef, #f8f9fa); border-radius: 8px; font-family: Arial, sans-serif; border-left: 4px solid #4facfe;">
            <h4 style="margin-top: 0; color: #495057; display: flex; align-items: center;"><i class="fas fa-clipboard-list" style="margin-right: 8px; color: #4facfe;"></i> Important Notes:</h4>
            <ul style="margin-bottom: 0; color: #6c757d; line-height: 1.6;">
                <li>Please verify doctor availability before visiting</li>
                <li>Consultation fees may have changed</li>
                <li>In case of emergency, visit the nearest hospital immediately</li>
                <li>This is for informational purposes only</li>
            </ul>
        </div>
        """
        
        return response


    def get_statistics(self) -> Dict:
        """Get statistics about the doctors database"""
        if self.doctors_df is None:
            return {}
        
        return {
            'total_doctors': len(self.doctors_df),
            'total_cities': self.doctors_df['city'].nunique(),
            'total_specialties': self.doctors_df['speciality'].nunique(),
            'avg_experience': float(self.doctors_df['year_of_experience'].mean()) if not self.doctors_df['year_of_experience'].isna().all() else 0,
            'avg_consultation_fee': float(self.doctors_df['consultation_fee'].mean()) if not self.doctors_df['consultation_fee'].isna().all() else 0,
            'top_cities': self.doctors_df['city'].value_counts().head(5).to_dict(),
            'top_specialties': self.doctors_df['speciality'].value_counts().head(10).to_dict()
        }

# Test the system
if __name__ == "__main__":
    print("🧪 TESTING OPHTHALMOLOGIST SEARCH")
    print("=" * 50)
    
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        # Test ophthalmologist search
        test_cases = [
            ("ophthalmologist", "Mumbai"),
            ("eye specialist", "Delhi"),
            ("cardiologist", "Bangalore"),
            ("general practitioner", None)
        ]
        
        for specialist, city in test_cases:
            print(f"\n🔍 Testing: {specialist}" + (f" in {city}" if city else ""))
            doctors = recommender.recommend_doctors(specialist, city, limit=3)
            
            if doctors:
                print(f"✅ Found {len(doctors)} doctors:")
                for i, doctor in enumerate(doctors, 1):
                    print(f"  {i}. Dr. {doctor['name']} - {doctor['specialty']} - {doctor['city']}")
            else:
                print(f"❌ No {specialist} found")
    else:
        print("❌ Failed to load doctors data")
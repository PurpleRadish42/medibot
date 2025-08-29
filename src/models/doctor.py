# src/models/doctor.py
"""
Doctor/Specialist model definitions
"""
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Specialist:
    """Model for a medical specialist"""
    name: str
    specialty: str
    description: str
    common_conditions: List[str]
    
# Define available specialists
SPECIALISTS = [
    Specialist(
        name="General Practitioner",
        specialty="GP",
        description="Primary care physician for general health concerns",
        common_conditions=["fever", "cold", "flu", "general checkup"]
    ),
    Specialist(
        name="Cardiologist",
        specialty="Cardiology",
        description="Heart and cardiovascular system specialist",
        common_conditions=["chest pain", "heart palpitations", "high blood pressure"]
    ),
    Specialist(
        name="Neurologist",
        specialty="Neurology",
        description="Brain and nervous system specialist",
        common_conditions=["headaches", "migraines", "seizures", "neuropathy"]
    ),
    Specialist(
        name="Orthopedist",
        specialty="Orthopedics",
        description="Bone, joint, and musculoskeletal specialist",
        common_conditions=["joint pain", "fractures", "sports injuries", "arthritis"]
    ),
    Specialist(
        name="Gastroenterologist",
        specialty="Gastroenterology",
        description="Digestive system specialist",
        common_conditions=["stomach pain", "acid reflux", "IBS", "constipation"]
    ),
    Specialist(
        name="Pulmonologist",
        specialty="Pulmonology",
        description="Lung and respiratory specialist",
        common_conditions=["breathing problems", "asthma", "chronic cough", "COPD"]
    ),
    Specialist(
        name="Endocrinologist",
        specialty="Endocrinology",
        description="Hormone and metabolic disorder specialist",
        common_conditions=["diabetes", "thyroid issues", "hormonal imbalances"]
    ),
    Specialist(
        name="Dermatologist",
        specialty="Dermatology",
        description="Skin, hair, and nail specialist",
        common_conditions=["skin rashes", "acne", "eczema", "psoriasis"]
    ),
    Specialist(
        name="ENT Specialist",
        specialty="Otolaryngology",
        description="Ear, nose, and throat specialist",
        common_conditions=["ear pain", "sinusitis", "throat pain", "hearing loss"]
    ),
    Specialist(
        name="Urologist",
        specialty="Urology",
        description="Urinary and male reproductive system specialist",
        common_conditions=["urinary issues", "kidney stones", "prostate problems"]
    ),
    Specialist(
        name="Gynecologist",
        specialty="Gynecology",
        description="Female reproductive system specialist",
        common_conditions=["menstrual issues", "pregnancy concerns", "pelvic pain"]
    ),
    Specialist(
        name="Psychiatrist",
        specialty="Psychiatry",
        description="Mental health specialist",
        common_conditions=["depression", "anxiety", "mood disorders", "sleep issues"]
    ),
    Specialist(
        name="Rheumatologist",
        specialty="Rheumatology",
        description="Autoimmune and joint disease specialist",
        common_conditions=["arthritis", "lupus", "fibromyalgia", "joint inflammation"]
    ),
    Specialist(
        name="Nephrologist",
        specialty="Nephrology",
        description="Kidney specialist",
        common_conditions=["kidney disease", "kidney failure", "dialysis needs"]
    ),
    Specialist(
        name="Ophthalmologist",
        specialty="Ophthalmology",
        description="Eye and vision specialist",
        common_conditions=["vision problems", "eye pain", "cataracts", "glaucoma"]
    )
]

def get_specialist_by_name(name: str) -> Optional[Specialist]:
    """Get specialist by name"""
    for specialist in SPECIALISTS:
        if specialist.name.lower() == name.lower() or specialist.specialty.lower() == name.lower():
            return specialist
    return None
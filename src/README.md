# Source Code (src/)

This directory contains the core application source code organized into specialized modules.

## Structure

- **ai/** - AI and machine learning modules
  - `medical_image_analyzer.py` - Analyzes medical images using OpenAI GPT-4 Vision
  - `enhanced_medical_analysis.py` - Advanced medical image processing
  - `fast_medical_ai.py` - Optimized AI analysis for quick responses

- **llm/** - Language model integration
  - `recommender.py` - LLM-powered doctor recommendation system

- **models/** - Data models and schemas
  - Database model definitions
  - Data validation classes

- **database/** - Database connection and query handlers
  - MySQL connections
  - MongoDB connections
  - Database utility functions

- **api/** - API endpoint definitions
  - RESTful API routes
  - Request/response handlers
  - API authentication

## Usage

Import modules from this directory using:
```python
from src.ai.medical_image_analyzer import MedicalImageAnalyzer
from src.llm.recommender import get_doctor_recommendations
```

## Dependencies

All modules require the packages specified in `requirements.txt` at the root level.

"""
Simple Flask app for testing the Skin Analyzer without database dependencies
"""
import sys
import os
from pathlib import Path
from functools import wraps

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables.")

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'test-secret-key'

# Mock login required decorator for testing
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Mock user for testing
        request.user = {'id': 'test_user', 'username': 'test'}
        return f(*args, **kwargs)
    return decorated_function

# Basic routes for testing
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/skin-analyzer')
@login_required
def skin_analyzer():
    """Skin condition analyzer page"""
    return render_template('skin_analyzer.html')

@app.route('/api/v1/analyze-skin', methods=['POST'])
@login_required
def api_analyze_skin():
    """API endpoint for skin condition analysis"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No image file selected'
            }), 400
        
        # Read image data
        image_data = image_file.read()
        
        # Get user city from form data if provided
        user_city = request.form.get('city', None)
        
        print(f"🔬 Analyzing skin image for user {request.user['id']}")
        print(f"   Image size: {len(image_data)} bytes")
        print(f"   User city: {user_city}")
        
        # Import and use skin analyzer
        try:
            from src.ai.skin_analyzer import analyze_skin_image
            result = analyze_skin_image(image_data, user_city)
            
            if result['success']:
                print(f"✅ Skin analysis completed successfully")
                print(f"   Found {len(result['analysis']['conditions'])} potential conditions")
                print(f"   Recommended specialist: {result['analysis']['specialist_type']}")
                print(f"   Found {len(result['analysis']['doctors'])} doctors")
                
                return jsonify(result)
            else:
                print(f"❌ Skin analysis failed: {result.get('error', 'Unknown error')}")
                return jsonify(result), 400
                
        except ImportError as e:
            print(f"❌ Skin analyzer import error: {e}")
            return jsonify({
                'success': False,
                'message': 'Skin analyzer not available'
            }), 500
        except Exception as e:
            print(f"❌ Skin analysis error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }), 500
    
    except Exception as e:
        print(f"❌ API Error in /api/v1/analyze-skin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/chat')
@login_required
def chat():
    """Mock chat page"""
    return "<h1>Chat Page</h1><p><a href='/skin-analyzer'>Go to Skin Analyzer</a></p>"

if __name__ == '__main__':
    print("=" * 70)
    print("🧪 TESTING SKIN ANALYZER - SIMPLIFIED VERSION")
    print("=" * 70)
    print("🌐 Access URLs:")
    print("  📱 Main app: http://localhost:5000")
    print("  🔬 Skin Analyzer: http://localhost:5000/skin-analyzer")
    print("=" * 70)
    
    app.run(debug=True, port=5000, use_reloader=False)
# Static Assets

This directory contains all static files served by the Flask application.

## Contents

Typical structure includes:

- **css/** - Stylesheets
  - Application styles
  - Component-specific styles
  - Responsive design rules

- **js/** - JavaScript files
  - Client-side functionality
  - AJAX calls
  - UI interactions

- **images/** - Image assets
  - Logos
  - Icons
  - Background images

- **uploads/** - User uploaded files (if applicable)
  - Medical images
  - Profile pictures

## Access

Static files are served at the `/static/` URL path:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
```

## Note

User uploaded files should be handled securely and validated before storage.

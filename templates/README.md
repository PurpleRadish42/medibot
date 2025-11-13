# Templates

This directory contains all HTML templates for the MediBot web application.

## Files

- `index.html` - Homepage and landing page
- `login.html` - User login interface
- `register.html` - New user registration form
- `dashboard.html` - Main user dashboard
- `chat.html` - AI chatbot conversation interface
- `medical_image_analyzer.html` - Medical image upload and analysis interface

## Template Engine

Templates use Jinja2 template engine with Flask. Common patterns:

```html
<!-- Variable rendering -->
{{ variable_name }}

<!-- Control structures -->
{% if condition %}
    ...
{% endif %}

{% for item in items %}
    ...
{% endfor %}

<!-- Template inheritance -->
{% extends "base.html" %}
{% block content %}
    ...
{% endblock %}
```

## Styling

All templates reference CSS files from the `static/` directory.

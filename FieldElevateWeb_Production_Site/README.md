# FieldElevate Web Application

A comprehensive field management solution built with Flask, featuring performance optimizations and modern web practices.

*Last updated: March 19, 2024*

## Features

- **Dashboard Views**
  - Home page with overview
  - Admin dashboard for field management
  - Investor view for portfolio tracking
- **Performance Optimizations**
  - Response caching
  - Static file optimization
  - Lazy loading
  - Resource preloading
- **Monitoring & Reliability**
  - Health check endpoints
  - Performance monitoring
  - Error tracking
  - Memory usage monitoring

## Tech Stack

- **Backend**: Python 3.9.18, Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Dependencies**:
  - Flask-SQLAlchemy
  - Flask-Login
  - Flask-WTF
  - Pandas
  - Plotly
  - Gunicorn
  - Whitenoise

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/dogefield/df1.git
   cd FieldElevateWeb_Production_Site
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   # Development
   python main_app.py

   # Production
   gunicorn --bind 0.0.0.0:$PORT main_app:app
   ```

## Project Structure

```
FieldElevateWeb_Production_Site/
├── main_app.py           # Main application file
├── requirements.txt      # Python dependencies
├── Procfile             # Process file for deployment
├── runtime.txt          # Python runtime version
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── main.js      # Custom JavaScript
└── templates/           # HTML templates
    ├── index.html       # Home page
    ├── admin.html       # Admin dashboard
    └── investor_view.html # Investor dashboard
```

## Performance Features

- **Server-side Caching**
  - Route response caching
  - Static file caching
  - Memory usage monitoring

- **Client-side Optimizations**
  - Resource preloading
  - Lazy loading for images
  - Deferred JavaScript loading
  - Local storage caching

## Deployment

The application is configured for deployment on Render with the following settings:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 --keep-alive 5 --log-level info main_app:app`

## Monitoring

- Health check endpoint: `/health`
- Returns detailed status including:
  - Cache size and health
  - Memory usage
  - Timestamp
  - Error states

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Support

For support, please contact the development team or create an issue in the repository.

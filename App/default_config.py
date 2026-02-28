import os

# Flask default configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
ENV = os.getenv('FLASK_ENV', 'development')

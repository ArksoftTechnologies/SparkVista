import os

# Define basedir for use in SQLALCHEMY_DATABASE_URI
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string-for-dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt-key'
    
    # Email Config
    MAIL_SERVER = 'arksofttechnologies.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'info@arksofttechnologies.com'
    MAIL_PASSWORD = 'F?*jyD9(LYk7' # User provided this placeholder, ideally env var
    MAIL_SUBJECT_PREFIX = '[Spark Laundry]'
    
    # Premium branding colors (accessible via config if needed globally)
    BRAND_PRIMARY = "#4F46E5" # Indigo 600
    BRAND_SECONDARY = "#10B981" # Emerald 500

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.getcwd()), 'laundry_dev.db')

class ProductionConfig(Config):
    DEBUG = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        uri = os.environ.get('DATABASE_URL')
        if uri and uri.startswith('postgres://'):
            uri = uri.replace('postgres://', 'postgresql://', 1)
        return uri
        
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

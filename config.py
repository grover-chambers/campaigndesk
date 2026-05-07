import os
from dotenv import load_dotenv
load_dotenv()

def get_database_url():
    url = os.environ.get('DATABASE_URL', '')
    if not url:
        # Local fallback only
        return 'sqlite:////home/brayo/campaigndesk/campaigndesk.db'
    # Railway gives postgres:// — SQLAlchemy needs postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url

class Config:
    SECRET_KEY                     = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI        = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_CLOUD_NAME          = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY             = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET          = os.environ.get('CLOUDINARY_API_SECRET')
    CLOUDINARY_UPLOAD_PRESET       = os.environ.get('CLOUDINARY_UPLOAD_PRESET', 'campaigndesk_unsigned')
    WHATSAPP_BRIDGE_URL            = os.environ.get('WHATSAPP_BRIDGE_URL', 'http://127.0.0.1:3001')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:////home/brayo/campaigndesk/campaigndesk.db'
    )

class ProductionConfig(Config):
    DEBUG = False
    # Force DATABASE_URL — no SQLite fallback in production
    SQLALCHEMY_DATABASE_URI = get_database_url()

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     ProductionConfig,
}

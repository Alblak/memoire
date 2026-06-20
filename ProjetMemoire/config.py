"""
Fichier de configuration central du système
Contient tous les paramètres, clés API, seuils et constantes
"""

import os
from datetime import timedelta

class Config:
    """Configuration principale de l'application"""
    
    # ==================== CONFIGURATION BASE DE DONNÉES ====================
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'uac_thesis_manager')
    
    # ==================== CONFIGURATION APPLICATION FLASK ====================
    SECRET_KEY = os.environ.get('SECRET_KEY', 'votre_cle_secrete_tres_securisee_uaac_2024')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # ==================== CONFIGURATION UPLOAD FICHIERS ====================
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
    
    UPLOAD_SUBFOLDERS = {
        'concepts': 'concepts/',
        'travaux': 'travaux/',
        'final': 'final/',
        'rapports': 'rapports/',
        'temp': 'temp/'
    }
    
    # ==================== SEUILS ACADÉMIQUES ====================
    SEUIL_SIMILARITE = int(os.environ.get('SEUIL_SIMILARITE', 20))
    SEUIL_GENAI = float(os.environ.get('SEUIL_GENAI', 0.6))
    DELAI_SOUMISSION_CHAPITRE = int(os.environ.get('DELAI_SOUMISSION_CHAPITRE', 14))
    DELAI_CORRECTION_DIRECTEUR = int(os.environ.get('DELAI_CORRECTION_DIRECTEUR', 7))
    DELAI_SOUTENANCE_MAX = int(os.environ.get('DELAI_SOUTENANCE_MAX', 90))
    
    # ==================== CONFIGURATION APIs EXTERNES ====================
    COPYLEAKS_EMAIL = os.environ.get('COPYLEAKS_EMAIL', '')
    COPYLEAKS_API_KEY = os.environ.get('COPYLEAKS_API_KEY', '')
    COPYLEAKS_ENABLED = bool(COPYLEAKS_EMAIL and COPYLEAKS_API_KEY)
    
    TURNITIN_API_KEY = os.environ.get('TURNITIN_API_KEY', '')
    TURNITIN_API_SECRET = os.environ.get('TURNITIN_API_SECRET', '')
    TURNITIN_ENABLED = bool(TURNITIN_API_KEY and TURNITIN_API_SECRET)
    
    PLAGSCAN_API_KEY = os.environ.get('PLAGSCAN_API_KEY', '')
    PLAGSCAN_ENABLED = bool(PLAGSCAN_API_KEY)
    
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
    GOOGLE_CX = os.environ.get('GOOGLE_CX', '')
    GOOGLE_SEARCH_ENABLED = bool(GOOGLE_API_KEY and GOOGLE_CX)
    
    # Activer/désactiver toutes les APIs externes (ajouté)
    USE_EXTERNAL_APIS = True  # <-- AJOUTEZ CETTE LIGNE
    
    # ==================== CONFIGURATION EMAIL ====================
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'notifications@uaconline.edu.cd')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    
    # ==================== CONFIGURATION SMS (Twilio) ====================
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
    SMS_ENABLED = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)
    
    # ==================== CONFIGURATION MACHINE LEARNING ====================
    ML_MODELS_PATH = 'models/'
    BERT_MODEL_NAME = 'roberta-base-openai-detector'
    GPT2_MODEL_NAME = 'gpt2'
    USE_GPU = False
    
    # ==================== CONFIGURATION RAPPORTS ====================
    RAPPORT_DIR = 'rapports_similarite/'
    RAPPORT_FORMAT = 'pdf'
    RAPPORT_INCLUDE_SOURCES = True
    RAPPORT_INCLUDE_GRAPHS = True
    
    # ==================== CONFIGURATION CACHING ====================
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 1000
    
    # ==================== CONFIGURATION LOGGING ====================
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    LOG_MAX_BYTES = 10485760
    LOG_BACKUP_COUNT = 10
    
    # ==================== CONFIGURATION SÉCURITÉ ====================
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # ==================== CONFIGURATION PERFORMANCE ====================
    ASYNC_ENABLED = True
    ASYNC_WORKERS = 4
    BATCH_SIZE = 100
    
    # ==================== CONFIGURATION INTERFACE ====================
    ITEMS_PER_PAGE = 20
    DASHBOARD_REFRESH_INTERVAL = 30
    THEME = 'light'


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    RATELIMIT_ENABLED = False
    USE_EXTERNAL_APIS = False  # Désactiver APIs en dev


class TestingConfig(Config):
    """Configuration pour les tests unitaires"""
    DEBUG = False
    TESTING = True
    MYSQL_DB = 'uac_thesis_manager_test'
    RATELIMIT_ENABLED = False
    LOG_LEVEL = 'ERROR'
    USE_EXTERNAL_APIS = False


class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    RATELIMIT_ENABLED = True
    USE_EXTERNAL_APIS = True  # Activer APIs en prod
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# Sélection de la configuration selon l'environnement
ENV = os.environ.get('FLASK_ENV', 'development')
if ENV == 'production':
    config = ProductionConfig()
elif ENV == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()
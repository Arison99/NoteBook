"""
Configuration management for NoteBook backend
Handles environment variables and application settings
"""

import os
from pathlib import Path
from typing import Optional

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # CouchDB settings
    COUCHDB_URL = os.getenv('COUCHDB_URL', 'http://localhost:5984/')
    COUCHDB_USER = os.getenv('COUCHDB_USER', 'admin')
    COUCHDB_PASSWORD = os.getenv('COUCHDB_PASSWORD', 'password')
    
    # Replication settings
    REPLICATION_NODES = os.getenv('REPLICATION_NODES', '').split(',')
    REPLICATION_USER = os.getenv('REPLICATION_USER', COUCHDB_USER)
    REPLICATION_PASSWORD = os.getenv('REPLICATION_PASSWORD', COUCHDB_PASSWORD)
    CONTINUOUS_REPLICATION = os.getenv('CONTINUOUS_REPLICATION', 'true').lower() == 'true'
    REPLICATION_FILTER = os.getenv('REPLICATION_FILTER', '')
    REPLICATION_RETRY_SECONDS = int(os.getenv('REPLICATION_RETRY_SECONDS', '30'))
    
    # Security settings
    ENCRYPTION_KEY_PATH = os.getenv('ENCRYPTION_KEY_PATH', 'config/encryption.key')
    KEY_STORE_PATH = os.getenv('KEY_STORE_PATH', 'config/key_store.json')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get CouchDB configuration"""
        return {
            'url': cls.COUCHDB_URL,
            'username': cls.COUCHDB_USER,
            'password': cls.COUCHDB_PASSWORD
        }
    
    @classmethod
    def get_replication_config(cls) -> dict:
        """Get replication configuration"""
        return {
            'nodes': [node.strip() for node in cls.REPLICATION_NODES if node.strip()],
            'username': cls.REPLICATION_USER,
            'password': cls.REPLICATION_PASSWORD,
            'continuous': cls.CONTINUOUS_REPLICATION,
            'filter': cls.REPLICATION_FILTER,
            'retry_seconds': cls.REPLICATION_RETRY_SECONDS
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Override with more secure defaults for production
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    
    @classmethod
    def validate(cls):
        """Validate production configuration"""
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    FLASK_ENV = 'testing'
    
    # Use test database settings
    COUCHDB_URL = os.getenv('TEST_COUCHDB_URL', 'http://test-couchdb:5984/')
    COUCHDB_USER = os.getenv('TEST_COUCHDB_USER', 'test_admin')
    COUCHDB_PASSWORD = os.getenv('TEST_COUCHDB_PASSWORD', 'test_password123')


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env: Optional[str] = None) -> Config:
    """Get configuration based on environment"""
    env = env or os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])
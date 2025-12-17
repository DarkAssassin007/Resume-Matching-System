"""
Configuration file for Resume Matching System
"""

import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'resume_matching_secret_key_2024'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
    
    # Database configuration
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = int(os.environ.get('DB_PORT') or 5432)
    DB_NAME = os.environ.get('DB_NAME') or 'resume_matching'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'postgres'
    
    # Spark configuration
    SPARK_UI_PORT = int(os.environ.get('SPARK_UI_PORT') or 4040)
    SPARK_DRIVER_MEMORY = os.environ.get('SPARK_DRIVER_MEMORY') or '2g'
    SPARK_SHUFFLE_PARTITIONS = int(os.environ.get('SPARK_SHUFFLE_PARTITIONS') or 4)
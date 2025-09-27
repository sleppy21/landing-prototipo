"""
Configuración centralizada para el Bot Asistente de Consultas
"""
import os
from pathlib import Path
from typing import Dict, Any

# Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

class Config:
    """Configuración base"""
    
    # Configuración del servidor
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
    
    # Configuración de archivos
    DATA_FILE = os.environ.get("DATA_FILE", str(DATA_DIR / "catalogue.json"))
    CONTEXT_DIR = os.environ.get("CONTEXT_DIR", str(DATA_DIR / "context"))
    
    # Configuración del modelo de IA
    MODEL_ID = os.environ.get("MODEL_ID", "google/flan-t5-small")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Configuración de cache y rate limiting
    CACHE_TTL = int(os.environ.get("CACHE_TTL", 300))  # segundos
    REQUESTS_PER_MINUTE = int(os.environ.get("REQUESTS_PER_MINUTE", 40))
    MAX_PROCESSING_TIME = int(os.environ.get("MAX_PROCESSING_TIME", 30))  # segundos
    
    # Configuración de base de datos vectorial
    CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", str(BASE_DIR / "chroma_db"))
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    # Configuración de seguridad
    REBUILD_SECRET = os.environ.get("REBUILD_SECRET", "")
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Retorna todas las configuraciones como diccionario"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    REQUESTS_PER_MINUTE = 60

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    DATA_FILE = str(BASE_DIR / "tests" / "test_data.json")

# Configuración por defecto
config = DevelopmentConfig()

# Seleccionar configuración según entorno
ENV = os.environ.get("FLASK_ENV", "development")
if ENV == "production":
    config = ProductionConfig()
elif ENV == "testing":
    config = TestingConfig()
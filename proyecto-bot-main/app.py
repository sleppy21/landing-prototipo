#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py
Nueva aplicación principal del Bot Asistente de Tienda
Versión modular y optimizada con sistema de configuración, logging y analytics avanzados
"""

import os
import sys
import time
import atexit
import signal
from pathlib import Path
from typing import Dict, Any

# Agregar directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Imports de módulos propios
from core.config import config
from core.logger import setup_logging
from core.analytics import AnalyticsEngine
from src.api.chat_routes import chat_bp
from src.services.cache_service import CacheService
from src.services.rate_limit_service import RateLimitService
from src.core.chat_engine import ChatEngine

class BotApplication:
    """Clase principal de la aplicación del bot"""

    def __init__(self):
        self.config = config
        self.logger_system = None
        self.analytics = None
        self.cache_service = None
        self.rate_limit_service = None
        self.chat_engine = None
        self.app = None

    def initialize(self):
        """Inicializa todos los componentes de la aplicación"""
        print("🤖 Inicializando Fashion Store Assistant...")

        # 1. Configurar logging
        self.logger_system = setup_logging(self.config)
        self.logger = self.logger_system.get_logger(__name__)
 self.logger.info("Sistema de logging inicializado")

 # 2. Inicializar analytics
 self.analytics = AnalyticsEngine(self.config)
 self.logger.info("Sistema de analytics inicializado")

 # 3. Crear aplicación Flask
 self.app = Flask(__name__)
 self.app.config.update({
 'JSON_AS_ASCII': False,
 'MAX_CONTENT_LENGTH': 16 * 1024 * 1024, # 16MB max
 'SECRET_KEY': os.urandom(24)
 })

 # 4. Configurar CORS
 CORS(self.app, origins=self.config.security.cors_origins)

 # 5. Inicializar servicios
 self.cache_service = CacheService(self.config.cache)
 self.rate_limit_service = RateLimitService(self.config.rate_limit)

 # 6. Inicializar motor de chat (sin parámetros, usa config.settings)
 self.chat_engine = ChatEngine()

 # 7. Registrar blueprints y rutas
 self._register_routes()

 # 8. Configurar handlers de cierre
 self._setup_shutdown_handlers()

 self.logger.info(" Aplicación inicializada correctamente")
 self._print_startup_summary()

 def _register_routes(self):
 """Registra todas las rutas de la aplicación"""

 # Registrar blueprint del chat
 self.app.register_blueprint(chat_bp)

 # Rutas principales
 @self.app.route('/')
 def index():
 """Página principal del chat"""
 return render_template('index.html')

 @self.app.route('/health')
 def health():
 """Endpoint de health check"""
 try:
 stats = self.analytics.get_realtime_stats() if self.analytics else {}
 return jsonify({
 "status": "healthy",
 "version": "2.0.0",
 "uptime": time.time() - self._start_time,
 "config_summary": self.config.get_summary(),
 "stats": stats
 }), 200
 except Exception as e:
 self.logger.error(f"Health check failed: {e}")
 return jsonify({
 "status": "unhealthy",
 "error": str(e)
 }), 500

 @self.app.route('/api/v1/analytics/dashboard')
 def analytics_dashboard():
 """Endpoint para dashboard de analytics"""
 if not self.analytics or not self.analytics.enabled:
 return jsonify({"error": "Analytics disabled"}), 404

 try:
 return jsonify({
 "realtime_stats": self.analytics.get_realtime_stats(),
 "popular_questions": self.analytics.get_popular_questions(15),
 "error_analysis": self.analytics.get_error_analysis(),
 "session_analysis": self.analytics.get_session_analysis(),
 "usage_trends": self.analytics.get_usage_trends(24)
 }), 200
 except Exception as e:
 self.logger.error(f"Analytics dashboard error: {e}")
 return jsonify({"error": "Analytics error"}), 500

 @self.app.route('/api/v1/system/info')
 def system_info():
 """Información del sistema"""
 return jsonify({
 "config": self.config.get_summary(),
 "services": {
 "cache": self.cache_service.get_stats() if self.cache_service else None,
 "rate_limit": self.rate_limit_service.get_stats() if self.rate_limit_service else None,
 "chat_engine": self.chat_engine.get_health_status() if self.chat_engine else None
 },
 "logging": self.logger_system.get_log_stats() if self.logger_system else None
 }), 200

 # Handlers de error globales
 @self.app.errorhandler(404)
 def not_found(error):
 return jsonify({
 "error": "Recurso no encontrado",
 "message": "La página o endpoint solicitado no existe"
 }), 404

 @self.app.errorhandler(500)
 def internal_error(error):
 self.logger.error(f"Internal server error: {error}")
 return jsonify({
 "error": "Error interno del servidor",
 "message": "Ha ocurrido un error interno. Por favor, intenta de nuevo."
 }), 500

 @self.app.errorhandler(429)
 def rate_limit_error(error):
 return jsonify({
 "error": "Demasiadas solicitudes",
 "message": "Has excedido el límite de solicitudes. Intenta de nuevo más tarde."
 }), 429

 # Middleware para logging de requests
 @self.app.before_request
 def log_request_info():
 if request.endpoint not in ['health', 'static']:
 self.logger.debug(f"Request: {request.method} {request.url} from {request.remote_addr}")

 @self.app.after_request
 def log_response_info(response):
 if request.endpoint not in ['health', 'static']:
 self.logger.debug(f"Response: {response.status_code} for {request.method} {request.url}")
 return response

 def _setup_shutdown_handlers(self):
 """Configura handlers para cierre limpio de la aplicación"""
 self._start_time = time.time()

 def shutdown_handler(signum=None, frame=None):
 self.logger.info(" Iniciando cierre de la aplicación...")

 try:
 # Guardar analytics
 if self.analytics and self.analytics.enabled:
 export_file = self.analytics.export_data()
 self.logger.info(f"Analytics exportados a: {export_file}")

 # Limpiar cache
 if self.cache_service:
 self.cache_service.cleanup()

 # Limpiar logs antiguos
 if self.logger_system:
 self.logger_system.cleanup_old_logs()

 self.logger.info(" Cierre limpio completado")

 except Exception as e:
 print(f"Error durante cierre: {e}")

 sys.exit(0)

 # Registrar handlers
 atexit.register(shutdown_handler)
 signal.signal(signal.SIGINT, shutdown_handler)
 signal.signal(signal.SIGTERM, shutdown_handler)

 def _print_startup_summary(self):
 """Imprime resumen de inicio"""
 summary = f"""
╔══════════════════════════════════════════════════════════════╗
║ Fashion Store Assistant v2.0 ║
╠══════════════════════════════════════════════════════════════╣
║ Servidor: {self.config.server.host}:{self.config.server.port:<10} Debug: {str(self.config.server.debug):<6} ║
║ Modelo: {self.config.model.model_id:<20} ║
║ Cache: TTL {self.config.cache.ttl_seconds}s, Max {self.config.cache.max_entries:<6} entradas ║
║ Rate Limit: {self.config.rate_limit.requests_per_minute:<3} requests/minuto ║
║ Logging: Nivel {self.config.logging.level:<5} -> {self.config.logging.log_dir:<15} ║
║ Features: {', '.join(self.config.get_summary()['features_enabled']):<35} ║
╠══════════════════════════════════════════════════════════════╣
║ URLs: ║
║ Chat: http://{self.config.server.host}:{self.config.server.port}/ ║
║ Health: http://{self.config.server.host}:{self.config.server.port}/health ║
║ Analytics: http://{self.config.server.host}:{self.config.server.port}/api/v1/analytics/dashboard ║
║ API Docs: http://{self.config.server.host}:{self.config.server.port}/api/v1/ ║
╚══════════════════════════════════════════════════════════════╝
 """
 print(summary)

 def run(self):
 """Ejecuta la aplicación"""
 if not self.app:
 raise RuntimeError("Aplicación no inicializada. Llamar initialize() primero.")

 try:
 self.app.run(
 host=self.config.server.host,
 port=self.config.server.port,
 debug=self.config.server.debug,
 threaded=self.config.server.threaded,
 use_reloader=False # Evitar problemas con hot reload
 )
 except Exception as e:
 self.logger.error(f"Error ejecutando aplicación: {e}")
 raise

# Función principal
def main():
 """Función principal de la aplicación"""
 try:
 # Crear y inicializar aplicación
 app = BotApplication()
 app.initialize()

 # Ejecutar aplicación
 app.run()

 except KeyboardInterrupt:
 print("\n Aplicación interrumpida por el usuario")
 except Exception as e:
 print(f" Error fatal: {e}")
 sys.exit(1)

if __name__ == "__main__":
 main()
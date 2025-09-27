"""
Endpoints REST para el chat del Bot Asistente de Consultas
"""
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

from src.models.schemas import ChatMessage, ChatResponse
from src.services.cache_service import cache_service
from src.services.rate_limit_service import rate_limit_service
from src.services.processing_service import processing_lock_service
from src.core.chat_engine import ChatEngine

logger = logging.getLogger(__name__)

# Blueprint para las rutas del chat
chat_bp = Blueprint('chat', __name__, url_prefix='/api/v1/chat')

# Instancia del motor de chat
chat_engine = ChatEngine()

@chat_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Endpoint principal para hacer preguntas al bot
    
    Body:
        {
            "question": "string"
        }
    
    Returns:
        {
            "answer": "string",
            "confidence": float,
            "processing": bool,
            "error": "string" (opcional)
        }
    """
    try:
        # Obtener IP del cliente
        client_ip = request.remote_addr or "unknown"
        
        # Verificar rate limiting
        allowed, rate_info = rate_limit_service.is_allowed(client_ip)
        if not allowed:
            logger.warning(f"Rate limit exceeded for client {client_ip}")
            return jsonify({
                "error": "Límite de solicitudes alcanzado. Intenta de nuevo en un minuto.",
                "rate_limit_info": rate_info
            }), 429
        
        # Validar datos de entrada
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "error": "No se recibió ninguna pregunta. ¿En qué puedo ayudarte? 🤔"
            }), 400
        
        try:
            # Validar usando Pydantic
            chat_message = ChatMessage(**data)
            question = chat_message.question
        except Exception as e:
            return jsonify({
                "error": "Pregunta inválida. Por favor, proporciona una pregunta válida."
            }), 400
        
        # Verificar si el bot está procesando
        if processing_lock_service.is_bot_processing():
            logger.info(f"Request blocked - bot busy processing for client {client_ip}")
            return jsonify({
                "answer": "Estoy procesando tu consulta anterior, por favor espera un momento... ⏳",
                "processing": True,
                "rate_limit_info": rate_info
            }), 200
        
        # Intentar iniciar procesamiento
        if not processing_lock_service.start_processing(question):
            return jsonify({
                "answer": "Estoy ocupado en este momento, por favor intenta de nuevo en unos segundos... ⏳",
                "processing": True,
                "rate_limit_info": rate_info
            }), 200

        try:
            # Procesar la pregunta
            response = chat_engine.process_question(question, client_ip)
            
            # Agregar información de rate limiting
            response["rate_limit_info"] = rate_info
            
            logger.info(f"Question processed successfully for client {client_ip}")
            return jsonify(response), 200
            
        except Exception as e:
            logger.exception(f"Error processing question for client {client_ip}")
            return jsonify({
                "answer": "Disculpa la interrupción. Estoy teniendo algunas dificultades técnicas. ¿Podrías intentarlo de nuevo en un momento? 🔄",
                "error": "Internal processing error",
                "rate_limit_info": rate_info
            }), 500
        
        finally:
            # Siempre liberar el bloqueo
            processing_lock_service.finish_processing()
    
    except Exception as e:
        logger.exception("Unexpected error in ask_question endpoint")
        return jsonify({
            "error": "Error interno del servidor. Por favor, intenta de nuevo.",
            "details": str(e) if logger.level == logging.DEBUG else None
        }), 500

@chat_bp.route('/status', methods=['GET'])
def get_chat_status():
    """
    Endpoint para obtener el estado del chat
    
    Returns:
        {
            "processing_status": dict,
            "system_health": dict,
            "cache_stats": dict,
            "rate_limit_stats": dict
        }
    """
    try:
        return jsonify({
            "processing_status": processing_lock_service.get_current_status(),
            "system_health": chat_engine.get_health_status(),
            "cache_stats": cache_service.get_stats(),
            "rate_limit_stats": rate_limit_service.get_stats()
        }), 200
    
    except Exception as e:
        logger.exception("Error getting chat status")
        return jsonify({
            "error": "Error obteniendo estado del sistema",
            "details": str(e) if logger.level == logging.DEBUG else None
        }), 500

@chat_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """
    Endpoint para obtener sugerencias de preguntas
    
    Query Parameters:
        - query (opcional): Filtrar sugerencias por texto
        - limit (opcional): Número máximo de sugerencias (default: 5)
    
    Returns:
        {
            "suggestions": [
                {
                    "text": "string",
                    "category": "string",
                    "icon": "string"
                }
            ]
        }
    """
    try:
        query = request.args.get('query', '').strip()
        limit = min(int(request.args.get('limit', 5)), 10)  # Máximo 10
        
        suggestions = chat_engine.get_suggestions(query, limit)
        
        return jsonify({
            "suggestions": suggestions,
            "total": len(suggestions)
        }), 200
    
    except Exception as e:
        logger.exception("Error getting suggestions")
        return jsonify({
            "error": "Error obteniendo sugerencias",
            "suggestions": []
        }), 500

@chat_bp.route('/history', methods=['GET'])
def get_processing_history():
    """
    Endpoint para obtener el historial de procesamiento (para debugging)
    
    Query Parameters:
        - limit (opcional): Número máximo de entradas (default: 10)
    
    Returns:
        {
            "history": [
                {
                    "query": "string",
                    "duration": float,
                    "completed": bool,
                    "timestamp": float
                }
            ],
            "stats": dict
        }
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)  # Máximo 50
        
        history = processing_lock_service.get_processing_history()
        stats = processing_lock_service.get_stats()
        
        return jsonify({
            "history": history[-limit:] if history else [],
            "stats": stats,
            "total_entries": len(history)
        }), 200
    
    except Exception as e:
        logger.exception("Error getting processing history")
        return jsonify({
            "error": "Error obteniendo historial",
            "history": [],
            "stats": {}
        }), 500

@chat_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    Endpoint para obtener estadísticas detalladas del cache
    
    Returns:
        {
            "stats": dict,
            "sample_entries": list,
            "total_entries": int
        }
    """
    try:
        cache_info = cache_service.get_cache_info()
        return jsonify(cache_info), 200
    
    except Exception as e:
        logger.exception("Error getting cache stats")
        return jsonify({
            "error": "Error obteniendo estadísticas del cache",
            "stats": {}
        }), 500

@chat_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    Endpoint para limpiar el cache (requiere autenticación en producción)
    
    Returns:
        {
            "message": "string",
            "success": bool
        }
    """
    try:
        # En producción, aquí iría validación de token/autenticación
        cache_service.clear()
        
        logger.info("Cache cleared manually")
        return jsonify({
            "message": "Cache limpiado exitosamente",
            "success": True
        }), 200
    
    except Exception as e:
        logger.exception("Error clearing cache")
        return jsonify({
            "error": "Error limpiando cache",
            "success": False
        }), 500

# Manejo de errores para el blueprint
@chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado",
        "message": "El endpoint solicitado no existe"
    }), 404

@chat_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Método no permitido",
        "message": "El método HTTP no está permitido para este endpoint"
    }), 405

@chat_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Ha ocurrido un error interno. Por favor, intenta de nuevo."
    }), 500
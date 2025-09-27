#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py - Fashion Store Bot (Versión Simplificada)
Bot asistente integrado con landing Fashion Store
"""

import os
import sys
import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

# Configuración básica
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'fashion-store-secret-key-2024'

# Configurar CORS más permisivo para desarrollo
CORS(app, 
     origins=["*"],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Credentials'],
     supports_credentials=True)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

@app.route('/')
def index():
    """Página principal del chat"""
    return jsonify({
        "message": "Fashion Store Bot API",
        "version": "2.0.0",
        "endpoints": ["/health", "/api/chat", "/api/suggestions"],
        "status": "running"
    })

@app.route('/health')
def health():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "service": "Fashion Store Bot",
        "integration": "active",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Endpoint principal del chat"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Verificar si hay datos JSON
        if not request.is_json:
            return jsonify({
                "error": "Content-Type debe ser application/json",
                "response": "Por favor, envía los datos en formato JSON."
            }), 400
            
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No se recibieron datos",
                "response": "Por favor, envía un mensaje."
            }), 400
            
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                "error": "Mensaje vacío",
                "response": "Por favor, escribe una pregunta."
            }), 400
        
        # Respuestas predefinidas para demostración
        responses = {
            "hola": "¡Hola! Soy tu asistente virtual de Fashion Store. ¿En qué puedo ayudarte?",
            "productos": "Tenemos una amplia gama de productos: ropa para mujer, hombre, niños, accesorios y cosméticos.",
            "horarios": "Nuestros horarios son de 10:00 AM a 9:00 PM, de lunes a domingo.",
            "ubicacion": "Puedes encontrarnos en nuestras tiendas físicas o comprar online en nuestro sitio web.",
            "ofertas": "¡Tenemos ofertas increíbles! Descuentos de hasta 50% en artículos seleccionados.",
            "tallas": "Ofrecemos una guía completa de tallas para todos nuestros productos. ¿Necesitas ayuda con alguna prenda específica?",
            "envios": "Realizamos envíos gratuitos en compras mayores a $99. El tiempo de entrega estándar es de 3-5 días hábiles.",
            "cambios": "Aceptamos cambios y devoluciones dentro de 30 días de la compra, con etiquetas originales.",
            "contacto": "Puedes contactarnos por teléfono, email o chat en vivo. ¡Estamos aquí para ayudarte!"
        }
        
        # Buscar respuesta
        response = "Gracias por tu consulta. Soy un asistente virtual de Fashion Store. Puedo ayudarte con información sobre productos, horarios, ofertas, tallas, envíos y más. ¿Hay algo específico que te gustaría saber?"
        
        user_message_lower = user_message.lower()
        for keyword, answer in responses.items():
            if keyword in user_message_lower:
                response = answer
                break
        
        return jsonify({
            "response": response,
            "status": "success",
            "timestamp": datetime.datetime.now().isoformat(),
            "message_received": user_message
        }), 200
        
    except Exception as e:
        print(f"Error en chat endpoint: {e}")
        return jsonify({
            "error": "Error interno del servidor",
            "response": "Lo siento, ha ocurrido un error. Por favor, intenta de nuevo.",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    """Endpoint para sugerencias rápidas"""
    return jsonify({
        "suggestions": [
            "Ver ofertas del día",
            "¿Cómo hacer un cambio?",
            "Catálogo de temporada",
            "Guía de tallas",
            "Horarios de atención",
            "Información de envíos"
        ],
        "status": "success"
    })

@app.route('/api/v1/chat/suggestions', methods=['GET'])
def chat_suggestions():
    """Endpoint v1 para sugerencias del chat"""
    return suggestions()

@app.route('/api/v1/chat/ask', methods=['POST', 'OPTIONS'])
def chat_ask():
    """Endpoint v1 para preguntas del chat"""
    return chat()

# Servir archivos estáticos si existen
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Recurso no encontrado",
        "message": "La página solicitada no existe",
        "available_endpoints": ["/health", "/api/chat", "/api/suggestions"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Ha ocurrido un error interno"
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Método no permitido",
        "message": f"El método {request.method} no está permitido para esta ruta",
        "allowed_methods": ["GET", "POST", "OPTIONS"]
    }), 405

def main():
    """Función principal"""
    print("🤖 Fashion Store Bot - Versión Simplificada")
    print("🌐 Servidor iniciando...")
    print("✅ Bot listo para recibir consultas")
    
    # Configurar puerto 5001 específicamente para el launcher
    port = 5001
    
    print(f"🚀 Servidor corriendo en http://localhost:{port}")
    print("📝 Endpoints disponibles:")
    print("   - GET  /health")
    print("   - POST /api/chat")
    print("   - GET  /api/suggestions")
    print("   - POST /api/v1/chat/ask")
    print("   - GET  /api/v1/chat/suggestions")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,  # Desactivar debug para reducir logs
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Error iniciando el bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
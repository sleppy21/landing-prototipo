#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py - Fashion Store Bot (Versión Simplificada)
Bot asistente integrado con landing Fashion Store
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Configuración básica
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'fashion-store-secret-key-2024'

# Configurar CORS para permitir integración con el landing
CORS(app, origins=["http://localhost:8080", "http://localhost:3000", "http://127.0.0.1:8080", "http://[::]:8080", "*"])

@app.route('/')
def index():
    """Página principal del chat"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "service": "Fashion Store Bot",
        "integration": "active"
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat"""
    try:
        data = request.get_json()
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
            "timestamp": str(Path().resolve())
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Error interno del servidor",
            "response": "Lo siento, ha ocurrido un error. Por favor, intenta de nuevo.",
            "details": str(e)
        }), 500

@app.route('/api/suggestions')
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
        ]
    })

@app.route('/api/v1/chat/suggestions')
def chat_suggestions():
    """Endpoint v1 para sugerencias del chat"""
    return suggestions()

@app.route('/api/v1/chat/ask', methods=['POST'])
def chat_ask():
    """Endpoint v1 para preguntas del chat"""
    return chat()

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Recurso no encontrado",
        "message": "La página solicitada no existe"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Ha ocurrido un error interno"
    }), 500

def main():
    """Función principal"""
    print("Fashion Store Bot - Version Simplificada")
    print("Servidor iniciando...")
    print("Bot listo para recibir consultas")
    
    # Obtener puerto desde variable de entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"Error iniciando el bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot simplificado para Fashion Store
Versión mínima para pruebas rápidas
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*")

# Respuestas predefinidas para el bot
RESPUESTAS = {
    'saludo': [
        "¡Hola! Bienvenido a Fashion Store. ¿En qué puedo ayudarte?",
        "¡Hola! Soy tu asistente virtual. ¿Cómo puedo ayudarte hoy?",
        "¡Hola! ¿Buscas algo específico en nuestra tienda?"
    ],
    'ofertas': [
        "🏷️ ¡Tenemos ofertas increíbles! Hasta 50% de descuento en vestidos de verano.",
        "🏷️ ¡Ofertas del día! 30% de descuento en toda la colección de primavera.",
        "🏷️ ¡Super ofertas! 2x1 en accesorios seleccionados."
    ],
    'tallas': [
        "📏 Ofrecemos tallas desde XS hasta XXL. ¿Necesitas ayuda con alguna talla específica?",
        "📏 Tenemos una guía de tallas completa. ¿Para qué prenda necesitas información?",
        "📏 Nuestras tallas van desde XS hasta XXL. ¿En qué puedo ayudarte?"
    ],
    'envios': [
        "📦 Envíos gratis en compras mayores a $50. Entrega en 2-3 días hábiles.",
        "📦 Ofrecemos envío express (24h) y envío estándar (2-3 días).",
        "📦 Envíos a todo el país. ¿Necesitas información sobre tu zona?"
    ],
    'horarios': [
        "🕒 Horarios de atención: Lunes a Viernes 9:00-18:00, Sábados 10:00-16:00.",
        "🕒 Estamos disponibles L-V 9:00-18:00 y Sábados 10:00-16:00.",
        "🕒 Nuestros horarios: L-V 9:00-18:00, Sábados 10:00-16:00. Domingos cerrado."
    ],
    'productos': [
        "👗 Tenemos una amplia colección de vestidos, blusas, pantalones y accesorios.",
        "👗 Nuestra tienda ofrece ropa femenina de alta calidad y accesorios únicos.",
        "👗 Explora nuestra colección: vestidos elegantes, casual wear y accesorios fashion."
    ],
    'default': [
        "Gracias por tu pregunta. ¿Puedes ser más específico sobre lo que necesitas?",
        "Te ayudo con información sobre productos, ofertas, tallas, envíos y horarios. ¿Qué te interesa?",
        "Estoy aquí para ayudarte con cualquier duda sobre Fashion Store. ¿En qué puedo asistirte?"
    ]
}

def detectar_intencion(mensaje):
    """Detecta la intención del mensaje del usuario"""
    mensaje_lower = mensaje.lower()
    
    # Saludos
    if any(word in mensaje_lower for word in ['hola', 'buenos', 'buenas', 'saludos', 'hi', 'hello']):
        return 'saludo'
    
    # Ofertas
    if any(word in mensaje_lower for word in ['oferta', 'descuento', 'promocion', 'rebaja', 'precio']):
        return 'ofertas'
    
    # Tallas
    if any(word in mensaje_lower for word in ['talla', 'tamaño', 'medida', 'size']):
        return 'tallas'
    
    # Envíos
    if any(word in mensaje_lower for word in ['envio', 'entrega', 'shipping', 'delivery']):
        return 'envios'
    
    # Horarios
    if any(word in mensaje_lower for word in ['horario', 'hora', 'abierto', 'cerrado', 'atencion']):
        return 'horarios'
    
    # Productos
    if any(word in mensaje_lower for word in ['producto', 'vestido', 'blusa', 'pantalon', 'ropa', 'accesorio']):
        return 'productos'
    
    return 'default'

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'service': 'Fashion Store Bot Simple',
        'version': '1.0.0',
        'integration': 'active'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat"""
    try:
        data = request.get_json()
        mensaje = data.get('message', '').strip()
        
        if not mensaje:
            return jsonify({
                'response': 'Por favor, escribe un mensaje.',
                'status': 'error'
            }), 400
        
        # Detectar intención y generar respuesta
        intencion = detectar_intencion(mensaje)
        respuesta = random.choice(RESPUESTAS[intencion])
        
        logger.info(f"Usuario: {mensaje} | Intención: {intencion}")
        
        return jsonify({
            'response': respuesta,
            'status': 'success',
            'intent': intencion
        })
        
    except Exception as e:
        logger.error(f"Error en chat: {str(e)}")
        return jsonify({
            'response': 'Lo siento, ha ocurrido un error. Por favor, intenta de nuevo.',
            'status': 'error'
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Devuelve sugerencias rápidas"""
    return jsonify({
        'suggestions': [
            "Ver ofertas del día",
            "Guía de tallas",
            "Información de envíos",
            "Horarios de atención",
            "Ver productos nuevos"
        ]
    })

# Endpoints adicionales para compatibilidad
@app.route('/api/v1/chat/suggestions', methods=['GET'])
def get_suggestions_v1():
    return get_suggestions()

@app.route('/api/v1/chat/ask', methods=['POST'])
def chat_v1():
    return chat()

if __name__ == '__main__':
    print("🤖 Iniciando Fashion Store Bot Simple...")
    print("🌐 Servidor disponible en: http://localhost:5000")
    print("📱 Health check: http://localhost:5000/health")
    print("💬 Chat API: http://localhost:5000/api/chat")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
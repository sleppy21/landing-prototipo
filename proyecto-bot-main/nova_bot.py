#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot híbrido que combina la simplicidad de simple_bot.py 
con las funcionalidades avanzadas de app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import logging
import time
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*")

# Estadísticas simples
stats = {
    'start_time': time.time(),
    'total_messages': 0,
    'popular_questions': {},
    'user_sessions': {}
}

# Respuestas mejoradas del bot
RESPUESTAS = {
    'saludo': [
        "¡Hola! 👋 Bienvenido a Fashion Store. Soy NOVA, tu asistente virtual. ¿En qué puedo ayudarte?",
        "¡Hola! ✨ Soy NOVA, tu asistente personal de Fashion Store. ¿Cómo puedo ayudarte hoy?",
        "¡Hola! 🌟 ¿Buscas algo específico en nuestra tienda? Estoy aquí para ayudarte."
    ],
    'ofertas': [
        "🏷️ ¡Ofertas increíbles esperándote! Hasta 50% de descuento en vestidos de verano y 30% en toda la colección de primavera.",
        "🔥 ¡Super ofertas del día! 2x1 en accesorios seleccionados y envío gratis en compras superiores a $50.",
        "💎 ¡Ofertas exclusivas! Descuentos especiales en nuestra colección premium. ¿Te interesa alguna categoría en particular?"
    ],
    'tallas': [
        "📏 Ofrecemos tallas completas desde XS hasta XXL. Tenemos una guía detallada de medidas. ¿Para qué prenda necesitas información?",
        "👗 Nuestras tallas van desde XS hasta XXL con ajuste perfecto. ¿Necesitas ayuda con alguna talla específica?",
        "📐 Tenemos guía de tallas interactiva y asesoramiento personalizado. ¿Qué tipo de prenda estás buscando?"
    ],
    'envios': [
        "📦 Envíos gratis en compras mayores a $50. Entrega estándar 2-3 días, express 24h disponible.",
        "🚚 Ofrecemos envío a todo el país: Express (24h), Estándar (2-3 días) y Programado para tu comodidad.",
        "🌍 Envíos nacionales e internacionales. Tracking en tiempo real incluido. ¿Necesitas información sobre tu zona?"
    ],
    'horarios': [
        "🕒 Estamos disponibles: Lunes a Viernes 9:00-18:00, Sábados 10:00-16:00. Chat 24/7 disponible.",
        "⏰ Horarios de atención: L-V 9:00-18:00, Sábados 10:00-16:00. Soporte online siempre activo.",
        "🔔 Atención personalizada: L-V 9:00-18:00, Sábados 10:00-16:00. ¿Necesitas ayuda inmediata?"
    ],
    'productos': [
        "👗 Descubre nuestra colección: vestidos elegantes, casual wear, ropa de oficina y accesorios únicos.",
        "✨ Catálogo completo: moda femenina de alta calidad, desde básicos hasta piezas de diseñador exclusivas.",
        "🛍️ Explora nuestras categorías: vestidos, blusas, pantalones, accesorios y la nueva colección seasonal."
    ],
    'pago': [
        "💳 Aceptamos: tarjetas de crédito/débito, PayPal, transferencias bancarias y pago en efectivo contra entrega.",
        "🔒 Pagos 100% seguros con encriptación. Múltiples opciones: tarjetas, digital wallets y financiamiento.",
        "💰 Facilidades de pago disponibles: cuotas sin interés, pago diferido y descuentos por pago inmediato."
    ],
    'devolucion': [
        "↩️ Política de devolución: 30 días para cambios/devoluciones. Productos en perfecto estado con etiquetas.",
        "🔄 Cambios y devoluciones gratuitas dentro de 30 días. Proceso simple y rápido garantizado.",
        "✅ Garantía de satisfacción: devolución fácil, reembolso completo o cambio por otra talla/color."
    ],
    'contacto': [
        "📞 Contáctanos: WhatsApp, email, chat en vivo. Respuesta inmediata garantizada.",
        "📧 Múltiples canales: support@fashionstore.com, chat web, redes sociales. ¡Siempre conectados!",
        "🤝 Soporte personalizado: teléfono, email, chat. Equipo especializado listo para ayudarte."
    ],
    'default': [
        "🤔 Interesante pregunta. Puedo ayudarte con información sobre productos, ofertas, tallas, envíos, horarios y más. ¿Qué necesitas saber?",
        "💭 Estoy aquí para asistirte con cualquier duda sobre Fashion Store. ¿Productos, envíos, ofertas, o algo más específico?",
        "🎯 Mi especialidad es ayudarte con todo lo relacionado a nuestra tienda. ¿Qué información buscas exactamente?"
    ]
}

def detectar_intencion(mensaje):
    """Detecta la intención del mensaje con mayor precisión"""
    mensaje_lower = mensaje.lower()
    
    # Saludos - más variaciones
    if any(word in mensaje_lower for word in ['hola', 'buenos', 'buenas', 'saludos', 'hi', 'hello', 'hey', 'holi']):
        return 'saludo'
    
    # Ofertas y precios
    if any(word in mensaje_lower for word in ['oferta', 'descuento', 'promocion', 'rebaja', 'precio', 'barato', 'económico', 'liquidacion']):
        return 'ofertas'
    
    # Tallas y medidas
    if any(word in mensaje_lower for word in ['talla', 'tamaño', 'medida', 'size', 'ajuste', 'queda']):
        return 'tallas'
    
    # Envíos y entregas
    if any(word in mensaje_lower for word in ['envio', 'entrega', 'shipping', 'delivery', 'llega', 'demora']):
        return 'envios'
    
    # Horarios y atención
    if any(word in mensaje_lower for word in ['horario', 'hora', 'abierto', 'cerrado', 'atencion', 'cuando']):
        return 'horarios'
    
    # Productos y catálogo
    if any(word in mensaje_lower for word in ['producto', 'vestido', 'blusa', 'pantalon', 'ropa', 'accesorio', 'catalogo', 'coleccion']):
        return 'productos'
    
    # Pagos
    if any(word in mensaje_lower for word in ['pago', 'pagar', 'tarjeta', 'efectivo', 'financiamiento', 'cuotas']):
        return 'pago'
    
    # Devoluciones
    if any(word in mensaje_lower for word in ['devolucion', 'cambio', 'devolver', 'cambiar', 'garantia']):
        return 'devolucion'
    
    # Contacto
    if any(word in mensaje_lower for word in ['contacto', 'contactar', 'telefono', 'email', 'whatsapp']):
        return 'contacto'
    
    return 'default'

def log_interaction(mensaje, intencion, user_id=None):
    """Registra interacciones para analytics simples"""
    stats['total_messages'] += 1
    
    # Rastrear preguntas populares
    if intencion in stats['popular_questions']:
        stats['popular_questions'][intencion] += 1
    else:
        stats['popular_questions'][intencion] = 1
    
    # Log básico
    logger.info(f"Usuario: {mensaje[:50]}... | Intención: {intencion}")

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud mejorado"""
    uptime = time.time() - stats['start_time']
    return jsonify({
        'status': 'healthy',
        'service': 'Fashion Store NOVA Assistant',
        'version': '2.5.0',
        'uptime_seconds': int(uptime),
        'uptime_formatted': f"{int(uptime//3600)}h {int((uptime%3600)//60)}m",
        'total_messages': stats['total_messages'],
        'integration': 'active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat mejorado"""
    try:
        data = request.get_json()
        mensaje = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        
        if not mensaje:
            return jsonify({
                'response': 'Por favor, escribe un mensaje para poder ayudarte.',
                'status': 'error'
            }), 400
        
        # Detectar intención y generar respuesta
        intencion = detectar_intencion(mensaje)
        respuesta = random.choice(RESPUESTAS[intencion])
        
        # Registrar interacción
        log_interaction(mensaje, intencion, user_id)
        
        return jsonify({
            'response': respuesta,
            'status': 'success',
            'intent': intencion,
            'confidence': 0.95,  # Simular confianza alta
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en chat: {str(e)}")
        return jsonify({
            'response': 'Lo siento, ha ocurrido un error técnico. Por favor, intenta de nuevo en un momento.',
            'status': 'error',
            'error_code': 'CHAT_ERROR'
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Devuelve sugerencias inteligentes"""
    return jsonify({
        'suggestions': [
            "¿Qué ofertas tienen disponibles?",
            "Necesito información sobre tallas",
            "¿Cuáles son sus horarios de atención?",
            "¿Cómo funciona el envío?",
            "Quiero ver la nueva colección",
            "¿Qué métodos de pago aceptan?"
        ],
        'status': 'success'
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Estadísticas simples del bot"""
    uptime = time.time() - stats['start_time']
    
    # Calcular intención más popular
    most_popular = max(stats['popular_questions'].items(), key=lambda x: x[1]) if stats['popular_questions'] else ('ninguna', 0)
    
    return jsonify({
        'uptime_hours': round(uptime / 3600, 2),
        'total_messages': stats['total_messages'],
        'most_popular_intent': most_popular[0],
        'most_popular_count': most_popular[1],
        'intents_breakdown': stats['popular_questions'],
        'messages_per_hour': round(stats['total_messages'] / max(uptime / 3600, 0.1), 2)
    })

# Endpoints adicionales para compatibilidad
@app.route('/api/v1/chat/suggestions', methods=['GET'])
def get_suggestions_v1():
    return get_suggestions()

@app.route('/api/v1/chat/ask', methods=['POST'])
def chat_v1():
    return chat()

@app.route('/api/v1/analytics/dashboard', methods=['GET'])
def analytics_dashboard():
    return get_analytics()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'message': 'La ruta solicitada no existe',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}")
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Ha ocurrido un error interno. Nuestro equipo ha sido notificado.',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    print("🤖 Iniciando Fashion Store NOVA Assistant...")
    print("🌟 Versión híbrida con funcionalidades avanzadas")
    print("🌐 Servidor disponible en: http://localhost:5000")
    print("📱 Health check: http://localhost:5000/health")
    print("💬 Chat API: http://localhost:5000/api/chat")
    print("📊 Analytics: http://localhost:5000/api/analytics")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
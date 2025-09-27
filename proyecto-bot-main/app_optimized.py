#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fashion Store Bot - Sistema Optimizado
Bot que se inicia bajo demanda para mejor rendimiento
"""

import os
import sys
import datetime
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import socket

# Configuración básica
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'fashion-store-secret-key-2024'

# CORS optimizado para el frontend
CORS(app, 
     origins=["http://localhost:8080", "http://localhost:8081", "http://127.0.0.1:8080", "http://127.0.0.1:8081"],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Accept'],
     supports_credentials=False)

# Estado del bot
bot_status = {
    "initialized": True,
    "ready": True,
    "conversations": 0,
    "start_time": datetime.datetime.now()
}

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type, Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET, POST, OPTIONS")
        return response

@app.route('/')
def index():
    """API Info"""
    return jsonify({
        "service": "Fashion Store Bot",
        "version": "3.0.0",
        "status": "ready",
        "uptime": str(datetime.datetime.now() - bot_status["start_time"]),
        "conversations": bot_status["conversations"]
    })

@app.route('/health')
def health():
    """Health check optimizado"""
    return jsonify({
        "status": "healthy",
        "ready": bot_status["ready"],
        "timestamp": datetime.datetime.now().isoformat()
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat optimizado"""
    try:
        data = request.get_json()
        if not data or not data.get('message'):
            return jsonify({
                "error": "Mensaje requerido",
                "response": "Por favor, envía un mensaje válido."
            }), 400
            
        user_message = data.get('message', '').strip().lower()
        bot_status["conversations"] += 1
        
        # Sistema de respuestas inteligente
        response = get_intelligent_response(user_message)
        
        return jsonify({
            "response": response,
            "status": "success",
            "conversation_id": bot_status["conversations"],
            "timestamp": datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error en chat: {e}")
        return jsonify({
            "error": "Error del servidor",
            "response": "Disculpa, ha ocurrido un error. Por favor intenta de nuevo."
        }), 500

def get_intelligent_response(message):
    """Sistema de respuestas inteligente"""
    
    # Respuestas categorizadas por temas
    responses = {
        # Saludos
        "saludos": {
            "keywords": ["hola", "buenos", "buenas", "hey", "hi", "saludo"],
            "response": "¡Hola! 👋 Bienvenido a Fashion Store. Soy tu asistente virtual y estoy aquí para ayudarte. ¿En qué puedo asistirte hoy?"
        },
        
        # Productos
        "productos": {
            "keywords": ["producto", "ropa", "catálogo", "qué venden", "artículos", "tienda"],
            "response": "🛍️ En Fashion Store tenemos una amplia colección:\n\n👗 Ropa para mujer (vestidos, blusas, pantalones)\n👔 Ropa para hombre (camisas, pantalones, chaquetas)\n👶 Ropa infantil\n👜 Accesorios (bolsos, cinturones, joyas)\n👠 Calzado\n💄 Cosméticos\n\n¿Te interesa alguna categoría en particular?"
        },
        
        # Tallas
        "tallas": {
            "keywords": ["talla", "tamaño", "medida", "size", "guía"],
            "response": "📏 **Guía de Tallas Fashion Store**\n\n**Mujer:**\nXS (32-34) | S (36-38) | M (40-42) | L (44-46) | XL (48-50)\n\n**Hombre:**\nS (36-38) | M (40-42) | L (44-46) | XL (48-50) | XXL (52-54)\n\n**Calzado:** Disponible del 35 al 45\n\n💡 ¿Necesitas ayuda con alguna prenda específica?"
        },
        
        # Ofertas
        "ofertas": {
            "keywords": ["oferta", "descuento", "promoción", "rebaja", "barato", "precio"],
            "response": "🔥 **¡Ofertas Especiales!**\n\n🎉 Hasta 50% OFF en artículos seleccionados\n💳 15% adicional pagando con tarjeta\n📦 Envío GRATIS en compras +$99\n👕 3x2 en camisetas básicas\n👗 20% OFF en nueva colección\n\n⏰ Ofertas válidas hasta fin de mes. ¿Te interesa alguna categoría?"
        },
        
        # Envíos
        "envios": {
            "keywords": ["envío", "delivery", "entrega", "shipping", "cuánto tarda", "enviar"],
            "response": "📦 **Información de Envíos**\n\n🚚 **Envío estándar:** 3-5 días hábiles ($15)\n⚡ **Envío express:** 1-2 días hábiles ($25)\n🆓 **Envío gratis:** En compras mayores a $99\n📍 **Cobertura:** Todo el país\n📱 **Tracking:** Seguimiento en tiempo real\n\n¿Necesitas calcular el envío para tu ubicación?"
        },
        
        # Horarios
        "horarios": {
            "keywords": ["horario", "hora", "abierto", "cerrado", "cuándo", "atención"],
            "response": "🕒 **Horarios de Atención**\n\n🏪 **Tienda física:**\nLunes a Sábado: 10:00 AM - 9:00 PM\nDomingos: 11:00 AM - 7:00 PM\n\n💻 **Tienda online:** 24/7\n\n📞 **Atención al cliente:**\nLunes a Viernes: 9:00 AM - 6:00 PM\n📧 Email: soporte@fashionstore.com"
        },
        
        # Cambios y devoluciones
        "cambios": {
            "keywords": ["cambio", "devolución", "devolver", "cambiar", "garantía", "return"],
            "response": "🔄 **Política de Cambios y Devoluciones**\n\n✅ **30 días** para cambios y devoluciones\n🏷️ Productos con **etiquetas originales**\n📄 **Comprobante** de compra requerido\n💰 **Reembolso completo** o cambio por otro producto\n🆓 **Sin costo** para cambios en tienda\n\n¿Necesitas hacer algún cambio?"
        },
        
        # Contacto
        "contacto": {
            "keywords": ["contacto", "teléfono", "email", "dirección", "ubicación", "dónde"],
            "response": "📞 **Contáctanos**\n\n📱 WhatsApp: +1 234-567-8900\n📧 Email: info@fashionstore.com\n🏪 Dirección: Av. Principal 123, Centro\n💬 Chat en vivo: Disponible 24/7\n📱 App móvil: Descárgala gratis\n\n¿Cómo prefieres que te contactemos?"
        },
        
        # Pagos
        "pagos": {
            "keywords": ["pago", "tarjeta", "efectivo", "transferencia", "cuotas", "financiación"],
            "response": "💳 **Métodos de Pago**\n\n💳 Tarjetas de crédito/débito (Visa, MasterCard)\n📱 Pago móvil (PayPal, Apple Pay, Google Pay)\n💰 Efectivo (solo en tienda)\n🏦 Transferencia bancaria\n📊 **Cuotas sin interés** hasta 12 meses\n\n¿Necesitas información sobre financiación?"
        }
    }
    
    # Buscar respuesta inteligente
    for category, info in responses.items():
        for keyword in info["keywords"]:
            if keyword in message:
                return info["response"]
    
    # Respuesta por defecto más inteligente
    return """🤖 Hola, soy tu asistente virtual de Fashion Store. 

Puedo ayudarte con:
• 🛍️ Productos y catálogo
• 📏 Guía de tallas
• 🔥 Ofertas y promociones
• 📦 Información de envíos
• 🕒 Horarios de atención
• 🔄 Cambios y devoluciones
• 📞 Información de contacto

¿En qué te puedo ayudar específicamente?"""

@app.route('/api/suggestions')
def suggestions():
    """Sugerencias rápidas"""
    return jsonify({
        "suggestions": [
            {"text": "Ver ofertas del día 🔥", "action": "ofertas"},
            {"text": "Guía de tallas 📏", "action": "tallas"},
            {"text": "Información de envíos 📦", "action": "envios"},
            {"text": "Horarios de atención 🕒", "action": "horarios"},
            {"text": "Contactar soporte 📞", "action": "contacto"}
        ]
    })

def find_available_port(start_port=5000, max_attempts=10):
    """Encuentra un puerto disponible comenzando desde start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

if __name__ == "__main__":
    print("🤖 Fashion Store Bot - Sistema Optimizado")
    print("🔍 Detectando puerto disponible automáticamente...")
    
    # Encontrar puerto disponible automáticamente
    port = find_available_port(5000)
    if port is None:
        print("❌ No se pudo encontrar un puerto disponible")
        sys.exit(1)
    
    print(f"✅ Puerto {port} detectado como disponible")
    print(f"🚀 Iniciando en puerto {port}...")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Error iniciando el bot: {e}")
        sys.exit(1)
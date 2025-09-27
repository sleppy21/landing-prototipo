#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Aplicación principal del Bot Asistente de Tienda
Versión simplificada y funcional
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, render_template

# Agregar directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar encoding para Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False

# Importar después de configurar Flask
from src.core.chat_engine import ChatEngine

# Inicializar el motor de chat
chat_engine = None

def init_chat_engine():
    """Inicializa el motor de chat de forma segura"""
    global chat_engine
    try:
        if chat_engine is None:
            chat_engine = ChatEngine()
            print("✅ Motor de chat inicializado correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar motor de chat: {e}")
        # Crear un motor básico como fallback
        chat_engine = BasicChatEngine()

class BasicChatEngine:
    """Motor de chat básico como fallback"""
    
    def procesar_mensaje(self, mensaje):
        """Procesa un mensaje básico"""
        return {
            'respuesta': f'¡Hola! Soy tu asistente de Fashion Store. Has dicho: "{mensaje}". ¿En qué puedo ayudarte?',
            'intencion': 'saludo',
            'confianza': 0.8,
            'metadata': {}
        }

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal para el chat"""
    try:
        data = request.get_json()
        
        if not data or 'mensaje' not in data:
            return jsonify({
                'error': 'Mensaje requerido',
                'respuesta': 'Por favor proporciona un mensaje válido.'
            }), 400
        
        mensaje = data['mensaje'].strip()
        
        if not mensaje:
            return jsonify({
                'error': 'Mensaje vacío',
                'respuesta': 'Por favor escribe algo para poder ayudarte.'
            }), 400
        
        # Procesar el mensaje
        if chat_engine is None:
            init_chat_engine()
        
        resultado = chat_engine.procesar_mensaje(mensaje)
        
        return jsonify({
            'respuesta': resultado.get('respuesta', 'Lo siento, no pude procesar tu mensaje.'),
            'intencion': resultado.get('intencion', 'desconocida'),
            'confianza': resultado.get('confianza', 0.5),
            'timestamp': resultado.get('timestamp'),
            'metadata': resultado.get('metadata', {})
        })
        
    except Exception as e:
        print(f"Error en chat endpoint: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'respuesta': 'Lo siento, ocurrió un error. Por favor intenta de nuevo.'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud del sistema"""
    return jsonify({
        'status': 'healthy',
        'chat_engine': 'initialized' if chat_engine else 'not_initialized',
        'timestamp': None
    })

if __name__ == '__main__':
    print("🚀 Iniciando Fashion Store Assistant...")
    
    # Inicializar componentes
    init_chat_engine()
    
    # Configurar servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌟 Servidor ejecutándose en http://localhost:{port}")
    print("💬 Chat disponible en la interfaz web")
    print("🔧 Presiona Ctrl+C para detener")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n👋 Cerrando Fashion Store Assistant...")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")
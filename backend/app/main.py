#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app_integrated.py
Servidor integrado que combina el bot Flask con el landing page estático
Version fusionada para simplicidad de uso
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file

# Agregar directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar encoding para Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Crear app Flask que sirva tanto el bot como el landing
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Rutas para archivos estáticos del landing (CSS, JS, imágenes)
@app.route('/css/<path:filename>')
def serve_css(filename):
    """Servir archivos CSS del landing"""
    return send_from_directory('../../frontend/assets/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Servir archivos JavaScript del landing"""
    return send_from_directory('../../frontend/assets/js', filename)

@app.route('/img/<path:filename>')
def serve_images(filename):
    """Servir imágenes del landing"""
    return send_from_directory('../../frontend/assets/images', filename)

@app.route('/fonts/<path:filename>')
def serve_fonts(filename):
    """Servir fuentes del landing"""
    return send_from_directory('../../frontend/assets/fonts', filename)

# Rutas para páginas del landing
@app.route('/')
def landing_index():
    """Página principal del landing"""
    return send_file('../../frontend/pages/index.html')

@app.route('/shop.html')
def landing_shop():
    """Página de tienda"""
    return send_file('../../frontend/pages/shop.html')

@app.route('/product-details.html')
def landing_product_details():
    """Página de detalles del producto"""
    return send_file('../../frontend/pages/product-details.html')

@app.route('/shop-cart.html')
def landing_cart():
    """Página del carrito"""
    return send_file('../../frontend/pages/shop-cart.html')

@app.route('/checkout.html')
def landing_checkout():
    """Página de checkout"""
    return send_file('../../frontend/pages/checkout.html')

@app.route('/contact.html')
def landing_contact():
    """Página de contacto"""
    return send_file('../../frontend/pages/contact.html')

@app.route('/blog.html')
def landing_blog():
    """Página del blog"""
    return send_file('../../frontend/pages/blog.html')

@app.route('/blog-details.html')
def landing_blog_details():
    """Página de detalles del blog"""
    return send_file('../../frontend/pages/blog-details.html')

@app.route('/test-chat-integration.html')
def test_page():
    """Página de pruebas de integración"""
    return send_file('../../frontend/pages/test-chat-integration.html')

# Importar funcionalidad del bot después de configurar Flask
try:
    from core.chat_engine import ChatEngine
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

except ImportError:
    print("⚠️ Módulos del bot no encontrados, usando funcionalidad básica")
    chat_engine = None
    
    class BasicChatEngine:
        """Motor de chat básico como fallback"""
        
        def procesar_mensaje(self, mensaje):
            """Procesa un mensaje básico"""
            respuestas_predefinidas = {
                'hola': '¡Hola! Bienvenido a Fashion Store. ¿En qué puedo ayudarte?',
                'productos': 'Tenemos una gran variedad de productos: camisetas, pantalones, chaquetas, zapatos y más. ¿Te interesa algo específico?',
                'ofertas': '¡Tenemos ofertas increíbles! Descuentos de hasta 50% en productos seleccionados.',
                'precios': 'Nuestros precios son muy competitivos. ¿Qué producto te interesa?',
                'ubicacion': 'Estamos ubicados en el centro comercial principal. También ofrecemos envío a domicilio.',
                'devoluciones': 'Aceptamos devoluciones dentro de 30 días con el recibo de compra.',
                'ayuda': 'Estoy aquí para ayudarte con cualquier pregunta sobre nuestros productos y servicios.'
            }
            
            mensaje_lower = mensaje.lower()
            respuesta = "¡Hola! Soy tu asistente virtual de Fashion Store. Puedo ayudarte con información sobre productos, precios, ofertas y más. ¿En qué puedo ayudarte?"
            
            for palabra_clave, resp in respuestas_predefinidas.items():
                if palabra_clave in mensaje_lower:
                    respuesta = resp
                    break
            
            return {
                'respuesta': respuesta,
                'intencion': 'consulta',
                'confianza': 0.7,
                'metadata': {}
            }
    
    def init_chat_engine():
        global chat_engine
        chat_engine = BasicChatEngine()
        print("✅ Motor de chat básico inicializado")

# Rutas del bot (interfaz del chat)
@app.route('/bot')
def bot_interface():
    """Interfaz del chat bot"""
    return render_template('index.html')

@app.route('/bot/chat', methods=['POST'])
def bot_chat():
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

@app.route('/chat', methods=['POST'])
def chat_compatibility():
    """Endpoint de compatibilidad para el chat (redirige a /bot/chat)"""
    return bot_chat()

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud del sistema"""
    return jsonify({
        'status': 'healthy',
        'chat_engine': 'initialized' if chat_engine else 'not_initialized',
        'services': ['landing_page', 'chat_bot'],
        'message': 'Servidor integrado funcionando correctamente'
    })

# Crear directorio de templates si no existe
templates_dir = Path('templates')
if not templates_dir.exists():
    templates_dir.mkdir(exist_ok=True)

# Crear template básico para el bot si no existe
bot_template = templates_dir / 'index.html'
if not bot_template.exists():
    bot_template.write_text('''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Bot - Fashion Store</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .chat-container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .chat-header { background: linear-gradient(135deg, #ca1515 0%, #e74c3c 100%); color: white; padding: 20px; text-align: center; }
        .chat-messages { height: 400px; overflow-y: auto; padding: 20px; }
        .chat-input { display: flex; padding: 20px; border-top: 1px solid #eee; }
        .chat-input input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-right: 10px; }
        .chat-input button { padding: 10px 20px; background: #ca1515; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .message { margin: 10px 0; padding: 10px; border-radius: 10px; }
        .user-message { background: #e3f2fd; text-align: right; }
        .bot-message { background: #f5f5f5; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 Asistente Virtual - Fashion Store</h1>
            <p>¡Hola! Estoy aquí para ayudarte</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                ¡Bienvenido! Soy tu asistente virtual de Fashion Store. Puedo ayudarte con información sobre productos, precios, ofertas y más. ¿En qué puedo ayudarte?
            </div>
        </div>
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Escribe tu mensaje aquí..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Enviar</button>
        </div>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Mostrar mensaje del usuario
            addMessage(message, 'user');
            input.value = '';
            
            // Enviar al servidor
            fetch('/bot/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensaje: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.respuesta || 'Lo siento, no pude procesar tu mensaje.', 'bot');
            })
            .catch(error => {
                addMessage('Error de conexión. Por favor intenta de nuevo.', 'bot');
                console.error('Error:', error);
            });
        }

        function addMessage(text, sender) {
            const messages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>''', encoding='utf-8')

if __name__ == '__main__':
    print("🚀 Iniciando Servidor Integrado Fashion Store...")
    print("📦 Combinando Landing Page + Chat Bot en un solo servidor")
    
    # Inicializar componentes
    init_chat_engine()
    
    # Configurar servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                 🏪 FASHION STORE - SERVIDOR INTEGRADO        ║
╠══════════════════════════════════════════════════════════════╣
║  🌐 Landing Page: http://localhost:{port}                         ║
║  🤖 Chat Bot:     http://localhost:{port}/bot                     ║
║  ❤️  Health:      http://localhost:{port}/health                  ║
║  🧪 Test Page:    http://localhost:{port}/test-chat-integration.html ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Todo funciona con UN SOLO COMANDO: python app_integrated.py ║
║  ✅ No necesitas dos servidores separados                   ║
║  ✅ El bot se abre directamente en el landing               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
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
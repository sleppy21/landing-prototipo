/**
 * Chat Integration Script
 * Maneja la integración del bot de chat con el landing Ashion
 * Versión profesional con manejo de errores y optimizaciones
 */

class ChatIntegration {
    constructor() {
        this.isInitialized = false;
        this.botServerUrl = 'http://localhost:5000';
        this.modal = null;
        this.iframe = null;
        this.floatButton = null;
        this.isModalOpen = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        // Configuración
        this.config = {
            checkServerInterval: 30000, // 30 segundos
            loadTimeout: 10000, // 10 segundos
            animationDelay: 1000 // 1 segundo
        };
        
        this.init();
    }

    /**
     * Inicializa la integración del chat
     */
    async init() {
        try {
            console.log('🤖 Iniciando integración del chat...');
            
            // Esperar a que el DOM esté listo
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setupChat());
            } else {
                this.setupChat();
            }
            
        } catch (error) {
            console.error('Error inicializando chat:', error);
            this.handleError('Error de inicialización');
        }
    }

    /**
     * Configura todos los elementos del chat
     */
    setupChat() {
        try {
            this.createFloatButton();
            this.createModal();
            this.bindEvents();
            this.checkBotServer();
            this.isInitialized = true;
            
            console.log('✅ Chat integrado correctamente');
            
            // Mostrar botón con animación después de un delay
            setTimeout(() => {
                if (this.floatButton) {
                    this.floatButton.classList.add('animate-entry');
                    this.floatButton.style.display = 'flex';
                }
            }, this.config.animationDelay);
            
        } catch (error) {
            console.error('Error configurando chat:', error);
            this.handleError('Error de configuración');
        }
    }

    /**
     * Crea el botón flotante
     */
    createFloatButton() {
        this.floatButton = document.createElement('button');
        this.floatButton.className = 'chat-float-button';
        this.floatButton.style.display = 'none'; // Oculto inicialmente
        this.floatButton.innerHTML = `
            <i class="fas fa-comments chat-icon" aria-hidden="true"></i>
            <span class="sr-only">Abrir chat de ayuda</span>
        `;
        this.floatButton.setAttribute('aria-label', 'Abrir asistente virtual');
        this.floatButton.setAttribute('title', 'Hablar con nuestro asistente virtual');
        
        document.body.appendChild(this.floatButton);
    }

    /**
     * Crea el modal del chat
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'chat-modal';
        this.modal.innerHTML = `
            <div class="chat-modal-content" role="dialog" aria-labelledby="chat-title" aria-modal="true">
                <div class="chat-modal-header">
                    <div class="chat-bot-avatar"></div>
                    <div class="chat-header-text">
                        <h2 id="chat-title" class="chat-modal-title">Asistente Virtual</h2>
                        <p class="chat-modal-subtitle">Fashion Store Assistant</p>
                    </div>
                    <button class="chat-close-button" aria-label="Cerrar chat">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="chat-iframe-container">
                    <div class="chat-loading">
                        <div class="chat-loading-spinner"></div>
                        <p>Conectando con el asistente...</p>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.modal);
    }

    /**
     * Vincula todos los eventos
     */
    bindEvents() {
        // Botón flotante
        if (this.floatButton) {
            this.floatButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal();
            });
        }

        // Botón cerrar modal
        const closeButton = this.modal.querySelector('.chat-close-button');
        if (closeButton) {
            closeButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal();
            });
        }

        // Cerrar modal al hacer click fuera
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Cerrar modal con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isModalOpen) {
                this.closeModal();
            }
        });

        // Eventos de ventana
        window.addEventListener('resize', () => this.handleResize());
        window.addEventListener('beforeunload', () => this.cleanup());
    }

    /**
     * Abre el modal del chat
     */
    async openModal() {
        if (this.isModalOpen) return;

        try {
            console.log('📱 Abriendo chat...');
            
            this.isModalOpen = true;
            this.modal.classList.add('active');
            
            // Deshabilitar scroll del body
            document.body.style.overflow = 'hidden';
            
            // Crear interfaz de chat si no existe
            if (!this.chatCreated) {
                await this.createChatInterface();
                this.chatCreated = true;
            }
            
            // Analytics
            this.trackEvent('chat_opened');
            
        } catch (error) {
            console.error('Error abriendo modal:', error);
            this.handleError('Error abriendo el chat');
            this.closeModal();
        }
    }

    /**
     * Cierra el modal del chat
     */
    closeModal() {
        if (!this.isModalOpen) return;

        console.log('📱 Cerrando chat...');
        
        this.isModalOpen = false;
        this.modal.classList.remove('active');
        
        // Restaurar scroll del body
        document.body.style.overflow = '';
        
        // Analytics
        this.trackEvent('chat_closed');
    }

    /**
     * Crea la interfaz de chat directa (sin iframe)
     */
    async createChatInterface() {
        const container = this.modal.querySelector('.chat-iframe-container');
        const loading = container.querySelector('.chat-loading');
        
        // Ocultar loading
        if (loading) loading.style.display = 'none';
        
        // Crear interfaz de chat directa
        container.innerHTML = `
            <div class="direct-chat-container">
                <div class="chat-messages-container" id="chatMessages">
                    <div class="welcome-message">
                        <div class="bot-message">
                            <div class="message-avatar"></div>
                            <div class="message-content">
                                <h3>¡Hola! Soy tu asistente virtual</h3>
                                <p>Estoy aquí para ayudarte con información sobre productos, ofertas, tallas, envíos y más. ¿En qué puedo ayudarte?</p>
                                <div class="quick-suggestions">
                                    <button class="suggestion-btn" data-msg="Ver ofertas del día">🏷️ Ofertas</button>
                                    <button class="suggestion-btn" data-msg="Guía de tallas">📏 Tallas</button>
                                    <button class="suggestion-btn" data-msg="Horarios de atención">🕒 Horarios</button>
                                    <button class="suggestion-btn" data-msg="Información de envíos">📦 Envíos</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="chat-input-container">
                    <div class="input-wrapper">
                        <input type="text" id="chatInput" placeholder="Escribe tu pregunta aquí..." maxlength="500">
                        <button id="sendButton" class="send-btn"></button>
                    </div>
                    <div class="typing-indicator" id="typingIndicator" style="display: none;">
                        <span>Asistente está escribiendo</span>
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Configurar eventos del chat
        this.setupChatEvents();
        
        return Promise.resolve();
    }
    
    /**
     * Configura los eventos del chat directo
     */
    setupChatEvents() {
        const chatInput = this.modal.querySelector('#chatInput');
        const sendButton = this.modal.querySelector('#sendButton');
        const messagesContainer = this.modal.querySelector('#chatMessages');
        
        // Evento de envío
        const sendMessage = async () => {
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Limpiar input
            chatInput.value = '';
            
            // Agregar mensaje del usuario
            this.addUserMessage(message);
            
            // Mostrar indicador de escritura
            this.showTypingIndicator(true);
            
            try {
                // Enviar mensaje al bot
                const response = await this.sendMessageToBot(message);
                
                // Ocultar indicador de escritura
                this.showTypingIndicator(false);
                
                // Agregar respuesta del bot
                this.addBotMessage(response);
                
            } catch (error) {
                this.showTypingIndicator(false);
                this.addBotMessage('Lo siento, ha ocurrido un error. Por favor, intenta de nuevo.');
                console.error('Error enviando mensaje:', error);
            }
        };
        
        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Sugerencias rápidas
        this.modal.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-msg');
                chatInput.value = message;
                sendMessage();
            });
        });
    }
    
    /**
     * Agrega mensaje del usuario al chat
     */
    addUserMessage(message) {
        const messagesContainer = this.modal.querySelector('#chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(message)}</p>
                <span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
            <div class="message-avatar"></div>
        `;
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    /**
     * Agrega mensaje del bot al chat con animación de escritura
     */
    addBotMessage(message) {
        const messagesContainer = this.modal.querySelector('#chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'bot-message';
        messageDiv.innerHTML = `
            <div class="message-avatar"></div>
            <div class="message-content typing">
                <p></p>
                <span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Animación de escritura
        this.typeWriterEffect(messageDiv.querySelector('p'), message);
    }
    
    /**
     * Efecto de máquina de escribir
     */
    typeWriterEffect(element, text) {
        let i = 0;
        const speed = 30; // Velocidad de escritura (ms)
        
        // Configuración inicial sin restricciones de ancho
        element.style.whiteSpace = 'pre-wrap';
        element.style.wordWrap = 'break-word';
        element.style.borderRight = '2px solid #8b5cf6';
        element.style.minHeight = '1.2em'; // Altura mínima para el cursor
        
        const typeInterval = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                this.scrollToBottom();
            } else {
                clearInterval(typeInterval);
                // Finalizar animación
                element.style.borderRight = 'none';
                element.parentElement.classList.remove('typing');
                element.parentElement.classList.add('typing-complete');
            }
        }, speed);
    }
    
    /**
     * Hace scroll suave al final del chat
     */
    scrollToBottom() {
        const messagesContainer = this.modal.querySelector('#chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
    }
    
    /**
     * Muestra/oculta indicador de escritura
     */
    showTypingIndicator(show) {
        const indicator = this.modal.querySelector('#typingIndicator');
        if (indicator) {
            indicator.style.display = show ? 'flex' : 'none';
        }
    }
    
    /**
     * Envía mensaje al bot via API
     */
    async sendMessageToBot(message) {
        const response = await fetch(`${this.botServerUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.response || 'No se pudo obtener respuesta del bot.';
    }
    
    /**
     * Escapa HTML para evitar XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Verifica si el servidor del bot está disponible
     */
    async checkBotServer() {
        try {
            const response = await fetch(`${this.botServerUrl}/health`, {
                method: 'GET',
                timeout: 5000,
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                console.log('✅ Servidor del bot disponible');
                this.updateButtonState('available');
                this.retryCount = 0;
            } else {
                throw new Error(`Servidor respondió con: ${response.status}`);
            }

        } catch (error) {
            console.warn('⚠️ Servidor del bot no disponible:', error.message);
            this.updateButtonState('unavailable');
            
            // Reintentar después de un tiempo
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                setTimeout(() => this.checkBotServer(), 5000 * this.retryCount);
            }
        }

        // Programar próxima verificación
        setTimeout(() => this.checkBotServer(), this.config.checkServerInterval);
    }

    /**
     * Actualiza el estado visual del botón
     */
    updateButtonState(state) {
        if (!this.floatButton) return;

        const icon = this.floatButton.querySelector('.chat-icon');
        const badge = this.floatButton.querySelector('.chat-notification-badge');

        // Remover estados previos
        this.floatButton.classList.remove('pulse', 'unavailable');
        if (badge) badge.remove();

        switch (state) {
            case 'available':
                this.floatButton.disabled = false;
                this.floatButton.classList.add('pulse');
                this.floatButton.title = 'Hablar con nuestro asistente virtual';
                if (icon) icon.className = 'fas fa-comments chat-icon';
                break;

            case 'unavailable':
                this.floatButton.disabled = true;
                this.floatButton.classList.add('unavailable');
                this.floatButton.title = 'Asistente no disponible temporalmente';
                if (icon) icon.className = 'fas fa-exclamation-triangle chat-icon';
                break;

            case 'notification':
                if (!badge) {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'chat-notification-badge';
                    newBadge.textContent = '!';
                    this.floatButton.appendChild(newBadge);
                }
                break;
        }
    }

    /**
     * Maneja errores de la aplicación
     */
    handleError(message, error = null) {
        console.error('❌ Error en chat:', message, error);
        
        // Mostrar notificación al usuario
        this.showNotification(message, 'error');
        
        // Analytics
        this.trackEvent('chat_error', {
            message: message,
            error: error?.message || 'Unknown error'
        });
    }

    /**
     * Muestra notificaciones al usuario
     */
    showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `chat-notification chat-notification-${type}`;
        notification.innerHTML = `
            <div class="chat-notification-content">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Estilos inline para la notificación
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: type === 'error' ? '#dc3545' : '#17a2b8',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            zIndex: '10001',
            fontSize: '14px',
            maxWidth: '300px',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });

        document.body.appendChild(notification);

        // Animación de entrada
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    /**
     * Maneja cambios de tamaño de ventana
     */
    handleResize() {
        if (this.isModalOpen && this.iframe) {
            // Reajustar iframe si es necesario
            console.log('🔄 Reajustando chat por cambio de tamaño');
        }
    }

    /**
     * Rastrea eventos para analytics
     */
    trackEvent(eventName, data = {}) {
        try {
            // Enviar a Google Analytics si está disponible
            if (typeof gtag !== 'undefined') {
                gtag('event', eventName, {
                    event_category: 'chat_integration',
                    ...data
                });
            }

            // Log local para debug
            console.log('📊 Evento:', eventName, data);

        } catch (error) {
            console.warn('Error enviando analytics:', error);
        }
    }

    /**
     * Limpieza al cerrar la página
     */
    cleanup() {
        if (this.iframe) {
            this.iframe.src = 'about:blank';
        }
        console.log('🧹 Limpieza de chat completada');
    }

    /**
     * Método público para mostrar/ocultar el chat
     */
    toggle() {
        if (this.isModalOpen) {
            this.closeModal();
        } else {
            this.openModal();
        }
    }

    /**
     * Método público para obtener el estado
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            modalOpen: this.isModalOpen,
            serverAvailable: !this.floatButton?.disabled,
            retryCount: this.retryCount
        };
    }
}

// Estilos adicionales para notificaciones (inyectados dinámicamente)
const notificationStyles = `
    .chat-notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .chat-notification-content i {
        font-size: 16px;
    }
    
    @media (max-width: 480px) {
        .chat-notification {
            right: 10px !important;
            left: 10px !important;
            max-width: none !important;
        }
    }
`;

// Inyectar estilos
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Inicializar cuando el DOM esté listo
let chatIntegration;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chatIntegration = new ChatIntegration();
    });
} else {
    chatIntegration = new ChatIntegration();
}

// Exponer globalmente para debug
window.chatIntegration = chatIntegration;

// Registrar service worker si está disponible
if ('serviceWorker' in navigator && 'PushManager' in window) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('✅ Service Worker registrado:', registration.scope);
            })
            .catch(error => {
                console.log('❌ Error registrando Service Worker:', error);
            });
    });
}
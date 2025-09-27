/**
 * Fashion Store Chat Widget - Sistema Optimizado
 * Chat flotante que se inicia bajo demanda como las mejores páginas con IA
 */

class FashionStoreChatWidget {
    constructor() {
        this.isInitialized = false;
        this.isOpen = false;
        this.botUrl = null; // Se detectará automáticamente
        this.widget = null;
        this.chatContainer = null;
        this.messageHistory = [];
        
        // Puertos posibles donde puede estar el bot
        this.possiblePorts = [5000, 5001, 5002, 3000, 8000, 8001];
        this.detectedPort = null;
        
        // Configuración
        this.config = {
            position: 'bottom-right', // Posición del botón
            theme: 'modern', // Tema moderno
            autoGreeting: false, // Sin saludo automático
            lazyLoad: true, // Carga bajo demanda
            animations: true // Animaciones suaves
        };
        
        // Inicializar widget
        this.init();
    }

    /**
     * Inicialización del widget - Solo el botón flotante
     */
    init() {
        console.log('🤖 Inicializando Fashion Store Chat Widget...');
        
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.createFloatingButton());
        } else {
            this.createFloatingButton();
        }
        
        this.isInitialized = true;
        console.log('✅ Chat Widget inicializado correctamente');
    }

    /**
     * Detectar automáticamente el puerto del bot
     */
    async detectBotPort() {
        console.log('🔍 Detectando puerto del bot automáticamente...');
        
        for (const port of this.possiblePorts) {
            try {
                const response = await fetch(`http://localhost:${port}/health`, {
                    method: 'GET',
                    mode: 'cors',
                    cache: 'no-cache',
                    signal: AbortSignal.timeout(2000) // Timeout de 2 segundos por puerto
                });
                
                if (response.ok) {
                    this.detectedPort = port;
                    this.botUrl = `http://localhost:${port}`;
                    console.log(`✅ Bot detectado automáticamente en puerto ${port}`);
                    return true;
                }
            } catch (error) {
                // Continuar probando el siguiente puerto
                console.log(`⏭️ Puerto ${port} no disponible, probando siguiente...`);
            }
        }
        
        console.warn('❌ No se pudo detectar el bot en ningún puerto');
        return false;
    }

    /**
     * Crear solo el botón flotante (sin el chat aún)
     */
    createFloatingButton() {
        // Verificar que el CSS esté cargado
        this.ensureCSSLoaded();
        
        // Crear botón flotante
        this.widget = document.createElement('div');
        this.widget.className = 'fs-chat-widget';
        this.widget.innerHTML = `
            <button class="fs-chat-button" id="fsChatButton" aria-label="Abrir asistente virtual">
                <div class="fs-chat-icon">
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3.04.97 4.43L1 23l6.57-1.97C9.96 21.64 11.46 22 13 22h7c1.1 0 2-.9 2-2V12c0-5.52-4.48-10-10-10zm0 18c-1.1 0-2.14-.21-3.12-.6L6 20l.6-2.88C6.21 16.14 6 15.1 6 14c0-3.31 2.69-6 6-6s6 2.69 6 6-2.69 6-6 6z"/>
                    </svg>
                </div>
                <div class="fs-chat-text">¿Necesitas ayuda?</div>
            </button>
        `;
        
        // Agregar al DOM
        document.body.appendChild(this.widget);
        
        // Event listeners
        this.setupEventListeners();
        
        // Animación de entrada
        setTimeout(() => {
            this.widget.classList.add('fs-visible');
        }, 1000); // Aparece después de 1 segundo
    }

    /**
     * Verificar que el CSS del chat widget esté cargado
     */
    ensureCSSLoaded() {
        const cssId = 'fs-chat-widget-css';
        if (!document.getElementById(cssId)) {
            const link = document.createElement('link');
            link.id = cssId;
            link.rel = 'stylesheet';
            link.type = 'text/css';
            link.href = 'css/fashion-chat-widget.css';
            document.head.appendChild(link);
            console.log('✅ CSS del chat widget cargado');
        }
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        const button = this.widget.querySelector('#fsChatButton');
        
        button.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleChat();
        });

        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });
    }

    /**
     * Alternar chat (abrir/cerrar)
     */
    async toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            await this.openChat();
        }
    }

    /**
     * Abrir chat - AQUÍ se inicia el bot bajo demanda
     */
    async openChat() {
        if (this.isOpen) return;
        
        console.log('📱 Abriendo chat...');
        
        // Cambiar estado del botón
        const button = this.widget.querySelector('#fsChatButton');
        button.classList.add('fs-loading');
        
        try {
            // Crear interfaz de chat si no existe
            if (!this.chatContainer) {
                await this.createChatInterface();
            }
            
            // Mostrar chat
            this.showChatInterface();
            
            // Cambiar estado
            this.isOpen = true;
            button.classList.remove('fs-loading');
            button.classList.add('fs-active');
            
            // Detectar puerto del bot o iniciarlo si no existe
            if (!this.botUrl) {
                const detected = await this.detectBotPort();
                if (!detected) {
                    // Bot no detectado, iniciarlo bajo demanda
                    console.log('🤖 Bot no detectado, iniciando bajo demanda...');
                    await this.startBotOnDemand();
                }
            }
            
            // Verificar que el bot esté disponible
            await this.checkBotAvailability();
            
            // Enviar saludo inicial si es la primera vez
            if (this.messageHistory.length === 0) {
                // Limpiar mensaje de inicio
                const messagesContainer = this.chatContainer.querySelector('#fsChatMessages');
                messagesContainer.innerHTML = '';
                this.addWelcomeMessage();
            }
            
        } catch (error) {
            console.error('Error abriendo chat:', error);
            button.classList.remove('fs-loading');
            this.showError(`Error iniciando el asistente: ${error.message}`);
            
            // Mostrar mensaje de error en el chat
            if (this.chatContainer) {
                const messagesContainer = this.chatContainer.querySelector('#fsChatMessages');
                messagesContainer.innerHTML = `
                    <div class="fs-error-message">
                        <h3>⚠️ Error de Conexión</h3>
                        <p>No se pudo iniciar el asistente virtual.</p>
                        <p><strong>Posibles soluciones:</strong></p>
                        <ul>
                            <li>Verifica que Python esté instalado</li>
                            <li>Asegúrate que no haya firewall bloqueando</li>
                            <li>Intenta refrescar la página</li>
                        </ul>
                        <button class="fs-retry-btn" onclick="location.reload()">🔄 Reintentar</button>
                    </div>
                `;
            }
        }
    }

    /**
     * Verificar disponibilidad del bot
     */
    async checkBotAvailability() {
        if (!this.botUrl) {
            throw new Error('URL del bot no detectada');
        }
        
        const response = await fetch(`${this.botUrl}/health`);
        if (!response.ok) {
            throw new Error(`Bot no disponible en ${this.botUrl}`);
        }
        return response.json();
    }

    /**
     * Crear interfaz completa del chat
     */
    async createChatInterface() {
        this.chatContainer = document.createElement('div');
        this.chatContainer.className = 'fs-chat-container';
        this.chatContainer.innerHTML = `
            <div class="fs-chat-header">
                <div class="fs-chat-avatar">
                    <svg viewBox="0 0 24 24" width="32" height="32">
                        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                </div>
                <div class="fs-chat-info">
                    <h3>Asistente Virtual</h3>
                    <p class="fs-chat-status">
                        <span class="fs-status-dot"></span>
                        En línea
                    </p>
                </div>
                <button class="fs-chat-close" id="fsChatClose" aria-label="Cerrar chat">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                        <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
            
            <div class="fs-chat-messages" id="fsChatMessages">
                <!-- Los mensajes se agregan aquí dinámicamente -->
            </div>
            
            <div class="fs-chat-input-container">
                <div class="fs-chat-input-wrapper">
                    <input 
                        type="text" 
                        id="fsChatInput" 
                        placeholder="Escribe tu pregunta..." 
                        maxlength="500"
                        autocomplete="off"
                    >
                    <button class="fs-chat-send" id="fsChatSend" aria-label="Enviar mensaje">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
                <div class="fs-typing-indicator" id="fsTypingIndicator" style="display: none;">
                    <span>Asistente está escribiendo</span>
                    <div class="fs-typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        // Agregar al widget
        this.widget.appendChild(this.chatContainer);
        
        // Configurar eventos del chat
        this.setupChatEvents();
    }

    /**
     * Configurar eventos del chat
     */
    setupChatEvents() {
        // Botón cerrar
        const closeBtn = this.chatContainer.querySelector('#fsChatClose');
        closeBtn.addEventListener('click', () => this.closeChat());
        
        // Input y botón enviar
        const input = this.chatContainer.querySelector('#fsChatInput');
        const sendBtn = this.chatContainer.querySelector('#fsChatSend');
        
        const sendMessage = () => this.sendMessage(input.value.trim());
        
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Auto-focus en el input
        input.focus();
    }

    /**
     * Mostrar interfaz del chat
     */
    showChatInterface() {
        this.chatContainer.classList.add('fs-visible');
        document.body.classList.add('fs-chat-open');
    }

    /**
     * Cerrar chat
     */
    closeChat() {
        if (!this.isOpen) return;
        
        console.log('📱 Cerrando chat...');
        
        // Cambiar estado
        this.isOpen = false;
        
        // Actualizar UI
        const button = this.widget.querySelector('#fsChatButton');
        button.classList.remove('fs-active');
        
        if (this.chatContainer) {
            this.chatContainer.classList.remove('fs-visible');
        }
        
        document.body.classList.remove('fs-chat-open');
    }

    /**
     * Agregar mensaje de bienvenida
     */
    addWelcomeMessage() {
        const welcomeMsg = `¡Hola! 👋 Soy tu asistente virtual de Fashion Store. 

Puedo ayudarte con:
• 🛍️ Productos y catálogo
• 📏 Guía de tallas  
• 🔥 Ofertas especiales
• 📦 Información de envíos
• 🕒 Horarios de atención

¿En qué puedo ayudarte hoy?`;

        this.addBotMessage(welcomeMsg, true);
        this.addQuickSuggestions();
    }

    /**
     * Agregar sugerencias rápidas
     */
    addQuickSuggestions() {
        const suggestions = [
            { text: "Ver ofertas 🔥", query: "ofertas" },
            { text: "Guía de tallas 📏", query: "tallas" },
            { text: "Envíos 📦", query: "envios" },
            { text: "Horarios 🕒", query: "horarios" }
        ];

        const messagesContainer = this.chatContainer.querySelector('#fsChatMessages');
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'fs-quick-suggestions';
        
        suggestions.forEach(suggestion => {
            const btn = document.createElement('button');
            btn.className = 'fs-suggestion-btn';
            btn.textContent = suggestion.text;
            btn.addEventListener('click', () => {
                this.sendMessage(suggestion.query);
                suggestionsDiv.remove(); // Remover sugerencias después de usar
            });
            suggestionsDiv.appendChild(btn);
        });
        
        messagesContainer.appendChild(suggestionsDiv);
        this.scrollToBottom();
    }

    /**
     * Enviar mensaje
     */
    async sendMessage(message) {
        if (!message) return;
        
        // Limpiar input
        const input = this.chatContainer.querySelector('#fsChatInput');
        input.value = '';
        
        // Agregar mensaje del usuario
        this.addUserMessage(message);
        
        // Mostrar indicador de escritura
        this.showTypingIndicator(true);
        
        try {
            // Enviar al bot
            const response = await this.sendToBot(message);
            
            // Ocultar indicador
            this.showTypingIndicator(false);
            
            // Agregar respuesta del bot
            this.addBotMessage(response);
            
        } catch (error) {
            this.showTypingIndicator(false);
            this.addBotMessage('Disculpa, ha ocurrido un error. Por favor intenta de nuevo.');
            console.error('Error enviando mensaje:', error);
        }
    }

    /**
     * Enviar mensaje al bot
     */
    async sendToBot(message) {
        const response = await fetch(`${this.botUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.response;
    }

    /**
     * Agregar mensaje del usuario
     */
    addUserMessage(message) {
        const messagesContainer = this.chatContainer.querySelector('#fsChatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'fs-message fs-user-message';
        messageDiv.innerHTML = `
            <div class="fs-message-content">
                <p>${this.escapeHtml(message)}</p>
                <span class="fs-message-time">${this.getTimeString()}</span>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.messageHistory.push({ type: 'user', message, timestamp: new Date() });
        this.scrollToBottom();
    }

    /**
     * Agregar mensaje del bot con efecto de escritura
     */
    addBotMessage(message, instant = false) {
        const messagesContainer = this.chatContainer.querySelector('#fsChatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'fs-message fs-bot-message';
        messageDiv.innerHTML = `
            <div class="fs-message-avatar">
                <svg viewBox="0 0 24 24" width="24" height="24">
                    <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
            </div>
            <div class="fs-message-content">
                <div class="fs-message-text"></div>
                <span class="fs-message-time">${this.getTimeString()}</span>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.messageHistory.push({ type: 'bot', message, timestamp: new Date() });
        
        // Efecto de escritura o mostrar instantáneamente
        const textElement = messageDiv.querySelector('.fs-message-text');
        if (instant) {
            textElement.innerHTML = this.formatMessage(message);
        } else {
            this.typeWriterEffect(textElement, message);
        }
        
        this.scrollToBottom();
    }

    /**
     * Efecto de máquina de escribir
     */
    typeWriterEffect(element, text) {
        const formattedText = this.formatMessage(text);
        element.innerHTML = '';
        
        let i = 0;
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = formattedText;
        const plainText = tempDiv.textContent || tempDiv.innerText || '';
        
        const typeInterval = setInterval(() => {
            if (i < plainText.length) {
                element.innerHTML = this.formatMessage(plainText.substring(0, i + 1));
                i++;
                this.scrollToBottom();
            } else {
                clearInterval(typeInterval);
                element.innerHTML = formattedText; // Mostrar versión final con formato
            }
        }, 30);
    }

    /**
     * Formatear mensaje con markdown básico
     */
    formatMessage(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    /**
     * Mostrar/ocultar indicador de escritura
     */
    showTypingIndicator(show) {
        const indicator = this.chatContainer.querySelector('#fsTypingIndicator');
        indicator.style.display = show ? 'flex' : 'none';
        if (show) this.scrollToBottom();
    }

    /**
     * Scroll suave al final
     */
    scrollToBottom() {
        const messagesContainer = this.chatContainer.querySelector('#fsChatMessages');
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    /**
     * Obtener hora actual formateada
     */
    getTimeString() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Escapar HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Mostrar error
     */
    showError(message) {
        // Crear notificación de error
        const notification = document.createElement('div');
        notification.className = 'fs-error-notification';
        notification.innerHTML = `
            <div class="fs-error-content">
                <svg viewBox="0 0 24 24" width="20" height="20">
                    <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remover
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * Iniciar el bot bajo demanda
     */
    async startBotOnDemand() {
        console.log('🚀 Iniciando bot bajo demanda...');
        
        // Mostrar mensaje de carga
        this.showBotStartingMessage();
        
        try {
            console.log('⏳ Esperando que el bot se inicie...');
            
            // Intentar conectar cada 2 segundos por un máximo de 30 segundos
            for (let attempt = 1; attempt <= 15; attempt++) {
                console.log(`🔄 Intento ${attempt}/15 - Verificando si el bot está disponible...`);
                
                const detected = await this.detectBotPort();
                if (detected) {
                    console.log(`✅ Bot detectado y funcionando en puerto ${this.detectedPort}`);
                    return true;
                }
                
                // Si es el primer intento, mostrar mensaje especial
                if (attempt === 1) {
                    this.showBotStartingMessage('Iniciando servidor del bot...');
                    // Intentar iniciar el bot haciendo una petición especial
                    await this.triggerBotStart();
                }
                
                // Esperar 2 segundos antes del siguiente intento
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
            
            throw new Error('El bot no se pudo iniciar en el tiempo esperado');
            
        } catch (error) {
            console.error('❌ Error iniciando bot bajo demanda:', error);
            throw error;
        }
    }
    
    /**
     * Intentar activar el inicio del bot
     */
    async triggerBotStart() {
        try {
            // Intentar conectar a puertos comunes para despertar el bot
            const ports = [5000, 5001, 5002];
            
            for (const port of ports) {
                try {
                    await fetch(`http://localhost:${port}/health`, {
                        method: 'GET',
                        mode: 'cors',
                        cache: 'no-cache',
                        signal: AbortSignal.timeout(1000)
                    });
                } catch (e) {
                    // Ignorar errores, solo estamos intentando despertar el bot
                }
            }
        } catch (error) {
            // No hay problema si falla
        }
    }
    
    /**
     * Mostrar mensaje de que el bot se está iniciando
     */
    showBotStartingMessage(customMessage = null) {
        if (!this.chatContainer) return;
        
        const messagesContainer = this.chatContainer.querySelector('#fsChatMessages');
        
        // Limpiar mensajes anteriores
        messagesContainer.innerHTML = '';
        
        const startingMsg = customMessage || `🚀 Iniciando asistente virtual...

Por favor espera unos segundos mientras iniciamos el servidor del bot.

⏳ Esto puede tardar entre 5-15 segundos la primera vez.

🔄 El sistema se está preparando para atenderte.`;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'fs-message fs-bot-message fs-starting-message';
        messageDiv.innerHTML = `
            <div class="fs-message-avatar">
                <div class="fs-loading-spinner"></div>
            </div>
            <div class="fs-message-content">
                <div class="fs-message-text">${this.formatMessage(startingMsg)}</div>
                <span class="fs-message-time">${this.getTimeString()}</span>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
}

// Inicializar automáticamente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.fashionStoreChat = new FashionStoreChatWidget();
});

// Exponer globalmente para debugging
window.FashionStoreChatWidget = FashionStoreChatWidget;
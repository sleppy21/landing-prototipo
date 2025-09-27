/**
 * Chat Bot Integration Script
 * Compatible with Ashion Fashion Template
 * Version: 1.0
 */

class ChatBotIntegration {
    constructor(options = {}) {
        this.options = {
            botUrl: window.location.origin + '/bot',
            buttonPosition: 'bottom-right',
            autoOpen: false,
            enableTooltip: true,
            enableNotification: true,
            maxRetries: 3,
            retryDelay: 2000,
            ...options
        };
        
        this.isOpen = false;
        this.isLoading = false;
        this.retryCount = 0;
        this.elements = {};
        
        this.init();
    }
    
    init() {
        this.createElements();
        this.bindEvents();
        this.checkBotStatus();
        
        // Auto abrir si está habilitado
        if (this.options.autoOpen) {
            setTimeout(() => this.openChat(), 1000);
        }
        
        console.log('💬 Chat Bot Integration initialized');
    }
    
    createElements() {
        // Crear botón flotante
        this.elements.button = this.createChatButton();
        
        // Crear overlay del modal
        this.elements.overlay = this.createModalOverlay();
        
        // Crear modal
        this.elements.modal = this.createChatModal();
        
        // Insertar elementos en el DOM
        document.body.appendChild(this.elements.button);
        document.body.appendChild(this.elements.overlay);
        document.body.appendChild(this.elements.modal);
    }
    
    createChatButton() {
        const button = document.createElement('button');
        button.className = 'chat-bot-button';
        button.setAttribute('aria-label', 'Abrir chat de ayuda');
        button.setAttribute('title', 'Habla con nuestro asistente virtual');
        
        button.innerHTML = `
            <i class="fa fa-comments chat-icon" aria-hidden="true"></i>
            <i class="fa fa-times close-icon" aria-hidden="true"></i>
            ${this.options.enableTooltip ? '<div class="chat-tooltip">¿Necesitas ayuda?</div>' : ''}
        `;
        
        return button;
    }
    
    createModalOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'chat-modal-overlay';
        return overlay;
    }
    
    createChatModal() {
        const modal = document.createElement('div');
        modal.className = 'chat-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'chat-title');
        modal.setAttribute('aria-modal', 'true');
        
        modal.innerHTML = `
            <div class="chat-modal-header">
                <h3 class="chat-modal-title" id="chat-title">
                    <i class="fa fa-robot" aria-hidden="true"></i>
                    Asistente Virtual
                </h3>
                <div class="chat-status">En línea</div>
                <button class="chat-modal-close" aria-label="Cerrar chat">
                    <i class="fa fa-times" aria-hidden="true"></i>
                </button>
            </div>
            <div class="chat-modal-body">
                <div class="chat-loading">
                    <div class="spinner"></div>
                    <p>Conectando con el asistente...</p>
                </div>
                <iframe class="chat-iframe" style="display: none;"></iframe>
            </div>
        `;
        
        return modal;
    }
    
    bindEvents() {
        // Click en el botón
        this.elements.button.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleChat();
        });
        
        // Click en overlay para cerrar
        this.elements.overlay.addEventListener('click', () => {
            this.closeChat();
        });
        
        // Click en botón cerrar
        const closeButton = this.elements.modal.querySelector('.chat-modal-close');
        closeButton.addEventListener('click', () => {
            this.closeChat();
        });
        
        // Tecla ESC para cerrar
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });
        
        // Prevenir propagación de clicks dentro del modal
        this.elements.modal.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Eventos del iframe
        const iframe = this.elements.modal.querySelector('.chat-iframe');
        iframe.addEventListener('load', () => {
            this.onIframeLoad();
        });
        
        iframe.addEventListener('error', () => {
            this.onIframeError();
        });
        
        // Redimensionar ventana
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }
    
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    openChat() {
        if (this.isLoading) return;
        
        this.isOpen = true;
        this.isLoading = true;
        
        // Actualizar UI
        this.elements.button.classList.add('active');
        this.elements.overlay.classList.add('active');
        this.elements.modal.classList.add('active');
        
        // Cargar iframe si no está cargado
        const iframe = this.elements.modal.querySelector('.chat-iframe');
        if (!iframe.src) {
            this.loadBotInterface();
        } else {
            this.showIframe();
        }
        
        // Enfocar modal para accesibilidad
        this.elements.modal.focus();
        
        // Evento personalizado
        this.dispatchEvent('chatOpened');
        
        console.log('💬 Chat opened');
    }
    
    closeChat() {
        this.isOpen = false;
        
        // Actualizar UI
        this.elements.button.classList.remove('active');
        this.elements.overlay.classList.remove('active');
        this.elements.modal.classList.remove('active');
        
        // Devolver foco al botón
        this.elements.button.focus();
        
        // Evento personalizado
        this.dispatchEvent('chatClosed');
        
        console.log('💬 Chat closed');
    }
    
    loadBotInterface() {
        const iframe = this.elements.modal.querySelector('.chat-iframe');
        const loading = this.elements.modal.querySelector('.chat-loading');
        
        // Mostrar loading
        loading.style.display = 'block';
        iframe.style.display = 'none';
        
        // Configurar iframe
        iframe.src = this.options.botUrl;
        iframe.setAttribute('title', 'Interfaz del chat bot');
        
        // Timeout de seguridad
        setTimeout(() => {
            if (this.isLoading) {
                this.onIframeError();
            }
        }, 10000);
    }
    
    onIframeLoad() {
        const iframe = this.elements.modal.querySelector('.chat-iframe');
        const loading = this.elements.modal.querySelector('.chat-loading');
        
        try {
            // Verificar si el iframe cargó correctamente
            if (iframe.contentWindow && iframe.contentDocument) {
                this.showIframe();
                this.retryCount = 0;
            } else {
                throw new Error('Iframe no accesible');
            }
        } catch (error) {
            console.warn('No se puede acceder al contenido del iframe:', error);
            this.showIframe(); // Mostrar de todos modos
        }
    }
    
    showIframe() {
        const iframe = this.elements.modal.querySelector('.chat-iframe');
        const loading = this.elements.modal.querySelector('.chat-loading');
        
        this.isLoading = false;
        loading.style.display = 'none';
        iframe.style.display = 'block';
        
        // Animar entrada
        iframe.classList.add('fade-in');
        
        this.dispatchEvent('chatLoaded');
    }
    
    onIframeError() {
        console.error('Error cargando el chat bot');
        
        const loading = this.elements.modal.querySelector('.chat-loading');
        
        if (this.retryCount < this.options.maxRetries) {
            this.retryCount++;
            loading.innerHTML = `
                <div class="spinner"></div>
                <p>Reintentando conexión... (${this.retryCount}/${this.options.maxRetries})</p>
            `;
            
            setTimeout(() => {
                this.loadBotInterface();
            }, this.options.retryDelay);
        } else {
            this.showError();
        }
    }
    
    showError() {
        const loading = this.elements.modal.querySelector('.chat-loading');
        
        loading.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <i class="fa fa-exclamation-triangle" style="font-size: 48px; color: #e74c3c; margin-bottom: 15px;"></i>
                <h4 style="color: #333; margin-bottom: 10px;">Chat no disponible</h4>
                <p style="color: #666; margin-bottom: 20px;">
                    No se pudo conectar con el asistente virtual. 
                    Asegúrate de que el servidor esté ejecutándose.
                </p>
                <button onclick="window.chatBot.retryConnection()" 
                        style="background: #ca1515; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                    Reintentar
                </button>
                <p style="color: #999; font-size: 12px; margin-top: 15px;">
                    Para usar el chat, ejecuta: <code>python main.py</code> en la carpeta proyecto-bot
                </p>
            </div>
        `;
        
        this.isLoading = false;
        this.dispatchEvent('chatError');
    }
    
    retryConnection() {
        this.retryCount = 0;
        const iframe = this.elements.modal.querySelector('.chat-iframe');
        iframe.src = '';
        this.loadBotInterface();
    }
    
    checkBotStatus() {
        // Verificar si el bot está disponible
        fetch('/health', { 
            method: 'GET'
        })
        .then(response => {
            if (response.ok) {
                console.log('✅ Bot server is available');
                this.updateStatus('online');
            } else {
                console.warn('⚠️ Bot server not responding correctly');
                this.updateStatus('offline');
            }
        })
        .catch(() => {
            console.warn('⚠️ Bot server not available');
            this.updateStatus('offline');
        });
    }
    
    updateStatus(status) {
        const statusElement = this.elements.modal.querySelector('.chat-status');
        
        if (status === 'online') {
            statusElement.textContent = 'En línea';
            statusElement.style.color = 'rgba(255, 255, 255, 0.9)';
        } else {
            statusElement.textContent = 'Desconectado';
            statusElement.style.color = 'rgba(255, 255, 255, 0.6)';
        }
    }
    
    handleResize() {
        // Ajustar posición del modal en dispositivos móviles
        if (window.innerWidth <= 768 && this.isOpen) {
            this.elements.modal.style.transform = 'none';
        }
    }
    
    dispatchEvent(eventName, data = {}) {
        const event = new CustomEvent(`chatBot.${eventName}`, {
            detail: { ...data, instance: this }
        });
        document.dispatchEvent(event);
    }
    
    // Métodos públicos
    open() {
        this.openChat();
    }
    
    close() {
        this.closeChat();
    }
    
    toggle() {
        this.toggleChat();
    }
    
    destroy() {
        // Limpiar eventos y elementos
        this.elements.button.remove();
        this.elements.overlay.remove();
        this.elements.modal.remove();
        
        console.log('💬 Chat Bot Integration destroyed');
    }
}

// Auto-inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si ya existe una instancia
    if (!window.chatBot) {
        // Configuración por defecto
        const config = {
            botUrl: window.location.origin + '/bot',
            enableTooltip: true,
            enableNotification: true,
            autoOpen: false
        };
        
        // Crear instancia global
        window.chatBot = new ChatBotIntegration(config);
        
        // Eventos personalizados para integración
        document.addEventListener('chatBot.chatOpened', (e) => {
            console.log('Chat bot opened:', e.detail);
        });
        
        document.addEventListener('chatBot.chatClosed', (e) => {
            console.log('Chat bot closed:', e.detail);
        });
        
        document.addEventListener('chatBot.chatError', (e) => {
            console.error('Chat bot error:', e.detail);
        });
    }
});

// Exportar para uso como módulo
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatBotIntegration;
}
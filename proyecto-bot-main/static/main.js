// Fashion Store Assistant - Versión final optimizada
// Combina todas las mejores características sin errores de corrupción

// Configuración principal
const CONFIG = {
    TYPING_SPEED: 50,
    MAX_RETRIES: 3,
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 300,
    CACHE_DURATION: 5 * 60 * 1000, // 5 minutos
    MAX_SUGGESTIONS: 6,
    ERROR_MESSAGES: {
        NETWORK: "Parece que hay un problema de conexión. Por favor, verifica tu internet y vuelve a intentar.",
        SERVER: "El servidor está teniendo problemas. Por favor, intenta de nuevo en unos momentos.",
        GENERAL: "Ocurrió un error inesperado. Por favor, intenta de nuevo.",
        RATE_LIMIT: "Has enviado muchas consultas. Espera un momento antes de intentar de nuevo."
    },
    API_ENDPOINTS: {
        ASK: '/api/v1/chat/ask',
        STATUS: '/api/v1/chat/status',
        SUGGESTIONS: '/api/v1/chat/suggestions',
        HEALTH: '/health'
    }
};

// Utilidades mejoradas
const utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    formatMessage(text) {
        if (!text) return '';
        
        // Escapar HTML primero
        text = this.escapeHtml(text);
        
        // Formatear elementos especiales
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/S\/(\d+(\.\d{2})?)/g, '<span class="price">S/$1</span>')
            .replace(/\n/g, '<br>');
    }
};

// Cache Manager optimizado
class CacheManager {
    constructor() {
        this.cache = new Map();
        this.timestamps = new Map();
    }

    set(key, value) {
        this.cache.set(key, value);
        this.timestamps.set(key, Date.now());
        this.cleanup();
    }

    get(key) {
        const timestamp = this.timestamps.get(key);
        if (timestamp && (Date.now() - timestamp < CONFIG.CACHE_DURATION)) {
            return this.cache.get(key);
        }
        this.delete(key);
        return null;
    }

    delete(key) {
        this.cache.delete(key);
        this.timestamps.delete(key);
    }

    cleanup() {
        const now = Date.now();
        for (const [key, timestamp] of this.timestamps.entries()) {
            if (now - timestamp > CONFIG.CACHE_DURATION) {
                this.delete(key);
            }
        }
    }
}

// Gestor de sugerencias inteligente
class SuggestionsManager {
    constructor() {
        this.cache = new CacheManager();
        this.defaultSuggestions = [
            { text: "Ver ofertas del día", icon: "percentage", category: "promociones" },
            { text: "Política de devoluciones", icon: "exchange-alt", category: "servicio" },
            { text: "Métodos de pago", icon: "credit-card", category: "servicio" },
            { text: "Guía de tallas", icon: "ruler", category: "informacion" },
            { text: "Ubicación de tienda", icon: "map-marker-alt", category: "ubicacion" },
            { text: "Horario de atención", icon: "clock", category: "informacion" },
            { text: "Últimas novedades", icon: "sparkles", category: "productos" },
            { text: "Ropa formal", icon: "user-tie", category: "productos" }
        ];
        this.smartSuggestions = [];
        this.loadSmartSuggestions();
    }

    async loadSmartSuggestions() {
        try {
            const cached = this.cache.get('smart_suggestions');
            if (cached) {
                this.smartSuggestions = cached;
                return;
            }

            const response = await fetch(CONFIG.API_ENDPOINTS.SUGGESTIONS);
            if (response.ok) {
                const data = await response.json();
                this.smartSuggestions = data.suggestions || [];
                this.cache.set('smart_suggestions', this.smartSuggestions);
            }
        } catch (error) {
            console.log('Error loading smart suggestions:', error);
        }
    }

    filterSuggestions(query = "") {
        const allSuggestions = [...this.smartSuggestions, ...this.defaultSuggestions];
        
        if (!query.trim()) {
            return allSuggestions.slice(0, CONFIG.MAX_SUGGESTIONS);
        }

        const queryLower = query.toLowerCase();
        const filtered = allSuggestions.filter(s => 
            s.text.toLowerCase().includes(queryLower) ||
            (s.category && s.category.toLowerCase().includes(queryLower))
        );

        return filtered
            .sort((a, b) => {
                const aExact = a.text.toLowerCase().startsWith(queryLower);
                const bExact = b.text.toLowerCase().startsWith(queryLower);
                if (aExact && !bExact) return -1;
                if (!aExact && bExact) return 1;
                return 0;
            })
            .slice(0, CONFIG.MAX_SUGGESTIONS);
    }

    generateHTML(suggestions) {
        return suggestions.map(suggestion => `
            <button type="button" class="suggestion-chip" data-question="${utils.escapeHtml(suggestion.text)}">
                <i class="fas fa-${suggestion.icon}" aria-hidden="true"></i>
                ${utils.escapeHtml(suggestion.text)}
            </button>
        `).join('');
    }

    updateContextual(text) {
        const suggestions = [];
        const lowerText = text.toLowerCase();
        
        if (lowerText.includes('precio') || lowerText.includes('s/')) {
            suggestions.push({text: 'Ver más productos similares', icon: 'tags'});
        }
        if (lowerText.includes('talla')) {
            suggestions.push({text: 'Guía de tallas', icon: 'ruler'});
            suggestions.push({text: 'Política de cambios', icon: 'exchange-alt'});
        }
        if (lowerText.includes('color') || lowerText.includes('disponible')) {
            suggestions.push({text: 'Ver otros colores disponibles', icon: 'palette'});
        }
        if (lowerText.includes('devolución') || lowerText.includes('cambio')) {
            suggestions.push({text: 'Ubicación de la tienda', icon: 'map-marker-alt'});
        }
        
        return suggestions;
    }
}

// Monitor de conexión
class ConnectionMonitor {
    constructor() {
        this.isOnline = navigator.onLine;
        this.isHealthy = true;
        this.setupListeners();
    }

    setupListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showConnectionStatus('Conexión restaurada', 'success');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showConnectionStatus('Sin conexión a internet', 'error');
        });
    }

    showConnectionStatus(message, type) {
        const notification = document.createElement('div');
        notification.className = `connection-notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    markHealthy() {
        if (!this.isHealthy) {
            this.isHealthy = true;
            this.showConnectionStatus('Servidor conectado', 'success');
        }
    }

    markUnhealthy() {
        if (this.isHealthy) {
            this.isHealthy = false;
            this.showConnectionStatus('Problemas de conexión con el servidor', 'warning');
        }
    }
}

// Clase principal del chat optimizada
class ChatAssistant {
    constructor() {
        this.isProcessing = false;
        this.abortController = null;
        this.sessionId = this.generateSessionId();
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeTheme();
        this.setupAccessibility();
        
        this.suggestionsManager = new SuggestionsManager();
        this.connectionMonitor = new ConnectionMonitor();
        
        this.performanceMetrics = {
            responsesTimes: [],
            errorCount: 0,
            totalRequests: 0
        };
        
        this.showWelcomeMessage();
        this.setupPerformanceMonitoring();
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.chatForm = document.getElementById('chat-form');
        this.quickSuggestions = document.getElementById('quick-suggestions');
        this.themeToggle = document.getElementById('theme-toggle');
    }

    initializeEventListeners() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        this.userInput.addEventListener('input', utils.debounce(
            () => this.handleInputChange(), 
            CONFIG.DEBOUNCE_DELAY
        ));
        
        // Escuchar clics en sugerencias
        document.addEventListener('click', (e) => {
            const suggestionChip = e.target.closest('.suggestion-chip');
            if (suggestionChip && !this.isProcessing) {
                const question = suggestionChip.dataset.question;
                if (question) {
                    this.userInput.value = question;
                    this.handleSubmit(new Event('submit'));
                }
            }
        });
    }

    initializeTheme() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (this.themeToggle) {
                this.themeToggle.querySelector('i').classList.replace('fa-moon', 'fa-sun');
            }
        }

        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const icon = this.themeToggle.querySelector('i');
        
        if (isDark) {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            icon.classList.replace('fa-sun', 'fa-moon');
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            icon.classList.replace('fa-moon', 'fa-sun');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isProcessing) {
            await this.cancelCurrentRequest();
            return;
        }
        
        const question = this.userInput.value.trim();
        if (!question) return;

        this.isProcessing = true;
        this.updateSendButton(true);
        
        this.addUserMessage(question);
        this.userInput.value = '';
        this.showTypingIndicator();
        
        this.abortController = new AbortController();

        try {
            const response = await this.askQuestion(question, this.abortController.signal);
            this.hideTypingIndicator();
            
            if (response.canceled) {
                return;
            }
            
            if (response.error) {
                throw new Error(response.error);
            }

            await this.addBotMessageWithAnimation(response.answer);
            
            // Actualizar sugerencias contextuales
            const contextualSuggestions = this.suggestionsManager.updateContextual(response.answer);
            if (contextualSuggestions.length > 0) {
                this.quickSuggestions.innerHTML = this.suggestionsManager.generateHTML(contextualSuggestions);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            
            if (error.name === 'AbortError') {
                return;
            }
            
            await this.addBotMessage(
                'Lo siento, estoy teniendo problemas para procesar tu pregunta. ¿Podrías intentarlo de nuevo?',
                true
            );
        } finally {
            this.isProcessing = false;
            this.abortController = null;
            this.updateSendButton(false);
            this.userInput.focus();
        }
    }

    handleInputChange() {
        const query = this.userInput.value.trim();
        const filteredSuggestions = this.suggestionsManager.filterSuggestions(query);
        this.quickSuggestions.innerHTML = this.suggestionsManager.generateHTML(filteredSuggestions);
    }

    async askQuestion(question, signal) {
        const startTime = performance.now();
        
        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.ASK, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.sessionId
                },
                body: JSON.stringify({ 
                    question,
                    session_id: this.sessionId,
                    timestamp: Date.now()
                }),
                signal: signal
            });

            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error(CONFIG.ERROR_MESSAGES.RATE_LIMIT);
                }
                throw new Error('Error en la respuesta del servidor');
            }

            const result = await response.json();
            
            // Métricas de performance
            const responseTime = performance.now() - startTime;
            this.updatePerformanceMetrics(responseTime, false);
            this.connectionMonitor.markHealthy();
            
            return result;
            
        } catch (error) {
            const responseTime = performance.now() - startTime;
            this.updatePerformanceMetrics(responseTime, true);
            this.connectionMonitor.markUnhealthy();
            throw error;
        }
    }

    async cancelCurrentRequest() {
        if (this.abortController) {
            this.abortController.abort();
        }
        
        this.isProcessing = false;
        this.hideTypingIndicator();
        this.updateSendButton(false);
    }

    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `<div class="message-content">${utils.formatMessage(text)}</div>`;
        
        // Animación de entrada suave
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        this.chatMessages.appendChild(messageDiv);
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
        
        this.scrollToBottom();
    }

    addBotMessage(text, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message bot${isError ? ' error' : ''}`;
        messageDiv.innerHTML = `<div class="message-content">${utils.formatMessage(text)}</div>`;
        
        // Animación de entrada suave
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        this.chatMessages.appendChild(messageDiv);
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
        
        this.scrollToBottom();
    }

    async addBotMessageWithAnimation(text, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message bot${isError ? ' error' : ''}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        messageDiv.appendChild(contentDiv);
        
        // Animación de entrada suave
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        this.chatMessages.appendChild(messageDiv);
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
        
        // Esperar animación de entrada
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Efecto de escritura optimizado (por palabras)
        await this.typeWriterByWords(text, contentDiv);
        
        this.scrollToBottom();
    }

    async typeWriterByWords(text, element) {
        const words = text.split(' ');
        let currentText = '';
        
        for (let i = 0; i < words.length; i++) {
            currentText += words[i];
            
            if (i < words.length - 1) {
                currentText += ' ';
            }
            
            // Usar textContent para evitar problemas de encoding
            element.textContent = currentText;
            
            // Velocidad variable optimizada
            const delay = words[i].length > 5 ? 80 : 50;
            await new Promise(resolve => setTimeout(resolve, delay));
            
            this.scrollToBottom();
        }
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        typingDiv.style.opacity = '0';
        typingDiv.style.transform = 'translateY(20px)';
        this.chatMessages.appendChild(typingDiv);
        
        requestAnimationFrame(() => {
            typingDiv.style.transition = 'all 0.3s ease';
            typingDiv.style.opacity = '1';
            typingDiv.style.transform = 'translateY(0)';
        });
        
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.style.transition = 'all 0.3s ease';
            typingIndicator.style.opacity = '0';
            typingIndicator.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                if (typingIndicator.parentNode) {
                    typingIndicator.remove();
                }
            }, 300);
        }
    }

    updateSendButton(processing) {
        const sendBtn = this.sendBtn;
        const icon = sendBtn.querySelector('i');
        
        if (processing) {
            sendBtn.classList.add('processing');
            icon.className = 'fas fa-spinner fa-spin';
            sendBtn.disabled = true;
            sendBtn.setAttribute('aria-label', 'Procesando mensaje...');
        } else {
            sendBtn.classList.remove('processing');
            icon.className = 'fas fa-paper-plane';
            sendBtn.disabled = false;
            sendBtn.setAttribute('aria-label', 'Enviar mensaje');
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    updatePerformanceMetrics(responseTime, hasError) {
        this.performanceMetrics.totalRequests++;
        this.performanceMetrics.responsesTimes.push(responseTime);
        
        if (hasError) {
            this.performanceMetrics.errorCount++;
        }
        
        // Mantener solo las últimas 50 mediciones
        if (this.performanceMetrics.responsesTimes.length > 50) {
            this.performanceMetrics.responsesTimes = 
                this.performanceMetrics.responsesTimes.slice(-50);
        }
    }

    async showWelcomeMessage() {
        await new Promise(resolve => setTimeout(resolve, 500));
        await this.addBotMessageWithAnimation('Hola! Soy tu asistente de Fashion Store. En que puedo ayudarte hoy?');
    }

    setupPerformanceMonitoring() {
        // Health check periódico
        setInterval(() => {
            this.performHealthCheck();
        }, 30000);
    }

    async performHealthCheck() {
        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.HEALTH);
            if (response.ok) {
                this.connectionMonitor.markHealthy();
            } else {
                this.connectionMonitor.markUnhealthy();
            }
        } catch (error) {
            this.connectionMonitor.markUnhealthy();
        }
    }

    setupAccessibility() {
        // Manejar navegación por teclado
        this.chatMessages.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const focusableElements = this.chatMessages.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                this.handleTabNavigation(e, Array.from(focusableElements));
            }
        });

        // Anunciar mensajes nuevos para lectores de pantalla
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList?.contains('message') && !node.classList?.contains('typing')) {
                            const text = node.textContent;
                            const role = node.classList.contains('user') ? 'usuario' : 'asistente';
                            this.announceForScreenReader(`Nuevo mensaje de ${role}: ${text}`);
                        }
                    });
                }
            });
        });

        observer.observe(this.chatMessages, { childList: true });
    }

    handleTabNavigation(event, elements) {
        const firstElement = elements[0];
        const lastElement = elements[elements.length - 1];

        if (event.shiftKey && document.activeElement === firstElement) {
            lastElement.focus();
            event.preventDefault();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
            firstElement.focus();
            event.preventDefault();
        }
    }

    announceForScreenReader(text) {
        const announce = document.createElement('div');
        announce.setAttribute('aria-live', 'polite');
        announce.classList.add('sr-only');
        announce.textContent = text;
        document.body.appendChild(announce);
        setTimeout(() => announce.remove(), 1000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ChatAssistant();
    
    // Service Worker para PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(error => {
            console.log('Service Worker registration failed:', error);
        });
    }
});
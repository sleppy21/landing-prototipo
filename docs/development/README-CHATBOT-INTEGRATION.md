# 🤖 Integración Chat Bot - Fashion Store

## 📋 Descripción
Este proyecto integra un asistente virtual inteligente en el landing page de Fashion Store. El bot utiliza inteligencia artificial para responder preguntas sobre productos, precios, políticas y servicios de la tienda.

## 🏗️ Arquitectura del Proyecto

```
ashion-master/                    # Landing Page Principal
├── css/
│   ├── chat-bot.css             # Estilos del chat bot
│   └── ...                      # Otros estilos del template
├── js/
│   ├── chat-bot.js              # Funcionalidad del chat bot
│   └── ...                      # Otros scripts del template
├── index.html                   # Página principal (con bot integrado)
├── shop.html                    # Tienda (con bot integrado)
├── product-details.html         # Detalles de producto (con bot integrado)
├── shop-cart.html               # Carrito (con bot integrado)
├── checkout.html                # Checkout (con bot integrado)
├── contact.html                 # Contacto (con bot integrado)
├── blog.html                    # Blog (con bot integrado)
├── blog-details.html            # Detalle blog (con bot integrado)
└── proyecto-bot/                # Aplicación Flask del Bot (independiente)
    ├── main.py                  # Servidor principal del bot
    ├── app.py                   # Aplicación avanzada del bot
    ├── src/                     # Código fuente del bot
    ├── templates/               # Templates HTML del bot
    ├── static/                  # Archivos estáticos del bot
    └── data/                    # Datos y configuración del bot
```

## 🚀 Instalación y Configuración

### Paso 1: Preparar el Bot
```powershell
# Navegar a la carpeta del bot
cd "proyecto-bot"

# Instalar dependencias (automático)
./install_optimized.bat

# O instalación manual
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Paso 2: Iniciar el Bot
```powershell
# Opción 1: Usar script automático
./start.bat
python main.py

# Opción 2: Manual
venv\Scripts\activate
python main.py
```

El bot estará disponible en: `http://localhost:5000`

### Paso 3: Abrir el Landing Page
Simplemente abre cualquiera de las páginas HTML del landing en tu navegador. El botón de chat aparecerá automáticamente en la esquina inferior derecha.

## 🎨 Características de la Integración

### 🔘 Botón Flotante
- **Posición**: Esquina inferior derecha (estándar de la industria)
- **Diseño**: Circular con gradiente rojo que coincide con el tema del sitio
- **Animaciones**: Hover effects y transiciones suaves
- **Tooltip**: "¿Necesitas ayuda?" al pasar el mouse
- **Indicador**: Badge verde que indica que el bot está en línea
- **Responsive**: Se adapta a dispositivos móviles

### 🖼️ Modal del Chat
- **Tamaño**: 380x600px en desktop, pantalla completa en móvil
- **Posición**: Esquina inferior derecha con overlay semi-transparente
- **Header**: Título "Asistente Virtual" con estado de conexión
- **Cuerpo**: Iframe que contiene la interfaz completa del bot
- **Animaciones**: Entrada suave con efectos de escala y opacity
- **Responsive**: Adaptación automática a diferentes tamaños de pantalla

### ⚡ Funcionalidades Técnicas
- **Detección automática**: Verifica si el bot está disponible
- **Reintentos inteligentes**: Sistema de reintentos con backoff exponencial
- **Manejo de errores**: Mensajes informativos si el bot no está disponible
- **Accesibilidad**: Soporte completo para lectores de pantalla
- **Teclado**: Navegación con Tab y cierre con Escape
- **Performance**: CSS y JS optimizados, lazy loading

## 🎯 Cómo Usar el Chat Bot

### Para Usuarios Finales:
1. **Abrir chat**: Click en el botón flotante rojo en la esquina inferior derecha
2. **Interactuar**: El bot responde a preguntas en lenguaje natural
3. **Cerrar chat**: Click en la X del modal o presionar Escape

### Ejemplos de Preguntas:
```
- "¿Qué productos tienen en oferta?"
- "¿Cuánto cuesta la camiseta premium?"
- "¿Tienen envío gratis?"
- "¿Cuál es su política de devoluciones?"
- "¿Dónde están ubicados?"
- "Necesito ayuda con mi pedido"
```

## 🔧 Configuración Avanzada

### Personalizar la Integración
En el archivo `js/chat-bot.js`, puedes modificar:

```javascript
const config = {
    botUrl: 'http://localhost:5000',    // URL del servidor del bot
    enableTooltip: true,                // Mostrar tooltip de help
    enableNotification: true,           // Mostrar badge de notificación
    autoOpen: false,                    // Abrir automáticamente
    maxRetries: 3,                      // Reintentos máximos
    retryDelay: 2000                    // Delay entre reintentos (ms)
};
```

### Personalizar Estilos
En el archivo `css/chat-bot.css`, puedes modificar:

```css
/* Cambiar colores del botón */
.chat-bot-button {
    background: linear-gradient(135deg, #tu-color 0%, #otro-color 100%);
}

/* Cambiar posición del botón */
.chat-bot-button {
    bottom: 30px;  /* Distancia desde abajo */
    right: 30px;   /* Distancia desde la derecha */
}

/* Cambiar tamaño del modal */
.chat-modal {
    width: 400px;    /* Ancho */
    height: 650px;   /* Alto */
}
```

## 🌐 Compatibilidad

### Navegadores Soportados:
- ✅ Chrome 70+
- ✅ Firefox 65+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ Opera 60+

### Dispositivos:
- ✅ Desktop (Windows, macOS, Linux)
- ✅ Tablets (iPad, Android tablets)
- ✅ Móviles (iOS, Android)

### Resoluciones Probadas:
- ✅ 1920x1080 (Full HD)
- ✅ 1366x768 (Laptop estándar)
- ✅ 768x1024 (iPad)
- ✅ 375x667 (iPhone)
- ✅ 360x640 (Android móvil)

## 🐛 Solución de Problemas

### El botón no aparece:
1. Verifica que `chat-bot.css` y `chat-bot.js` estén cargados
2. Revisa la consola del navegador para errores de JavaScript
3. Asegúrate de que los archivos estén en las rutas correctas

### El bot no se conecta:
1. **Verificar que el servidor esté ejecutándose**:
   ```powershell
   cd proyecto-bot
   python main.py
   ```
2. **Verificar la URL**: Debe ser `http://localhost:5000`
3. **Verificar puertos**: Asegúrate de que el puerto 5000 esté disponible
4. **Firewall**: Permitir conexiones en el puerto 5000

### El modal no abre:
1. Revisa errores en la consola del navegador
2. Verifica que no haya conflictos con otros JavaScript
3. Comprueba que Font Awesome esté cargado (para los iconos)

### Problemas de diseño:
1. **Limpia caché**: Ctrl+F5 para recargar completamente
2. **Verifica CSS**: Asegúrate de que chat-bot.css se carga después de style.css
3. **Conflictos de estilos**: Revisa si hay estilos que interfieren

## 📱 Responsive Design

### Breakpoints:
- **Desktop**: > 768px - Modal flotante en esquina
- **Tablet**: 768px - Modal adaptado con márgenes
- **Móvil**: < 480px - Modal a pantalla completa

### Adaptaciones Móviles:
- Botón ligeramente más pequeño (55px vs 60px)
- Modal ocupa toda la pantalla excepto márgenes mínimos
- Tooltip oculto en dispositivos táctiles
- Gestos táctiles optimizados

## 🔒 Seguridad y Privacidad

### Medidas Implementadas:
- **CORS configurado**: Solo dominios autorizados
- **Sanitización**: Inputs del usuario sanitizados
- **Rate limiting**: Límite de requests por minuto
- **Iframe sandbox**: Restricciones de seguridad en iframe
- **No persistencia**: No se almacenan datos personales en localStorage

### Datos Compartidos:
- Solo se envían mensajes de texto al bot
- No se accede a cookies ni localStorage desde el landing
- Comunicación cifrada si se usa HTTPS

## 🚀 Deployment en Producción

### Para Servidor Web:
1. Subir todos los archivos del landing a tu servidor web
2. Configurar el bot en un servidor separado (VPS, cloud, etc.)
3. Actualizar la URL del bot en `js/chat-bot.js`:
   ```javascript
   botUrl: 'https://tu-dominio.com:5000'
   ```
4. Configurar HTTPS para ambos servicios
5. Configurar CORS en el servidor del bot para permitir tu dominio

### Para Desarrollo Local:
1. Mantener la configuración actual con `localhost:5000`
2. Ejecutar el bot con `python main.py`
3. Abrir el landing desde un servidor web local (no file://)

## 📊 Analytics y Monitoreo

El bot incluye sistema de analytics que registra:
- Número de conversaciones iniciadas
- Preguntas más frecuentes
- Tiempo promedio de sesión
- Errores y problemas técnicos

Acceso al dashboard: `http://localhost:5000/api/v1/analytics/dashboard`

## 🛠️ Mantenimiento

### Actualizaciones Regulares:
1. **Bot**: Actualizar modelos de IA y base de conocimientos
2. **Landing**: Mantener compatibilidad con nuevas versiones de navegadores
3. **Dependencias**: Actualizar librerías de seguridad

### Logs y Monitoreo:
- Logs del bot: Revisa la consola donde ejecutas `python main.py`
- Logs del frontend: Abre Developer Tools (F12) en el navegador
- Health check: `http://localhost:5000/health`

## 🤝 Contribución

Para mejorar la integración:
1. Fork el repositorio
2. Crear branch para feature: `git checkout -b feature/mejora-chat`
3. Realizar cambios y commit: `git commit -m "Descripción"`
4. Push: `git push origin feature/mejora-chat`
5. Crear Pull Request

## 📞 Soporte

Si necesitas ayuda:
1. **Documentación**: Revisa este README completo
2. **Issues**: Crea un issue en GitHub con detalles del problema
3. **Logs**: Incluye siempre logs de consola y errores específicos
4. **Contexto**: Menciona SO, navegador, y pasos para reproducir

---

**🎉 ¡Disfruta de tu nuevo asistente virtual integrado! 🤖**

*Desarrollado con ❤️ para Fashion Store*  
*Versión 1.0 - Septiembre 2025*
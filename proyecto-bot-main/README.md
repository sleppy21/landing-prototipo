# Bot Asistente de Consultas - Fashion Store

## 🤖 Descripción
Bot asistente virtual inteligente para Fashion Store con procesamiento de lenguaje natural avanzado y búsqueda vectorial semántica. Utiliza modelos de IA locales para proporcionar respuestas contextuales sobre productos, precios, políticas y servicios de la tienda.

## 📋 Requisitos del Sistema

### Python
- **Versión requerida**: Python 3.11+ (Recomendado: Python 3.11.9)
- **Sistema operativo**: Windows, macOS, Linux
- **RAM mínima**: 4GB (Recomendado: 8GB+)
- **Espacio en disco**: 2GB libres

### Verificar Versión de Python
```bash
python --version
# Debe mostrar: Python 3.11.x o superior
```

## 🛠️ Instalación Paso a Paso

### 1. Clonar el Repositorio
```powershell
git clone https://github.com/sleppy21/proyecto-bot.git
cd proyecto-bot
```

### 2. Instalación Automática (Windows)
Ejecuta el script para instalar todo automáticamente:
```powershell
install_optimized.bat
```
Esto creará y activará el entorno virtual, instalará dependencias y optimizará el cache de paquetes.

### 3. Arranque del Bot
Para iniciar el bot y activar el entorno virtual:
```powershell
start.bat
```
Esto dejará la consola lista para ejecutar:
```powershell
python main.py         # Ejecuta el bot principal
python test_server.py  # Prueba el servidor
deactivate             # Salir del entorno virtual
```

---

**¿Instalación manual?**
Si prefieres instalar manualmente, sigue los pasos clásicos:
1. Crear entorno virtual: `python -m venv venv`
2. Activar entorno: `venv\Scripts\activate`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar: `python main.py`

## 📦 Dependencias Principales

### Core del Proyecto
- `flask==3.0.0` - Servidor web
- `werkzeug==3.0.1` - WSGI toolkit

### Inteligencia Artificial
- `torch==2.1.0` - Framework de Machine Learning
- `transformers==4.35.0` - Modelos de Hugging Face
- `sentence-transformers==2.2.2` - Embeddings semánticos
- `numpy==1.24.3` - Computación numérica
- `scikit-learn==1.3.0` - Algoritmos ML adicionales

### Utilidades
- `requests==2.31.0` - Cliente HTTP
- `tqdm==4.66.1` - Barras de progreso

## 🚀 Ejecución del Proyecto

### 1. Verificar Estructura de Archivos
Asegúrate de que tienes la siguiente estructura:
```
Bot-Asistente-de-Consultas/
├── bot_tienda.py          # Servidor principal
├── prompts.py             # Procesadores de IA
├── requirements.txt       # Dependencias
├── data/
│   └── catalogue.json     # Catálogo de productos
├── static/               # Archivos CSS, JS, PWA
├── templates/            # Templates HTML
└── venv/                # Entorno virtual (creado en instalación)
```

### 2. Activar Entorno Virtual (si no está activo)
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Ejecutar el Servidor
```bash
python bot_tienda.py
```

### 4. Acceder al Bot
- **Local**: http://localhost:5000
- **Red local**: http://192.168.1.41:5000 (o tu IP local)

## ⚠️ Solución de Problemas Comunes

### Error: "ModuleNotFoundError"
```bash
# Verificar que el entorno virtual está activado
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "torch no disponible"
```bash
# Para sistemas con problemas con PyTorch
pip uninstall torch
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
```

### Error: "Memoria insuficiente"
El proyecto está optimizado para usar modelos ligeros. Si sigues teniendo problemas:
- Cierra otras aplicaciones que consuman RAM
- Reinicia el sistema
- Verifica que tienes al menos 4GB de RAM disponible

### Error: "Puerto 5000 ocupado"
```bash
# En Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# En macOS/Linux  
lsof -ti:5000 | xargs kill -9
```

## 🎯 Funcionalidades Principales

### 🤖 IA Avanzada
- **Búsqueda Vectorial Semántica**: Encuentra respuestas precisas usando embeddings
- **Detección de Intenciones**: Reconoce automáticamente el tipo de consulta
- **Respuestas Contextuales**: Genera respuestas naturales tipo ChatGPT

### 🛍️ Funciones de Tienda
- Consulta de productos (precios, tallas, colores, disponibilidad)
- Información sobre ofertas y promociones actuales
- Políticas (devoluciones, envíos, garantías)
- Horarios y ubicación de tiendas
- Sistema de FAQ inteligente

### 💻 Interfaz Moderna
- Diseño responsive (móvil y desktop)
- Tema claro/oscuro automático
- Animaciones suaves y naturales
- Efecto de escritura del bot en tiempo real
- PWA (Progressive Web App) - instalable como app

## 🧪 Probar el Bot

### Consultas de Ejemplo
```
- "Ver ofertas del día"
- "¿Cuánto cuesta la camiseta premium?"
- "¿Tienen jeans en talla 32?"
- "¿Cuál es la política de devoluciones?"
- "¿Dónde están ubicados?"
- "hola" / "@agent Continuar"
```

### Comandos Especiales
- `@agent Continuar` - Continúa la conversación
- Preguntas sobre productos específicos
- Consultas sobre servicios y políticas

## 🔧 Configuración Avanzada

### Variables de Entorno (Opcional)
```bash
# Crear archivo .env
PORT=5000                    # Puerto del servidor
HOST=0.0.0.0                # Host del servidor  
MODEL_ID=google/flan-t5-small # Modelo de IA
REQUESTS_PER_MINUTE=40      # Límite de requests
CACHE_TTL=300               # Tiempo de caché (segundos)
```

### Personalización
- Edita `data/catalogue.json` para modificar productos y FAQs
- Modifica `static/styles.css` para cambiar la apariencia
- Actualiza `prompts.py` para ajustar las respuestas del bot

## 📊 Monitoreo

### Logs del Sistema
Los logs se muestran en la consola con información sobre:
- Inicialización de modelos de IA
- Procesamiento de consultas
- Errores y warnings
- Rendimiento del sistema

### Salud del Servidor
Endpoint de salud disponible en: `http://localhost:5000/health`

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas Técnicas

- **Primera ejecución**: Puede tomar 2-3 minutos mientras descarga los modelos de IA
- **Modelos utilizados**: 
  - `google/flan-t5-small` (generación de texto)
  - `all-MiniLM-L6-v2` (embeddings semánticos)
- **Almacenamiento**: Los vectores se generan en memoria al iniciar
- **Caché**: Sistema de caché en memoria para respuestas frecuentes

## 🆘 Soporte

Si encuentras problemas:
1. Verifica que Python 3.11+ esté instalado
2. Asegúrate de que el entorno virtual esté activado
3. Reinstala las dependencias con `pip install -r requirements.txt`
4. Verifica que tienes suficiente memoria RAM disponible
5. Revisa los logs en la consola para errores específicos

---

**Desarrollado con ❤️ para Fashion Store**  
*Versión 2.0 - Septiembre 2025*

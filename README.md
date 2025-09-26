# 🏪 Fashion Store - E-commerce con Chat Bot

Un proyecto moderno de e-commerce que combina un landing page profesional con un asistente virtual inteligente.

## 📋 Características

### 🌐 Frontend (Landing Page)
- ✅ Diseño responsive y moderno
- ✅ Catálogo de productos completo  
- ✅ Carrito de compras funcional
- ✅ Blog integrado
- ✅ Páginas de contacto y checkout
- ✅ Optimizado para móviles

### 🤖 Backend (Chat Bot)
- ✅ Asistente virtual inteligente
- ✅ Respuestas contextuales
- ✅ API REST completa
- ✅ Base de datos vectorial
- ✅ Procesamiento de lenguaje natural

## 🚀 Inicio Rápido

### 1️⃣ Configuración Inicial
```bash
# Clonar repositorio
git clone [tu-repo-url]
cd fashion-store

# Configurar entorno (solo la primera vez)
scripts\setup\setup-env.bat
```

### 2️⃣ Desarrollo

#### 🎯 Para trabajar solo en el Frontend:
```bash
scripts\development\start-frontend.bat
# Abre: http://localhost:8000
```

#### 🎯 Para trabajar solo en el Backend:
```bash
scripts\development\start-backend.bat
# Abre: http://localhost:5000
```

#### 🎯 Para desarrollo completo:
```bash
scripts\development\start-dev.bat
# Frontend: http://localhost:8000
# Backend:  http://localhost:5000
```

### 3️⃣ Producción
```bash
scripts\production\start-prod.bat
# Todo integrado en: http://localhost:5000
```

## 📁 Estructura del Proyecto

```
fashion-store/
├── 📁 frontend/                    # Landing Page
│   ├── 📁 pages/                   # Páginas HTML
│   ├── 📁 assets/                  # CSS, JS, imágenes
│   └── 📁 src/                     # Código fuente SASS
├── 📁 backend/                     # Chat Bot API
│   ├── 📁 app/                     # Aplicación principal
│   ├── 📁 config/                  # Configuraciones
│   ├── 📁 data/                    # Datos del bot
│   └── 📁 storage/                 # Base de datos
├── 📁 scripts/                     # Scripts de automatización
│   ├── 📁 development/             # Scripts de desarrollo
│   ├── 📁 production/              # Scripts de producción
│   └── 📁 setup/                   # Scripts de instalación
└── 📁 docs/                        # Documentación
    ├── 📁 setup/                   # Guías de instalación
    ├── 📁 development/             # Guías de desarrollo
    └── 📁 deployment/              # Guías de despliegue
```

## 🛠️ Tecnologías

### Frontend:
- **HTML5, CSS3, JavaScript**
- **Bootstrap 4** - Framework CSS
- **SASS** - Preprocesador CSS
- **jQuery** - Biblioteca JavaScript
- **Font Awesome** - Iconos

### Backend:
- **Python 3.11+** - Lenguaje principal
- **Flask** - Framework web
- **ChromaDB** - Base de datos vectorial
- **Transformers** - Procesamiento de texto
- **NumPy, Pandas** - Análisis de datos

## 📖 Documentación

- [🔧 Instalación y Configuración](docs/setup/)
- [💻 Guía de Desarrollo](docs/development/)
- [🚀 Despliegue en Producción](docs/deployment/)

## 🔧 Comandos Útiles

### Desarrollo del Frontend:
```bash
# Solo servidor estático
scripts\development\start-frontend.bat

# Compilar SASS (si usas)
sass frontend/src/scss/style.scss frontend/assets/css/style.css --watch
```

### Desarrollo del Backend:
```bash
# Solo API del chat bot
scripts\development\start-backend.bat

# Instalar nuevas dependencias
pip install nueva-libreria
pip freeze > backend/requirements.txt
```

### Mantenimiento:
```bash
# Actualizar dependencias
pip install -r backend/requirements.txt --upgrade

# Limpiar cache
python -c "import shutil; shutil.rmtree('backend/app/__pycache__', ignore_errors=True)"
```

## 🧪 Testing

### Frontend:
```bash
# Abrir en navegador
start http://localhost:8000

# Probar páginas específicas
start http://localhost:8000/pages/shop.html
start http://localhost:8000/pages/product-details.html
```

### Backend:
```bash
# Verificar salud del sistema
curl http://localhost:5000/health

# Probar chat bot
curl -X POST http://localhost:5000/bot/chat -H "Content-Type: application/json" -d "{\"mensaje\":\"Hola\"}"
```

## 🤝 Contribuir

1. **Fork** el proyecto
2. **Crear** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear** un Pull Request

## 📝 Changelog

### v2.0.0 - Estructura Reorganizada
- ✅ Separación clara entre frontend y backend
- ✅ Scripts de desarrollo organizados
- ✅ Documentación centralizada
- ✅ Estructura modular y escalable

### v1.0.0 - Versión Inicial
- ✅ Landing page completo
- ✅ Chat bot integrado
- ✅ Servidor unificado

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Si tienes problemas:

1. **Revisa** la [documentación](docs/)
2. **Verifica** que Python 3.11+ esté instalado
3. **Ejecuta** `scripts/setup/setup-env.bat` si es la primera vez
4. **Abre** un issue en GitHub

---

**⭐ ¡No olvides dar una estrella al proyecto si te fue útil!**
@echo off
echo ========================================
echo   FASHION STORE - CHAT INTEGRATION
echo ========================================
echo.

:: Cambiar al directorio del proyecto
cd /d "%~dp0"

:: Verificar si existe el entorno virtual
if not exist "proyecto-bot-main\venv\" (
    echo ERROR: No se encuentra el entorno virtual
    echo Ejecuta primero: python -m venv proyecto-bot-main\venv
    pause
    exit /b 1
)

:: Matar procesos existentes
echo 🔄 Cerrando procesos anteriores...
taskkill /F /IM python.exe 2>nul >nul
taskkill /F /IM "python.exe" 2>nul >nul

:: Esperar un momento
timeout /t 2 /nobreak >nul

:: Activar entorno virtual e instalar dependencias básicas
echo 📦 Preparando entorno...
call proyecto-bot-main\venv\Scripts\activate.bat
pip install flask flask-cors --quiet

:: Iniciar NOVA bot híbrido
echo 🤖 Iniciando NOVA Assistant...
start "NOVA Bot" cmd /k "cd proyecto-bot-main && python nova_bot.py"

:: Esperar a que el bot se inicie
echo ⏳ Esperando que el bot se inicie...
timeout /t 3 /nobreak >nul

:: Verificar que el bot esté funcionando
echo 🔍 Verificando bot...
curl -s http://localhost:5000/health >nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: El bot no responde
    pause
    exit /b 1
)

:: Iniciar servidor web simple para el landing
echo 🌐 Iniciando servidor web...
start "Fashion Store" cmd /k "python -m http.server 8080"

:: Esperar un momento
timeout /t 2 /nobreak >nul

:: Abrir navegador
echo 🚀 Abriendo navegador...
start http://localhost:8080

echo.
echo ✅ Todo listo!
echo 🤖 NOVA Bot: http://localhost:5000
echo 📊 Analytics: http://localhost:5000/api/analytics
echo 🌐 Landing: http://localhost:8080
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
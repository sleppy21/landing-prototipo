@echo off
setlocal enabledelayedexpansion
REM ================================================================
REM Fashion Store - Launcher Optimizado
REM Versión robusta con detección de errores y dependencias
REM ================================================================

title Fashion Store - Launcher Pro
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                Fashion Store - Launcher Pro                  ║
echo ║              Sistema Integrado Optimizado v2.0              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Variables de configuración
set LANDING_PORT=8080
set BOT_PORT=5000
set ERROR_COUNT=0
set BOT_SCRIPT=proyecto-bot-main\app_simple.py

REM ================================================================
REM VERIFICACIÓN DE ESTRUCTURA Y DEPENDENCIAS
REM ================================================================
echo 🔍 Verificando estructura del proyecto...

REM Verificar archivos esenciales
if not exist "index.html" (
    echo ❌ Error: No se encontró index.html
    echo    Asegúrate de estar en la carpeta correcta del proyecto
    set /a ERROR_COUNT+=1
)

if not exist "%BOT_SCRIPT%" (
    echo ❌ Error: No se encontró %BOT_SCRIPT%
    echo    Verifica que la carpeta proyecto-bot-main existe
    set /a ERROR_COUNT+=1
)

if not exist "css\chat-integration.css" (
    echo ❌ Error: No se encontró css\chat-integration.css
    echo    El chat integrado no funcionará correctamente
    set /a ERROR_COUNT+=1
)

if not exist "js\chat-integration.js" (
    echo ❌ Error: No se encontró js\chat-integration.js
    echo    El chat integrado no funcionará correctamente
    set /a ERROR_COUNT+=1
)

if %ERROR_COUNT% gtr 0 (
    echo.
    echo ❌ Se encontraron %ERROR_COUNT% errores críticos
    echo    Corrige estos errores antes de continuar
    pause
    exit /b 1
)

echo ✅ Estructura del proyecto verificada

REM Verificar Python
echo.
echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo    Descarga e instala Python desde https://python.org
    echo    Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
    echo ✅ Python %%v detectado
)

REM Verificar puertos disponibles
echo.
echo 🌐 Verificando puertos...
netstat -an | find ":%LANDING_PORT% " >nul
if %errorlevel% equ 0 (
    echo ⚠️  Puerto %LANDING_PORT% ocupado, cambiando a 8081
    set LANDING_PORT=8081
)

netstat -an | find ":%BOT_PORT% " >nul
if %errorlevel% equ 0 (
    echo ⚠️  Puerto %BOT_PORT% ocupado, cambiando a 5001
    set BOT_PORT=5001
)

echo ✅ Puertos %LANDING_PORT% y %BOT_PORT% disponibles

REM ================================================================
REM CONFIGURACIÓN DEL BOT
REM ================================================================
echo.
echo 🤖 Configurando Bot...

cd proyecto-bot-main

REM Verificar entorno virtual
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Error creando entorno virtual
        cd ..
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
)

REM Activar entorno virtual
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ❌ Error activando entorno virtual
    cd ..
    pause
    exit /b 1
)

REM Verificar/instalar dependencias
if not exist "requirements_simple.txt" (
    echo ❌ Error: No se encontró requirements_simple.txt
    cd ..
    pause
    exit /b 1
)

echo 📦 Verificando dependencias...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Instalando dependencias del bot...
    pip install -r requirements_simple.txt --quiet --disable-pip-version-check
    if %errorlevel% neq 0 (
        echo ❌ Error instalando dependencias
        echo    Verifica tu conexión a internet
        cd ..
        pause
        exit /b 1
    )
    echo ✅ Dependencias instaladas
) else (
    echo ✅ Dependencias ya instaladas
)

cd ..

REM ================================================================
REM INICIO DE SERVICIOS
REM ================================================================
echo.
echo 🚀 Iniciando servicios...

REM Crear directorio de logs si no existe
if not exist "logs" mkdir logs

REM Iniciar bot
echo 🤖 Iniciando Bot en puerto %BOT_PORT%...
cd proyecto-bot-main
start "Fashion Store Bot" /min cmd /c "call venv\Scripts\activate && set PORT=%BOT_PORT% && python app_simple.py > ..\logs\bot.log 2>&1"
cd ..

REM Esperar que el bot inicie
echo ⏳ Esperando que el bot inicie...
set /a "timeout_counter=0"
:wait_bot
timeout /t 1 /nobreak >nul
set /a "timeout_counter+=1"

REM Verificar si el bot está corriendo (método simple)
tasklist /fi "windowtitle eq Fashion Store Bot" 2>nul | find "cmd.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Bot iniciado correctamente
    goto bot_ready
)

if %timeout_counter% geq 10 (
    echo ❌ Timeout: El bot tardó demasiado en iniciar
    echo    Revisa el archivo logs\bot.log para más detalles
    pause
    exit /b 1
)

goto wait_bot

:bot_ready

REM Iniciar servidor web para el landing
echo 🌐 Iniciando Landing en puerto %LANDING_PORT%...
start "Fashion Store Landing" /min cmd /c "python -m http.server %LANDING_PORT% > logs\landing.log 2>&1"

REM Esperar que el landing inicie
timeout /t 3 /nobreak >nul

REM Verificar que el landing esté corriendo
tasklist /fi "windowtitle eq Fashion Store Landing" 2>nul | find "cmd.exe" >nul
if %errorlevel% neq 0 (
    echo ❌ Error: El landing no se inició correctamente
    echo    Revisa el archivo logs\landing.log para más detalles
    pause
    exit /b 1
)

echo ✅ Landing iniciado correctamente

REM ================================================================
REM VERIFICACIÓN FINAL Y APERTURA
REM ================================================================
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Servicios Iniciados                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🎉 ¡Todo funcionando correctamente!
echo.
echo 📍 URLs disponibles:
echo    🌐 Landing con chat: http://localhost:%LANDING_PORT%
echo    🤖 Bot directo:      http://localhost:%BOT_PORT%
echo.
echo 💬 Cómo usar el chat integrado:
echo    1. Ve al landing en tu navegador
echo    2. Busca el botón flotante en la esquina inferior derecha
echo    3. Haz clic para abrir el chat
echo    4. ¡Chatea con el asistente virtual!
echo.
echo 📋 Logs disponibles en:
echo    • logs\bot.log - Log del bot
echo    • logs\landing.log - Log del servidor web
echo.

REM Abrir navegador automáticamente
echo 🌍 Abriendo navegador...
start http://localhost:%LANDING_PORT%

echo.
echo ❓ Opciones:
echo    • Presiona ENTER para ver el estado de los servicios
echo    • Presiona Ctrl+C para detener todo
echo.
pause

REM ================================================================
REM MONITOREO SIMPLE
REM ================================================================
:monitor
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                   Estado de Servicios                        ║
echo ║                  %date% %time%                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar bot
tasklist /fi "windowtitle eq Fashion Store Bot" 2>nul | find "cmd.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Bot: FUNCIONANDO - Puerto %BOT_PORT%
) else (
    echo ❌ Bot: DETENIDO
)

REM Verificar landing
tasklist /fi "windowtitle eq Fashion Store Landing" 2>nul | find "cmd.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Landing: FUNCIONANDO - Puerto %LANDING_PORT%
) else (
    echo ❌ Landing: DETENIDO
)

echo.
echo 📊 URLs activas:
echo    🌐 http://localhost:%LANDING_PORT%
echo    🤖 http://localhost:%BOT_PORT%
echo.
echo 💡 Opciones:
echo    • Presiona ENTER para actualizar estado
echo    • Presiona Ctrl+C para detener servicios
echo    • Cierra esta ventana para detener todo
echo.

pause >nul
goto monitor
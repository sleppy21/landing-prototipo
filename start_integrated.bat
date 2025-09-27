@echo off
echo ========================================
echo  FASHION STORE - SERVIDOR INTEGRADO
echo ========================================
echo.
echo [INFO] Iniciando servidor integrado...
echo [INFO] Landing Page + Chat Bot en un solo servidor
echo.

REM Cambiar al directorio del proyecto bot
cd /d "%~dp0proyecto-bot"

REM Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado
    echo [INFO] Ejecuta primero: install_optimized.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar servidor integrado
echo [INFO] Ejecutando servidor integrado...
echo [INFO] Accede a: http://localhost:5000
echo [INFO] Presiona Ctrl+C para detener
echo.
python app_integrated.py

REM Si hay error, mostrar mensaje
if errorlevel 1 (
    echo.
    echo [ERROR] Error al ejecutar el servidor
    echo [INFO] Verifica que las dependencias estén instaladas
    pause
)
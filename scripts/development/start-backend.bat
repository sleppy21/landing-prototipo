@echo off
echo ========================================
echo   BACKEND DEVELOPMENT - Fashion Store
echo ========================================
echo.
echo [INFO] Iniciando servidor de desarrollo para el Backend...
echo [INFO] Solo el Chat Bot API en puerto 5000
echo.

cd /d "%~dp0..\..\backend"

REM Verificar si existe el entorno virtual
if not exist "..\proyecto-bot\venv\Scripts\activate.bat" (
    echo [ERROR] No se encuentra el entorno virtual
    echo [INFO] Ejecuta primero: setup-env.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
call "..\proyecto-bot\venv\Scripts\activate.bat"

echo [INFO] Servidor iniciado en: http://localhost:5000
echo [INFO] Solo APIs del Chat Bot disponibles
echo.

REM Ejecutar servidor del backend
python app\main.py

echo.
echo [INFO] Para detener: Ctrl+C
pause
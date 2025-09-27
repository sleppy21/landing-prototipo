@echo off
echo ========================================
echo   PRODUCCIÓN - Fashion Store
echo ========================================
echo.
echo [INFO] Iniciando servidor de producción...
echo [INFO] Todo integrado en puerto 5000
echo.

cd /d "%~dp0..\.."

REM Verificar si existe el entorno virtual
if not exist "proyecto-bot\venv\Scripts\activate.bat" (
    echo [ERROR] No se encuentra el entorno virtual
    echo [INFO] Ejecuta primero: scripts\setup\setup-env.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
call "proyecto-bot\venv\Scripts\activate.bat"

echo [INFO] ✅ Servidor integrado: http://localhost:5000
echo [INFO] ✅ Landing + Chat Bot en un solo servidor
echo.

REM Ejecutar servidor integrado desde backend
cd backend
python app\main.py --production

echo.
echo [INFO] Para detener: Ctrl+C
pause
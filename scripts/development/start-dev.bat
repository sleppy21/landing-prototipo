@echo off
echo ========================================
echo  DESARROLLO COMPLETO - Fashion Store
echo ========================================
echo.
echo [INFO] Iniciando desarrollo completo...
echo [INFO] Frontend (puerto 8000) + Backend (puerto 5000)
echo.

cd /d "%~dp0..\.."

REM Verificar si existe el entorno virtual
if not exist "proyecto-bot\venv\Scripts\activate.bat" (
    echo [ERROR] No se encuentra el entorno virtual
    echo [INFO] Ejecuta primero: scripts\setup\setup-env.bat
    pause
    exit /b 1
)

echo [INFO] ✅ Frontend: http://localhost:8000 (Archivos estáticos)
echo [INFO] ✅ Backend:  http://localhost:5000 (Chat Bot API)
echo.

REM Abrir Frontend en una nueva ventana
start "Frontend Server" cmd /k "cd frontend && python -m http.server 8000"

REM Esperar un poco y luego iniciar Backend
timeout /t 3 /nobreak >nul

REM Activar entorno virtual e iniciar Backend
call "proyecto-bot\venv\Scripts\activate.bat"
cd backend
python app\main.py

echo.
echo [INFO] Para detener: Cerrar ambas ventanas
pause
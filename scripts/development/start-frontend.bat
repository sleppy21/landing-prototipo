@echo off
echo ========================================
echo   FRONTEND DEVELOPMENT - Fashion Store
echo ========================================
echo.
echo [INFO] Iniciando servidor de desarrollo para el Frontend...
echo [INFO] Solo sirve archivos estáticos del landing page
echo.

cd /d "%~dp0..\.."
echo [INFO] Servidor iniciado en: http://localhost:8000

REM Usar Python para servir archivos estáticos desde frontend
cd frontend
python -m http.server 8000

echo.
echo [INFO] Para detener: Ctrl+C
pause
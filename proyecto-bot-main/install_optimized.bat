






@echo off
echo ========================================
echo  INSTALACION OPTIMIZADA - BOT TIENDA
echo ========================================

REM Crear directorio de caché si no existe
if not exist ".pip-cache" mkdir .pip-cache
if not exist ".pip-cache\wheels" mkdir .pip-cache\wheels

echo [1/3] Creando/activando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo [2/3] Actualizando pip e instalando dependencias...
python -m pip install --upgrade pip --cache-dir .pip-cache
python -m pip install -r requirements.txt --cache-dir .pip-cache --find-links .pip-cache\wheels
python -m pip wheel -r requirements.txt --wheel-dir .pip-cache\wheels --cache-dir .pip-cache --find-links .pip-cache\wheels

echo [3/3] Instalación completada y entorno listo.
echo Puedes iniciar el bot ejecutando:
echo   start.bat
echo O manualmente:
echo   venv\Scripts\activate
echo   python main.py
echo.
pause
@echo off
REM ================================================================
REM Fashion Store - Launcher Optimizado v3.0
REM Versión simplificada y más robusta
REM ================================================================

title Fashion Store - Launcher Pro
color 0F
chcp 65001 >nul 2>&1

echo.
echo ================================================================
echo                Fashion Store - Launcher Pro
echo              Sistema Integrado Optimizado v3.0
echo ================================================================
echo.

REM Variables de configuración
set LANDING_PORT=8080
set BOT_PORT=5000
set ERROR_COUNT=0
set BOT_SCRIPT=proyecto-bot-main\app_simple.py

echo Verificando estructura del proyecto...

if not exist "index.html" (
    echo [ERROR] No se encontro index.html
    echo         Asegurate de estar en la carpeta correcta del proyecto
    set /a ERROR_COUNT+=1
)

if not exist "%BOT_SCRIPT%" (
    echo [ERROR] No se encontro %BOT_SCRIPT%
    echo         Verifica que la carpeta proyecto-bot-main exista
    set /a ERROR_COUNT+=1
)

if %ERROR_COUNT% gtr 0 (
    echo.
    echo [ERROR] Se encontraron %ERROR_COUNT% errores criticos
    echo         Corrige estos errores antes de continuar
    pause
    exit /b 1
)

echo [OK] Estructura del proyecto verificada

echo.
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo         Descarga e instala Python desde https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
    echo [OK] Python %%v detectado
)

echo.
echo Verificando puertos...
netstat -an | find ":%LANDING_PORT%" >nul
if %errorlevel% equ 0 (
    echo [WARN] Puerto %LANDING_PORT% ocupado, cambiando a 8081
    set LANDING_PORT=8081
)

netstat -an | find ":%BOT_PORT%" >nul
if %errorlevel% equ 0 (
    echo [WARN] Puerto %BOT_PORT% ocupado, cambiando a 5001
    set BOT_PORT=5001
)

echo [OK] Puertos verificados: Landing=%LANDING_PORT%, Bot=%BOT_PORT%

echo.
echo Configurando Bot...

if not exist "proyecto-bot-main" (
    echo [ERROR] No existe la carpeta proyecto-bot-main
    pause
    exit /b 1
)

cd proyecto-bot-main

if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Error creando entorno virtual
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
)

if not exist "requirements_simple.txt" (
    echo [ERROR] No se encontro requirements_simple.txt
    cd ..
    pause
    exit /b 1
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Error activando entorno virtual
    cd ..
    pause
    exit /b 1
)

echo Verificando dependencias...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias del bot...
    pip install -r requirements_simple.txt --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] Error instalando dependencias
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
) else (
    echo [OK] Dependencias ya instaladas
)

cd ..

echo.
echo Creando directorio de logs...
if not exist "logs" mkdir "logs" >nul 2>&1

echo.
echo Iniciando servicios...

REM Iniciar Bot
echo [INFO] Iniciando Bot en puerto %BOT_PORT%...
cd proyecto-bot-main
start "Fashion Store Bot" /min cmd /c "call venv\Scripts\activate.bat && set PORT=%BOT_PORT% && python app_simple.py > ..\logs\bot.log 2>&1"
cd ..

REM Esperar que el bot inicie
echo Esperando que el bot inicie...
timeout /t 5 /nobreak >nul

REM Verificar que el bot este corriendo
for /L %%i in (1,1,10) do (
    netstat -an | find ":%BOT_PORT%" >nul
    if %errorlevel% equ 0 (
        echo [OK] Bot iniciado correctamente en puerto %BOT_PORT%
        goto bot_ready
    )
    echo Esperando... (%%i/10)
    timeout /t 2 /nobreak >nul
)

echo [ERROR] El bot no se inicio correctamente
echo         Revisa el archivo logs\bot.log para mas detalles
pause
exit /b 1

:bot_ready

REM Iniciar Landing Page
echo [INFO] Iniciando Landing Page en puerto %LANDING_PORT%...
start "Fashion Store Landing" /min cmd /c "python -m http.server %LANDING_PORT% > logs\landing.log 2>&1"

REM Esperar que el landing inicie
echo Esperando que el landing page inicie...
timeout /t 3 /nobreak >nul

REM Verificar que el landing este corriendo
for /L %%i in (1,1,5) do (
    netstat -an | find ":%LANDING_PORT%" >nul
    if %errorlevel% equ 0 (
        echo [OK] Landing page iniciado correctamente en puerto %LANDING_PORT%
        goto landing_ready
    )
    echo Esperando... (%%i/5)
    timeout /t 2 /nobreak >nul
)

echo [ERROR] El landing page no se inicio correctamente
echo         Revisa el archivo logs\landing.log para mas detalles
pause
exit /b 1

:landing_ready

echo.
echo ================================================================
echo                    Servicios Iniciados
echo ================================================================
echo.
echo Todo funcionando correctamente!
echo.
echo URLs disponibles:
echo    Landing Page: http://localhost:%LANDING_PORT%
echo    Bot API:      http://localhost:%BOT_PORT%
echo.
echo Logs disponibles:
echo    Bot:     logs\bot.log
echo    Landing: logs\landing.log
echo.

REM Abrir navegador
echo Abriendo navegador...
start http://localhost:%LANDING_PORT%
timeout /t 2 /nobreak >nul

echo.
echo Presiona cualquier tecla para ver el monitor de estado...
pause >nul

:monitor
cls
echo.
echo ================================================================
echo                   Estado de Servicios
echo                   %date% %time%
echo ================================================================
echo.

REM Verificar estado del bot
netstat -an | find ":%BOT_PORT%" >nul
if %errorlevel% equ 0 (
    echo [OK] Bot: FUNCIONANDO - Puerto %BOT_PORT%
) else (
    echo [ERROR] Bot: DETENIDO
)

REM Verificar estado del landing
netstat -an | find ":%LANDING_PORT%" >nul
if %errorlevel% equ 0 (
    echo [OK] Landing: FUNCIONANDO - Puerto %LANDING_PORT%
) else (
    echo [ERROR] Landing: DETENIDO
)

echo.
echo URLs activas:
echo    Landing: http://localhost:%LANDING_PORT%
echo    Bot API: http://localhost:%BOT_PORT%
echo.
echo Opciones:
echo    [R] - Recargar estado
echo    [O] - Abrir pagina en navegador
echo    [L] - Ver logs del bot
echo    [Q] - Salir (los servicios seguiran corriendo)
echo    [S] - Detener todos los servicios y salir
echo.

choice /c ROLQS /n /m "Selecciona una opcion: "

if errorlevel 5 goto stop_services
if errorlevel 4 goto exit_launcher
if errorlevel 3 goto show_logs
if errorlevel 2 goto open_browser
if errorlevel 1 goto monitor

:open_browser
start http://localhost:%LANDING_PORT%
goto monitor

:show_logs
echo.
echo Mostrando ultimas lineas del log del bot...
if exist "logs\bot.log" (
    more +10 "logs\bot.log"
) else (
    echo No se encontro el archivo de log del bot
)
echo.
pause
goto monitor

:stop_services
echo.
echo Deteniendo servicios...
taskkill /f /fi "windowtitle eq Fashion Store Bot" >nul 2>&1
taskkill /f /fi "windowtitle eq Fashion Store Landing" >nul 2>&1
echo [OK] Servicios detenidos
pause
exit

:exit_launcher
echo.
echo Los servicios seguiran corriendo en segundo plano
echo Para detenerlos manualmente, cierra las ventanas correspondientes
echo o ejecuta este script y selecciona la opcion [S]
pause
exit

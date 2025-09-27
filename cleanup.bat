@echo off
REM ================================================================
REM Fashion Store - Script de Limpieza
REM Elimina archivos innecesarios y optimiza el proyecto
REM ================================================================

title Fashion Store - Cleanup
color 0E

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║               Fashion Store - Limpieza                       ║
echo ║             Optimización del Proyecto v1.0                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🧹 Iniciando limpieza del proyecto...
echo.

REM Crear backup si no existe
if not exist "backup" (
    echo 📦 Creando backup de seguridad...
    mkdir backup
    echo ✅ Carpeta backup creada
)

REM Archivos innecesarios comunes
set "CLEANUP_TARGETS=*.tmp *.bak *.log *.cache Thumbs.db .DS_Store"

echo 🗑️  Eliminando archivos temporales...
for %%i in (%CLEANUP_TARGETS%) do (
    if exist "%%i" (
        del /q "%%i" 2>nul
        echo    • Eliminado: %%i
    )
)

REM Limpiar carpeta Source (archivos ZIP originales)
echo.
echo 📁 Analizando carpeta Source...
if exist "Source" (
    echo    • Encontrados archivos fuente originales
    echo    • Estos archivos ZIP pueden eliminarse ya que las librerías están integradas
    echo.
    set /p "CLEAN_SOURCE=¿Eliminar archivos ZIP de Source? (s/N): "
    if /i "!CLEAN_SOURCE!"=="s" (
        echo 🗑️  Eliminando archivos ZIP de Source...
        del /q "Source\*.zip" 2>nul
        echo ✅ Archivos ZIP eliminados
    ) else (
        echo ℹ️  Archivos ZIP conservados
    )
) else (
    echo    • Carpeta Source no encontrada
)

REM Limpiar logs antiguos si existen
echo.
echo 📋 Limpiando logs antiguos...
if exist "logs" (
    for %%f in (logs\*.log) do (
        if exist "%%f" (
            echo    • Archivando: %%f
            move "%%f" "backup\" >nul 2>&1
        )
    )
    echo ✅ Logs archivados en backup
) else (
    echo    • No hay logs que limpiar
)

REM Limpiar caché del bot si existe
echo.
echo 🤖 Limpiando caché del bot...
if exist "proyecto-bot-main\chroma_db" (
    echo    • Encontrado caché de embeddings
    set /p "CLEAN_CACHE=¿Limpiar caché de embeddings? (s/N): "
    if /i "!CLEAN_CACHE!"=="s" (
        rmdir /s /q "proyecto-bot-main\chroma_db" 2>nul
        echo ✅ Caché de embeddings limpio
    ) else (
        echo ℹ️  Caché conservado
    )
) else (
    echo    • No hay caché que limpiar
)

REM Limpiar __pycache__ si existe
echo.
echo 🐍 Limpiando caché de Python...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
        echo    • Eliminado: %%d
    )
)

REM Eliminar archivos .pyc
for /r . %%f in (*.pyc) do (
    if exist "%%f" (
        del /q "%%f" 2>nul
        echo    • Eliminado: %%f
    )
)

echo ✅ Caché de Python limpio

REM Optimizar imágenes (solo reportar tamaños)
echo.
echo 🖼️  Analizando imágenes...
set /a "img_count=0"
set /a "img_size=0"
for /r img %%f in (*.jpg *.png *.gif) do (
    set /a "img_count+=1"
    for %%s in ("%%f") do set /a "img_size+=%%~zs"
)

if %img_count% gtr 0 (
    set /a "img_size_mb=img_size/1024/1024"
    echo    • Encontradas %img_count% imágenes (~!img_size_mb! MB)
    echo    • Considera optimizar imágenes grandes para mejor rendimiento
) else (
    echo    • No hay imágenes que analizar
)

REM Crear archivo .gitignore si no existe
echo.
echo 📝 Configurando .gitignore...
if not exist ".gitignore" (
    echo # Fashion Store - Archivos a ignorar > .gitignore
    echo. >> .gitignore
    echo # Logs >> .gitignore
    echo logs/ >> .gitignore
    echo *.log >> .gitignore
    echo. >> .gitignore
    echo # Python >> .gitignore
    echo __pycache__/ >> .gitignore
    echo *.pyc >> .gitignore
    echo *.pyo >> .gitignore
    echo venv/ >> .gitignore
    echo .env >> .gitignore
    echo. >> .gitignore
    echo # Caché del bot >> .gitignore
    echo proyecto-bot-main/chroma_db/ >> .gitignore
    echo. >> .gitignore
    echo # Temporales >> .gitignore
    echo *.tmp >> .gitignore
    echo *.bak >> .gitignore
    echo Thumbs.db >> .gitignore
    echo .DS_Store >> .gitignore
    echo. >> .gitignore
    echo # Backup >> .gitignore
    echo backup/ >> .gitignore
    
    echo ✅ .gitignore creado
) else (
    echo    • .gitignore ya existe
)

REM Resumen de limpieza
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Limpieza Completada                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ Archivos temporales eliminados
echo ✅ Logs archivados en backup
echo ✅ Caché de Python limpio
echo ✅ .gitignore configurado
echo ℹ️  Backup disponible en carpeta 'backup'
echo.

REM Mostrar tamaño final del proyecto
echo 📊 Información del proyecto:
for /f "tokens=3" %%a in ('dir /s /-c ^| find "bytes"') do set "project_size=%%a"
echo    • Tamaño total del proyecto: %project_size% bytes
echo.

echo 💡 Recomendaciones:
echo    • Ejecuta esta limpieza periódicamente
echo    • Considera comprimir imágenes grandes
echo    • Mantén el backup actualizado
echo    • Revisa logs regularmente
echo.

echo 🎉 ¡Proyecto optimizado correctamente!
echo.
pause
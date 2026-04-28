@echo off
chcp 65001 >nul
title Instalacion del Entorno InfluxDB + Grafana

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   INSTALACION AUTOMATICA - InfluxDB + Grafana   ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: ── Verificar Docker ──────────────────────────────────
echo [1/4] Verificando que Docker este instalado...
docker --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Docker no esta instalado o no esta corriendo.
    echo.
    echo  Por favor:
    echo    1. Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop/
    echo    2. Instalalo y reinicia el computador
    echo    3. Asegurate de que Docker Desktop este abierto (icono en la barra de tareas)
    echo    4. Vuelve a ejecutar este archivo
    echo.
    pause
    exit /b 1
)
echo  OK - Docker encontrado.

:: ── Verificar Python ──────────────────────────────────
echo.
echo [2/4] Verificando que Python este instalado...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Python no esta instalado.
    echo.
    echo  Por favor:
    echo    1. Descarga Python desde: https://www.python.org/downloads/
    echo    2. Durante la instalacion, marca la opcion "Add Python to PATH"
    echo    3. Reinicia esta ventana y vuelve a ejecutar
    echo.
    pause
    exit /b 1
)
echo  OK - Python encontrado.

:: ── Instalar dependencias Python ──────────────────────
echo.
echo [3/4] Instalando librerias de Python necesarias...
pip install -r requirements.txt --quiet
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Fallo la instalacion de librerias Python.
    echo  Intenta ejecutar manualmente: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo  OK - Librerias instaladas correctamente.

:: ── Iniciar los servicios con Docker Compose ──────────
echo.
echo [4/4] Iniciando InfluxDB y Grafana con Docker...
docker compose up -d
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: No se pudieron iniciar los servicios.
    echo  Asegurate de que Docker Desktop este abierto e intenta de nuevo.
    echo.
    pause
    exit /b 1
)

:: ── Esperar a que los servicios esten listos ──────────
echo.
echo  Esperando a que los servicios esten listos...
timeout /t 15 /nobreak >nul

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║              INSTALACION EXITOSA                ║
echo ╠══════════════════════════════════════════════════╣
echo ║                                                  ║
echo ║   InfluxDB:  http://localhost:8086               ║
echo ║   Grafana:   http://localhost:3000               ║
echo ║                                                  ║
echo ║   Usuario/clave: ver archivo .env                ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo  Para subir un CSV:
echo    python upload_csv.py ruta\al\archivo.csv
echo.
echo  Para apagar los servicios:
echo    Ejecuta stop.bat
echo.
pause

@echo off
chcp 65001 >nul
title Instalacion del Entorno InfluxDB + Grafana

echo.
echo  ██╗██████╗  ██████╗     ██╗  ██╗    ██╗   ██╗████████╗██████╗
echo  ██║██╔══██╗██╔════╝     ╚██╗██╔╝    ██║   ██║╚══██╔══╝██╔══██╗
echo  ██║██║  ██║██║           ╚███╔╝     ██║   ██║   ██║   ██████╔╝
echo  ██║██║  ██║██║           ██╔██╗     ██║   ██║   ██║   ██╔═══╝
echo  ██║██████╔╝╚██████╗     ██╔╝ ██╗    ╚██████╔╝   ██║   ██║
echo  ╚═╝╚═════╝  ╚═════╝     ╚═╝  ╚═╝     ╚═════╝    ╚═╝   ╚═╝
echo.
echo                  Diplomado de Ciencia de Datos
echo  ====================================================================
echo         Instalacion automatica  --  InfluxDB + Grafana
echo  ====================================================================
echo.

:: Verificar Docker
echo  [1/4]  Verificando Docker...
where docker >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo +------------------------------------------------------+
    echo ^|  ERROR  Docker no fue encontrado en el sistema       ^|
    echo +------------------------------------------------------^|
    echo ^|  1. Descarga Docker Desktop:                         ^|
    echo ^|     https://www.docker.com/products/docker-desktop/  ^|
    echo ^|  2. Instala y abre Docker Desktop                    ^|
    echo ^|  3. Espera a que diga "Engine running"               ^|
    echo ^|  4. Vuelve a ejecutar este archivo                   ^|
    echo +------------------------------------------------------+
    echo.
    pause
    exit /b 1
)

docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo +------------------------------------------------------+
    echo ^|  ERROR  Docker Desktop no esta listo                 ^|
    echo +------------------------------------------------------^|
    echo ^|  1. Abre Docker Desktop desde el menu Inicio         ^|
    echo ^|  2. Espera a que diga "Engine running"               ^|
    echo ^|  3. Vuelve a ejecutar este archivo                   ^|
    echo +------------------------------------------------------+
    echo.
    pause
    exit /b 1
)
echo         OK  Docker listo.

:: Verificar Python
echo.
echo  [2/4]  Verificando Python...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo +------------------------------------------------------+
    echo ^|  ERROR  Python no esta instalado                     ^|
    echo +------------------------------------------------------^|
    echo ^|  1. Descarga Python:                                 ^|
    echo ^|     https://www.python.org/downloads/                ^|
    echo ^|  2. Marca "Add Python to PATH" en la instalacion     ^|
    echo ^|  3. Reinicia esta ventana y vuelve a ejecutar        ^|
    echo +------------------------------------------------------+
    echo.
    pause
    exit /b 1
)
echo         OK  Python listo.

:: Instalar dependencias Python
echo.
echo  [3/4]  Instalando librerias de Python...
pip install -r requirements.txt --quiet
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo +------------------------------------------------------+
    echo ^|  ERROR  No se pudieron instalar las librerias        ^|
    echo +------------------------------------------------------^|
    echo ^|  Ejecuta manualmente:                                ^|
    echo ^|    pip install -r requirements.txt                   ^|
    echo +------------------------------------------------------+
    echo.
    pause
    exit /b 1
)
echo         OK  Librerias instaladas.

:: Iniciar los servicios con Docker Compose
echo.
echo  [4/4]  Iniciando InfluxDB y Grafana...
docker compose up -d
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo +------------------------------------------------------+
    echo ^|  ERROR  No se pudieron iniciar los servicios         ^|
    echo +------------------------------------------------------^|
    echo ^|  Asegurate de que Docker Desktop este abierto        ^|
    echo ^|  e intentalo de nuevo.                               ^|
    echo +------------------------------------------------------+
    echo.
    pause
    exit /b 1
)

:: Esperar a que los servicios esten listos
echo.
echo         Esperando a que los servicios esten listos...
timeout /t 15 /nobreak >nul

echo.
echo  ====================================================================
echo         INSTALACION COMPLETADA
echo  ====================================================================
echo.
echo    InfluxDB  --^>  http://localhost:8086
echo    Grafana   --^>  http://localhost:3000
echo.
echo    Credenciales: ver archivo .env
echo.
echo  --------------------------------------------------------------------
echo.
echo    Subir CSV:   python upload_csv.py ruta\archivo.csv
echo    Apagar:      ejecuta stop.bat
echo.
echo  ====================================================================
echo.
pause
@echo off
chcp 65001 >nul
title InfluxDB + Grafana

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
echo.

echo  Iniciando servicios...
echo.
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

echo.
echo  ====================================================================
echo         SERVICIOS EN LINEA
echo  ====================================================================
echo.
echo    InfluxDB  --^>  http://localhost:8086
echo    Grafana   --^>  http://localhost:3000
echo.
echo  ====================================================================
echo.
pause
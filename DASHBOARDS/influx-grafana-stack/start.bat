@echo off
chcp 65001 >nul
title Iniciar InfluxDB + Grafana

echo.
echo  Iniciando InfluxDB y Grafana...
docker compose up -d
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Asegurate de que Docker Desktop este abierto e intenta de nuevo.
    pause
    exit /b 1
)
echo.
echo  Servicios iniciados:
echo    InfluxDB  ->  http://localhost:8086
echo    Grafana   ->  http://localhost:3000
echo.
pause

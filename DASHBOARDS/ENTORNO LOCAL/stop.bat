@echo off
chcp 65001 >nul
title Apagar InfluxDB + Grafana

echo.
echo  Apagando los servicios...
docker compose down
echo.
echo  Servicios detenidos. Los datos siguen guardados.
echo  Para volver a iniciar, ejecuta start.bat
echo.
pause

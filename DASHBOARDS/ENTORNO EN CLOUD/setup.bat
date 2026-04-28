@echo off
chcp 65001 >nul
title Instalacion - Cargador CSV a InfluxDB Cloud

echo.
echo ====================================================
echo    INSTALACION - Cargador CSV a InfluxDB Cloud
echo ====================================================
echo.

echo [1/2] Verificando que Python este instalado...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Python no esta instalado.
    echo.
    echo  Por favor:
    echo    1. Descarga Python desde: https://www.python.org/downloads/
    echo    2. Durante la instalacion, marca la opcion "Add Python to PATH"
    echo    3. Reinicia esta ventana y vuelve a ejecutar setup.bat
    echo.
    pause
    exit /b 1
)
echo  OK - Python encontrado.

echo.
echo [2/2] Instalando librerias necesarias...
pip install -r requirements.txt --quiet
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Fallo la instalacion de librerias.
    echo  Intenta ejecutar manualmente: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo  OK - Librerias instaladas correctamente.

echo.
echo ====================================================
echo             INSTALACION EXITOSA
echo ====================================================
echo.
echo  Siguiente paso:
echo    1. Edita config.yml con tus datos de
echo       InfluxDB Cloud (URL, token, org, bucket)
echo    2. Corre: python upload_csv.py archivo.csv
echo.
echo  Lee el README.md para la guia completa.
echo ====================================================
echo.
pause

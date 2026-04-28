# Entorno InfluxDB + Grafana con carga de CSV

Este paquete levanta un entorno completo de almacenamiento y visualización de datos en tu computador Windows, sin necesidad de conocimientos técnicos avanzados.

---

## ¿Qué incluye?

| Componente | Descripción | Acceso |
|------------|-------------|--------|
| **InfluxDB 2.x** | Base de datos de series de tiempo | http://localhost:8086 |
| **Grafana** | Dashboards y visualizaciones | http://localhost:3000 |
| **upload_csv.py** | Script para subir archivos CSV grandes | Línea de comandos |

---

## Requisitos previos

Antes de instalar, asegúrate de tener:

1. **Docker Desktop** — descárgalo en https://www.docker.com/products/docker-desktop/
   - Instálalo y ábrelo (debe aparecer su ícono en la barra de tareas de Windows)

2. **Python 3.8 o superior** — descárgalo en https://www.python.org/downloads/
   - Durante la instalación, **marca la opción "Add Python to PATH"**

---

## Instalación (primera vez)

1. Descarga y descomprime esta carpeta en tu computador
2. Abre la carpeta y haz **doble clic en `setup.bat`**
3. El script verificará los requisitos e instalará todo automáticamente
4. Al finalizar verás los enlaces de acceso a InfluxDB y Grafana

> Si Windows muestra una advertencia de seguridad, haz clic en **"Más información" → "Ejecutar de todas formas"**

---

## Uso diario

### Iniciar / apagar los servicios

- **Iniciar:** doble clic en `start.bat`
- **Apagar:** doble clic en `stop.bat`

Los datos **no se pierden** al apagar — quedan guardados en volúmenes de Docker.

---

## Subir un archivo CSV

### Paso 1 — Configura `config.yml`

Abre el archivo `config.yml` con el Bloc de notas y ajusta:

```yaml
influxdb:
  token: mi-token-super-secreto-cambiame-123456  # igual que en .env
  org: miorganizacion                             # igual que en .env
  bucket: misdatos                                # igual que en .env

csv:
  measurement: nombre_de_tu_tabla   # cómo quieres llamar a estos datos en InfluxDB
  time_column: "fecha"              # nombre de la columna con fecha/hora (o "" si no hay)
  time_format: "%Y-%m-%d %H:%M:%S" # formato de la fecha
  separator: ","                    # separador del CSV (coma, punto y coma, etc.)
  encoding: "utf-8"                 # prueba latin-1 si ves caracteres raros
  chunk_size: 50000                 # filas por lote (baja este número si tu PC tiene poca RAM)
```

### Paso 2 — Ejecuta el script

Abre una ventana de **Símbolo del sistema** (cmd) en la carpeta del proyecto:

```
python upload_csv.py ruta\al\archivo.csv
```

O simplemente ejecuta `python upload_csv.py` y el script te pedirá la ruta del archivo.

### Qué hace el script

1. Muestra una previsualización de las columnas del CSV
2. Detecta automáticamente qué columnas son datos numéricos (fields) y cuáles son categorías (tags)
3. Te pide confirmación antes de comenzar
4. Carga el archivo en lotes con una barra de progreso
5. Muestra un resumen al terminar

---

## Acceso a Grafana

1. Abre http://localhost:3000 en tu navegador
2. Usuario y contraseña: los que configuraste en `.env` (por defecto `admin` / `grafana123`)
3. InfluxDB ya estará configurado como fuente de datos automáticamente
4. Crea un nuevo dashboard → Add panel → selecciona "InfluxDB" y escribe tu query en Flux

**Ejemplo de query Flux básica:**
```flux
from(bucket: "misdatos")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "nombre_de_tu_tabla")
```

---

## Acceso a InfluxDB

1. Abre http://localhost:8086 en tu navegador
2. Usuario y contraseña: los que configuraste en `.env` (por defecto `admin` / `password123`)
3. Desde aquí puedes explorar los datos con el Data Explorer

---

## Cambiar contraseñas y credenciales

Edita el archivo `.env` con el Bloc de notas:

```
INFLUXDB_ADMIN_USER=admin
INFLUXDB_ADMIN_PASSWORD=TuNuevaContraseña
INFLUXDB_ORG=miorganizacion
INFLUXDB_BUCKET=misdatos
INFLUXDB_TOKEN=un-token-largo-y-seguro-que-nadie-adivine

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=TuOtraContraseña
```

> Después de cambiar el `.env`, ejecuta `stop.bat` y luego `setup.bat` para aplicar los cambios.  
> **IMPORTANTE:** Si ya tienes datos guardados y cambias el token, debes actualizar también `config.yml`.

---

## Consejos para archivos CSV muy grandes

- Reduce `chunk_size` en `config.yml` si ves errores de memoria (prueba con 10000)
- Para archivos de más de 1 GB, cierra otras aplicaciones mientras se carga
- El script muestra velocidad de carga en filas/segundo; velocidades normales: 10.000–100.000 filas/seg

---

## Solución de problemas frecuentes

| Problema | Solución |
|----------|----------|
| "Docker no está instalado" | Instala Docker Desktop y ábrelo antes de correr setup.bat |
| "Python no está instalado" | Instala Python y marca "Add to PATH" durante la instalación |
| Error de conexión en upload_csv.py | Verifica que start.bat haya corrido y que el token en config.yml coincida con .env |
| Caracteres raros en el CSV | Cambia `encoding: "latin-1"` en config.yml |
| Grafana no muestra datos | Verifica el nombre del measurement y el rango de fechas en el dashboard |

---

## Estructura de archivos

```
influx-grafana-stack/
├── docker-compose.yml          # Define los servicios Docker
├── .env                        # Contraseñas y configuración de conexión
├── config.yml                  # Configuración de carga de CSV
├── upload_csv.py               # Script de carga de CSV
├── requirements.txt            # Librerías Python necesarias
├── setup.bat                   # Instalación con un clic (ejecutar primero)
├── start.bat                   # Iniciar servicios
├── stop.bat                    # Apagar servicios
└── grafana/
    └── provisioning/
        └── datasources/
            └── influxdb.yml    # Conexión automática Grafana → InfluxDB
```

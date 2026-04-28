# Cargador CSV → InfluxDB Cloud + Grafana Cloud

Sube archivos CSV (incluso muy pesados) a InfluxDB Cloud y visualiza los datos en Grafana Cloud — todo accesible desde el navegador, desde cualquier lugar, sin instalar servidores.

---

## ¿Qué necesitas?

1. **Python 3.8+** instalado en tu PC → https://www.python.org/downloads/  
   *(marca "Add Python to PATH" durante la instalación)*
2. Una cuenta gratuita en **InfluxDB Cloud** → https://cloud2.influxdata.com
3. Una cuenta gratuita en **Grafana Cloud** → https://grafana.com

No necesitas Docker ni ningún servidor.

---

## PASO 1 — Crear cuenta en InfluxDB Cloud

1. Ve a https://cloud2.influxdata.com y haz clic en **"Get Started Free"**
2. Regístrate con tu email
3. Elige una región (ej: **US East** o **EU Frankfurt**) — esta define tu URL
4. Elige el plan **Free**

### Crear un bucket

1. En el menú izquierdo → **Load Data → Buckets**
2. Clic en **"+ Create Bucket"**
3. Dale un nombre (ej: `misdatos`) y haz clic en **Create**

### Obtener tu API Token

1. En el menú izquierdo → **Load Data → API Tokens**
2. Clic en **"+ Generate API Token" → "All Access Token"**  
   *(o "Custom Token" y marca Write en tu bucket)*
3. Copia el token — **guárdalo, solo se muestra una vez**

### Obtener tu URL y nombre de organización

1. Clic en tu perfil (esquina superior derecha) → **"About"**
2. Copia el campo **"Organization Name"** (generalmente es tu email)
3. La URL se ve en la barra del navegador, algo como:  
   `https://us-east-1-1.aws.cloud2.influxdata.com`

---

## PASO 2 — Configurar este paquete

1. Ejecuta **`setup.bat`** para instalar las librerías Python
2. Abre **`config.yml`** con el Bloc de notas y completa:

```yaml
influxdb:
  url: https://us-east-1-1.aws.cloud2.influxdata.com  # tu URL
  token: TU-TOKEN-AQUI                                 # el token que copiaste
  org: tu@email.com                                    # tu nombre de organización
  bucket: misdatos                                     # el bucket que creaste
```

3. Ajusta la sección `csv` según tu archivo:

```yaml
csv:
  measurement: nombre_de_tu_tabla   # cómo llamar a estos datos en InfluxDB
  time_column: "fecha"              # columna con fecha/hora, o "" si no hay
  time_format: "%Y-%m-%d %H:%M:%S" # formato de la fecha
  separator: ","                    # separador del CSV
  encoding: "utf-8"                 # prueba latin-1 si ves caracteres raros
  chunk_size: 20000                 # filas por lote (baja si hay errores de red)
```

---

## PASO 3 — Subir un CSV

Abre una ventana de **Símbolo del sistema (cmd)** en esta carpeta y ejecuta:

```
python upload_csv.py ruta\al\archivo.csv
```

O simplemente:

```
python upload_csv.py
```

El script te pedirá la ruta, mostrará una previsualización de las columnas y te pedirá confirmación antes de comenzar la carga.

---

## PASO 4 — Crear cuenta en Grafana Cloud y conectar InfluxDB

### Crear cuenta

1. Ve a https://grafana.com y haz clic en **"Create free account"**
2. Regístrate y accede a tu espacio en `https://TU-USUARIO.grafana.net`

### Conectar InfluxDB Cloud como fuente de datos

1. En el menú izquierdo → **Connections → Data sources**
2. Clic en **"+ Add new data source"**
3. Busca y selecciona **InfluxDB**
4. Configura así:

| Campo | Valor |
|-------|-------|
| **Query Language** | Flux |
| **URL** | Tu URL de InfluxDB Cloud (ej: `https://us-east-1-1.aws.cloud2.influxdata.com`) |
| **Organization** | Tu nombre de organización (el mismo que en config.yml) |
| **Token** | Tu API Token |
| **Default Bucket** | El nombre de tu bucket (ej: `misdatos`) |

5. Clic en **"Save & Test"** — debe aparecer "datasource is working"

### Crear un dashboard

1. Menú izquierdo → **Dashboards → + New dashboard**
2. Clic en **"+ Add visualization"**
3. Selecciona **InfluxDB** como fuente
4. Escribe tu consulta en Flux:

```flux
from(bucket: "misdatos")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "nombre_de_tu_tabla")
```

5. Clic en **"Apply"** y guarda el dashboard

---

## PASO 5 — Invitar usuarios a Grafana Cloud

1. En Grafana Cloud → menú izquierdo → **Administration → Users and access → Users**
2. Clic en **"Invite user"**
3. Ingresa el email de la persona y elige su rol:
   - **Viewer** — solo puede ver dashboards
   - **Editor** — puede crear y editar dashboards
   - **Admin** — acceso completo
4. La persona recibirá un email para crear su cuenta y acceder a los dashboards

---

## Solución de problemas frecuentes

| Problema | Solución |
|----------|----------|
| "El campo 'url' no ha sido configurado" | Completa los 4 campos en config.yml antes de correr el script |
| Error de conexión al subir CSV | Verifica que el token tenga permisos de **Write** en el bucket |
| "organization not found" | El campo `org` en config.yml debe ser exactamente igual al nombre de tu org en InfluxDB Cloud |
| Caracteres raros en los datos | Cambia `encoding: "latin-1"` en config.yml |
| Carga muy lenta | Reduce `chunk_size` a 5000 si tienes conexión lenta |
| Grafana no muestra datos | Revisa que el `_measurement` en la query Flux coincida con el `measurement` en config.yml |

---

## Estructura de archivos

```
influx-grafana-cloud/
├── upload_csv.py    # Script de carga (ejecutar para subir datos)
├── config.yml       # Configuración: URL, token, bucket, columnas CSV
├── requirements.txt # Librerías Python necesarias
├── setup.bat        # Instala las librerías (ejecutar una sola vez)
└── README.md        # Esta guía
```

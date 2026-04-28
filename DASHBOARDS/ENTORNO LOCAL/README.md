# Entorno InfluxDB + Grafana con carga de CSV

Este paquete levanta un entorno completo de almacenamiento y visualización de datos en tu computador Windows. Está pensado para **levantar un servicio rápido sin especial conocimiento previo**: sigue cada paso en orden y todo funcionará.

---

## Resumen del flujo completo

Antes de entrar en detalles, este es el orden exacto de los pasos. Síguelos en secuencia:

```
1. Instalar Docker Desktop  ──►  2. Instalar Python (marcar PATH)
        │                                   │
        └──────────────┬────────────────────┘
                       ▼
        3. Copiar .env.example → .env  y  editar credenciales
                       │
                       ▼
        4. Editar config.yml con tu token, org, bucket y columnas del CSV
                       │
                       ▼
        5. Ejecutar setup.bat  (solo la primera vez)
                       │
                       ▼
        6. Entrar a InfluxDB (localhost:8086) y copiar el Token
                       │
                       ▼
        7. Pegar el token en .env y en config.yml
                       │
                       ▼
        8. Ejecutar start.bat  (cada vez que quieras usar el entorno)
                       │
                       ▼
        9. Subir CSV con:  python upload_csv.py ruta\archivo.csv
                       │
                       ▼
       10. Ver dashboards en Grafana (localhost:3000)
```

> Todos los pasos de configuración (3, 4 y 7) deben hacerse **antes** de correr `setup.bat` por primera vez, o después de correr `stop.bat` si ya arrancaste el servicio.

---

## ¿Qué hace esto?

Instala dos programas que corren en tu computador de forma silenciosa (como un servidor local):

| Programa | Para qué sirve | Dirección de acceso |
|----------|---------------|---------------------|
| **InfluxDB** | Guarda los datos de tus CSVs, organizados por tiempo | http://localhost:8086 |
| **Grafana** | Muestra dashboards y gráficas con esos datos | http://localhost:3000 |

Además incluye un script de Python (`upload_csv.py`) que lee tus archivos CSV y los sube a InfluxDB.

---

## ¿Qué es un archivo `.bat`?

Un archivo `.bat` (o *batch*) es un archivo de texto con instrucciones para Windows. Al hacer doble clic en él, Windows abre una ventana negra (consola) y ejecuta esas instrucciones automáticamente — como si tú escribieras los comandos uno por uno, pero sin tener que saber nada. En este proyecto hay tres:

- **`setup.bat`** — instala todo (se ejecuta una sola vez la primera vez)
- **`start.bat`** — enciende los servicios (InfluxDB y Grafana)
- **`stop.bat`** — apaga los servicios

---

## PASO 0 — Instalar los programas necesarios

Antes de tocar cualquier archivo de configuración, instala lo siguiente. **No omitas ningún paso.**

---

### 0.1 — Docker Desktop

Docker es el programa que "contiene" y corre InfluxDB y Grafana. Sin él nada funciona.

1. Ve a: https://www.docker.com/products/docker-desktop/
2. Descarga la versión para **Windows**
3. Instálalo (siguiente → siguiente → instalar)
4. Cuando termine, **abre Docker Desktop** desde el menú Inicio
5. Espera a que en la parte inferior diga **"Engine running"** (puede tardar 1–2 minutos)
6. Deja Docker Desktop abierto en segundo plano — debe estar corriendo siempre que uses este entorno

> **¿Cómo sé que está listo?** En la barra de tareas de Windows, verás el ícono de una ballena. Si no tiene un punto de advertencia, está corriendo.

---

### 0.2 — Python

Python es el lenguaje de programación que usa el script para subir los CSVs.

1. Ve a: https://www.python.org/downloads/
2. Descarga la versión más reciente (botón amarillo grande)
3. Ejecuta el instalador y **ANTES de hacer clic en "Install Now"**, marca la casilla que dice:

   > ✅ **Add Python to PATH**

   Esta opción es crítica. Si no la marcas, Windows no sabrá dónde está Python y el `setup.bat` fallará con un error.

4. Haz clic en **"Install Now"** y espera a que termine
5. Cierra el instalador

> **¿Qué es el PATH?** Es una lista que tiene Windows con todas las carpetas donde puede buscar programas. Si Python no está en esa lista, cuando escribas `python` en la consola, Windows dirá que no lo conoce. Marcar esa casilla lo agrega automáticamente.

---

### 0.3 — Visual Studio Code + extensiones

**VS Code es el editor recomendado para trabajar con este proyecto.** Desde ahí podrás editar los archivos de configuración, ejecutar el script de Python y ver todo en un solo lugar, sin necesidad de abrir consolas aparte.

1. Descarga VS Code si aún no lo tienes: https://code.visualstudio.com/
2. Ábrelo y presiona `Ctrl + Shift + X` para ir a Extensiones
3. Busca e instala:
   - **Python** (de Microsoft) — para editar y ejecutar archivos `.py` directamente
   - **Batch Runner** (de Nils Soderman) — para ejecutar los `.bat` desde VS Code

> Si prefieres otro editor (Cursor, Spyder, etc.), también funciona. Lo importante es que puedas abrir la carpeta del proyecto y ejecutar archivos Python desde él.

---

## PASO 1 — Abrir el proyecto y configurar los archivos

**Antes de cualquier cosa, abre la carpeta del proyecto en VS Code** (o en tu editor preferido):

1. Abre VS Code
2. Menú **Archivo → Abrir carpeta**
3. Selecciona la carpeta `influx-grafana-stack`

Desde ese momento verás todos los archivos en el panel lateral izquierdo y podrás editarlos con un solo clic.

> ⚠️ **MUY IMPORTANTE:** Configura todos los archivos de este paso **antes** de ejecutar `setup.bat`. Una vez que arranques el servicio por primera vez, InfluxDB creará su base de datos con los valores que encuentre. Si los cambias después, el servicio puede quedar inconsistente y hay que borrarlo y empezar de nuevo.

---

### 1.1 — Archivo `.env` (credenciales y nombres)

Este es el archivo más importante. Define los nombres y contraseñas de todo el sistema.

El archivo `.env.example`, renómbralo a `.env`, luego ábrelo y edítalo:

```
INFLUXDB_ADMIN_USER=admin
INFLUXDB_ADMIN_PASSWORD=cambia_esta_password
INFLUXDB_ORG=NombreDeTuOrganizacion
INFLUXDB_BUCKET=NombreDeTuBucket
INFLUXDB_TOKEN=TU_TOKEN_DE_INFLUXDB_AQUI
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=cambia_esta_password
```

**Qué es cada campo:**

| Campo | Qué es | Ejemplo |
|-------|--------|---------|
| `INFLUXDB_ADMIN_USER` | Usuario administrador de InfluxDB | `admin` |
| `INFLUXDB_ADMIN_PASSWORD` | Contraseña de InfluxDB | `MiClave2024` |
| `INFLUXDB_ORG` | Nombre de tu organización en InfluxDB | `IDC Ingenieria` |
| `INFLUXDB_BUCKET` | Nombre del "contenedor" donde se guardan los datos | `Rotorkit` |
| `INFLUXDB_TOKEN` | Clave secreta para conectarse a InfluxDB desde fuera | (se genera en el PASO 2) |
| `GRAFANA_ADMIN_USER` | Usuario administrador de Grafana | `admin` |
| `GRAFANA_ADMIN_PASSWORD` | Contraseña de Grafana | `OtraClave2024` |

> **¿Qué es un bucket?** Es como una carpeta o base de datos dentro de InfluxDB. Puedes tener varios buckets para distintos proyectos o máquinas.
>
> **¿Qué es una organización?** Es el nivel más alto de agrupación en InfluxDB. Puede ser el nombre de tu empresa, equipo o proyecto.
>
> **¿Qué es el token?** Es una contraseña larga y única que InfluxDB usa para saber que quien se conecta tiene permiso. Lo verás en el PASO 2.

---

### 1.2 — Archivo `config.yml` (configuración de carga de CSV)

Este archivo le dice al script cómo leer tu CSV y dónde guardar los datos.

```yaml
influxdb:
  url: http://localhost:8086
  token: TU_TOKEN_DE_INFLUXDB_AQUI      # <-- mismo token que en .env
  org: NombreDeTuOrganizacion            # <-- mismo valor que INFLUXDB_ORG en .env
  bucket: NombreDeTuBucket               # <-- mismo valor que INFLUXDB_BUCKET en .env

csv:
  measurement: nombre_de_tus_datos
  time_column: "Fecha"
  time_format: "%Y-%m-%d %H:%M:%S%z"
  tag_columns: []
  field_columns: []
  separator: ","
  encoding: "utf-8"
  chunk_size: 5000
```

**Explicación de cada campo del CSV:**

#### `measurement`
Es el nombre con el que se identificarán estos datos dentro de InfluxDB. Piénsalo como el nombre de una tabla en Excel. Puedes ponerle cualquier nombre sin espacios, por ejemplo: `vibraciones_motor`, `lecturas_sensor`, `EBR_data`.

#### `time_column`
El nombre exacto de la columna en tu CSV que contiene la fecha y hora de cada fila.

- Si tu columna se llama `Fecha`, escribe `"Fecha"` (con las comillas)
- Si tu columna se llama `Timestamp`, escribe `"Timestamp"`


> ⚠️ El nombre debe ser exactamente igual al encabezado del CSV, incluyendo mayúsculas y acentos.

#### `time_format`
El formato en que está escrita la fecha en tu CSV. Esto es delicado — si el formato no coincide, el script fallará.

**¿Cómo saber qué formato tienes?** Abre tu CSV con el Bloc de notas o Excel y mira cómo se ve una fecha típica:

| Si tu fecha se ve así | Usa este formato |
|-----------------------|-----------------|
| `2024-01-15 14:30:00` | `"%Y-%m-%d %H:%M:%S"` |
| `2024-01-15 14:30:00+00:00` | `"%Y-%m-%d %H:%M:%S%z"` |
| `15/01/2024 14:30` | `"%d/%m/%Y %H:%M"` |
| `2024-01-15T14:30:00Z` | `"%Y-%m-%dT%H:%M:%SZ"` |

> **¿Qué es ISO 8601?** Es el estándar internacional de fechas. Se escribe de mayor a menor: año-mes-día hora:minuto:segundo. Ejemplos: `2024-01-15T14:30:00Z` o `2024-01-15 14:30:00`. Si tus fechas tienen esta forma, son ISO 8601 y el script las manejará bien.

#### `tag_columns` y `field_columns`
- `tag_columns`: columnas de **texto o categorías** (ej: nombre de máquina, turno, ubicación). Si los dejas como `[]` (corchetes vacíos), el script los detecta automáticamente.
- `field_columns`: columnas de **valores numéricos** (ej: temperatura, vibración, presión). Si los dejas como `[]`, el script usa todas las columnas que no sean fecha ni tag.

> **¿Cuándo debo llenar los corchetes?** Solo si el script se equivoca en la detección automática. En ese caso escribe los nombres así:
> ```yaml
> tag_columns: ["Maquina", "Turno"]
> field_columns: ["Temperatura", "Presion", "Vibracion"]
> ```

#### `separator`
El carácter que separa las columnas en tu CSV:
- `,` — coma (el más común en archivos exportados en inglés)
- `;` — punto y coma (común en Excel en español)
- `\t` — tabulador

#### `encoding`
Cómo está codificado el texto del archivo:
- `"utf-8"` — prueba esto primero
- `"latin-1"` o `"cp1252"` — si ves caracteres raros como `Ã©` en lugar de `é`

---

### 1.3 — Archivo `grafana/provisioning/datasources/influxdb.yml`

Este archivo conecta Grafana con InfluxDB automáticamente. **Normalmente no necesitas tocarlo** — usa variables del `.env`.

```yaml
jsonData:
  organization: ${INFLUXDB_ORG}     # <-- toma el valor de .env automáticamente
  defaultBucket: ${INFLUXDB_BUCKET} # <-- toma el valor de .env automáticamente
secureJsonData:
  token: ${INFLUXDB_TOKEN}          # <-- toma el valor de .env automáticamente
```

> ⚠️ No reemplaces `${INFLUXDB_ORG}` con el valor real — déjalo exactamente así con el signo `$` y las llaves `{}`. Grafana lee automáticamente el valor del `.env`. Si escribes el valor directamente, funcionará igual, pero tus credenciales quedarán expuestas si subes el archivo a internet.

---

## PASO 2 — Ejecutar `setup.bat` y configurar InfluxDB

1. Asegúrate de que **Docker Desktop esté abierto y corriendo** (ícono de ballena en la barra de tareas)
2. Haz doble clic en **`setup.bat`**
3. Si Windows muestra una advertencia, haz clic en **"Más información" → "Ejecutar de todas formas"**
4. La ventana negra mostrará el progreso. Espera a que termine

Al finalizar, InfluxDB y Grafana estarán corriendo. Ahora debes entrar a InfluxDB para obtener el token.

---

### 2.1 — Obtener el Token de InfluxDB

El token es la contraseña que usará el script de Python para conectarse. **Cópialo con cuidado.**

1. Abre http://localhost:8086 en tu navegador
2. Inicia sesión con el usuario y contraseña que pusiste en `.env`
3. En el primer inicio, InfluxDB te guiará por una configuración inicial. Si te pregunta por organización y bucket, **usa exactamente los mismos valores que pusiste en `.env`**
4. Una vez dentro, ve al menú de la izquierda → **Load Data** → **API Tokens**
5. Verás un token llamado algo como "admin's Token" — haz clic en él
6. Copia el token completo (es una cadena larga)

> **¿Y si no guardé el token?** No pasa nada. Ve a: **Load Data → API Tokens → Generate API Token → All Access Token** y crea uno nuevo. Copia ese valor.

7. Pega el token en dos lugares:
   - En `.env`, en la línea `INFLUXDB_TOKEN=...`
   - En `config.yml`, en la línea `token: ...`

> ⚠️ Si cambias el token en `.env` **después** de haber arrancado el servicio, debes ejecutar `stop.bat` y luego `setup.bat` de nuevo para que Grafana se actualice. El `config.yml` puedes actualizarlo en cualquier momento.

---

### 2.2 — Verificar tu organización y bucket

Si usaste una organización o bucket diferente al que venía por defecto, o si no estás seguro de cuál quedó creado:

1. En InfluxDB (http://localhost:8086), ve al menú izquierdo → **Load Data → Buckets**
2. Ahí verás la lista de buckets existentes. Copia el nombre exacto
3. Ve al menú izquierdo → el ícono de persona (arriba a la izquierda) → **About**
4. Ahí verás el nombre de tu organización. Copia el nombre exacto

Asegúrate de que esos nombres coincidan exactamente con los del `.env` y `config.yml` — incluyendo mayúsculas, espacios y tildes.

> ⚠️ Si la organización o el bucket que necesitas **no existe aún**, créalos desde InfluxDB antes de subir datos:
> - **Bucket nuevo:** Load Data → Buckets → **+ Create Bucket**
> - La organización se crea durante la instalación inicial y no se puede cambiar fácilmente

---

## PASO 3 — Uso diario

### Encender los servicios

Haz doble clic en **`start.bat`**. La ventana mostrará el banner y confirmará que los servicios están corriendo. Luego puedes cerrar esa ventana.

> **¿Por qué hay que "arrancar el servicio"?** InfluxDB y Grafana son programas que corren como servidores en tu computador. Al apagar Windows se apagan también. `start.bat` les dice a esos programas que vuelvan a correr. Es como encender una aplicación, pero en lugar de tener ventana propia, escuchan en una dirección local (`localhost`) que puedes abrir desde el navegador.

### Apagar los servicios

Haz doble clic en **`stop.bat`**. Los datos **no se pierden** — quedan guardados en volúmenes de Docker.

---

## PASO 4 — Subir un archivo CSV

### Método recomendado — ejecutar desde VS Code (o tu IDE)

Con la carpeta ya abierta en VS Code (como hiciste en el PASO 1):

1. En el panel lateral izquierdo, haz clic sobre el archivo **`upload_csv.py`**
2. En la esquina superior derecha verás un botón **▶ (Run)**. Haz clic en él
   > También puedes hacer clic derecho sobre el archivo → **"Run Python File in Terminal"**
3. VS Code abrirá una terminal automáticamente y ejecutará el script
4. El script te pedirá la ruta de tu archivo CSV. Para obtenerla fácilmente:
   - Ve al Explorador de Windows, localiza el archivo CSV
   - Mantén `Shift` + clic derecho sobre él → **"Copiar como ruta"**
   - Vuelve a la terminal de VS Code y pega con `Ctrl + V`
   - Presiona `Enter`
   > También puedes arrastrar el archivo CSV desde el Explorador directamente a la terminal y la ruta aparecerá sola.

### Método alternativo — terminal integrada de VS Code

Si quieres pasar la ruta directamente como argumento al ejecutar:

1. Abre la terminal integrada con **`Ctrl + ñ`** (o menú **Terminal → Nueva terminal**)
2. Copia la ruta del CSV (Shift + clic derecho → "Copiar como ruta") y ejecuta:
   ```
   python upload_csv.py "C:\ruta\a\tu\archivo.csv"
   ```

### El script mostrará paso a paso

1. Una previsualización de las columnas detectadas
2. Cuáles columnas detectó como tags y cuáles como fields
3. Te pedirá confirmación antes de comenzar
4. Una barra de progreso mientras sube los datos
5. Un resumen al finalizar

---

## Acceso a Grafana

1. Abre http://localhost:3000
2. Usuario y contraseña: los que configuraste en `.env`
3. InfluxDB ya estará configurado como fuente de datos
4. Crea un nuevo dashboard → **Add panel** → selecciona **InfluxDB** → escribe tu query en Flux

**Ejemplo de query básica:**
```flux
from(bucket: "NombreDeTuBucket")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "nombre_de_tus_datos")
```

---

## Solución de problemas

### Tabla de referencia rápida

| Mensaje / síntoma | Causa probable | Solución |
|-------------------|---------------|----------|
| "Docker no encontrado" al correr setup.bat | Docker Desktop no está instalado o no está en PATH | Instala Docker Desktop y ábrelo antes de correr setup.bat |
| Docker muestra error de WSL al abrir | WSL (subsistema de Linux) está desactualizado | Abre PowerShell como administrador y ejecuta: `wsl --update`. Luego reinicia Docker Desktop |
| "Python no está instalado" | Python no está en PATH | Reinstala Python marcando "Add Python to PATH" |
| "No se pudieron iniciar los servicios" en setup.bat | Docker Desktop está cerrado | Abre Docker Desktop desde el menú Inicio y espera a que esté listo |
| Servicio no enciende después de reiniciar Windows | Docker no arrancó automáticamente | Abre Docker Desktop, espera que diga "Engine running" y luego corre start.bat |
| `config.yml tiene valores sin configurar` | El token, org o bucket todavía tiene el valor de ejemplo | Sigue el PASO 2 para obtener el token y editar `config.yml` |
| `HTTP 401 Unauthorized` | Token incorrecto o expirado | Genera un nuevo All-Access Token en InfluxDB y actualiza `config.yml` y `.env` |
| `HTTP 404 Not Found` | El bucket u organización no existen con ese nombre exacto | Verifica nombre exacto en InfluxDB → Load Data → Buckets |
| `HTTP 400 Bad Request` | Formato de datos inválido enviado a InfluxDB | Verifica `time_format`, el separador y el encoding en `config.yml` |
| `Connection refused` / `10061` | InfluxDB no está corriendo | Ejecuta `start.bat` y espera 30 segundos |
| Caracteres raros en el CSV (`Ã©`, `Ã³`) | El archivo está en latin-1, no UTF-8 | Cambia `encoding: "latin-1"` en config.yml |
| Error de timestamp / fecha no parseada | `time_format` no coincide con las fechas del CSV | Abre el CSV, copia un valor de fecha y ajusta el formato (ver tabla abajo) |
| Grafana no muestra datos | El nombre del measurement no coincide | En tu query Flux verifica que `r._measurement` sea igual que `measurement` en config.yml |
| Grafana no conecta a InfluxDB (datasource error) | Variables del `.env` no se cargaron al contenedor | Ejecuta `stop.bat` y luego `setup.bat` de nuevo |
| InfluxDB pide configuración inicial aunque ya la hiciste | El volumen de datos se borró o el token en `.env` estaba vacío cuando se ejecutó `setup.bat` | Ejecuta `stop.bat`, edita `.env` con el token correcto, y ejecuta `setup.bat` de nuevo |
| Los datos suben pero no aparecen en Grafana | Rango de tiempo del panel no cubre las fechas del CSV | Cambia el rango de tiempo en Grafana al período que tienen tus datos |

---

### Errores frecuentes en la configuración de los archivos YML

Estos son los errores más comunes que ocurren por valores incorrectos en `config.yml` o `grafana/provisioning/datasources/influxdb.yml`. El script los detecta automáticamente, pero conviene entender por qué ocurren.

---

#### Error: token sigue siendo el valor de ejemplo

**Síntoma:** el script muestra `config.yml tiene valores sin configurar` o `HTTP 401 Unauthorized`.

**Qué revisar en `config.yml`:**
```yaml
influxdb:
  token: TU_TOKEN_DE_INFLUXDB_AQUI   # ← esto debe reemplazarse
```

**Cómo resolverlo:**
1. Abre http://localhost:8086 → Load Data → API Tokens
2. Haz clic en el token existente (o genera uno con "All Access")
3. Copia el valor completo y pégalo en `config.yml` y en `.env`

> Si cambias el token en `.env` después de haber arrancado los servicios, ejecuta `stop.bat` y `setup.bat` de nuevo para que Grafana también se actualice.

---

#### Error: org o bucket no coinciden entre `.env` y `config.yml`

**Síntoma:** `HTTP 404 Not Found` o el script dice que el bucket no es accesible.

**Causa:** InfluxDB distingue entre `IDC Ingenieria` y `idc ingenieria` (mayúsculas, espacios y tildes importan). Si el valor en `config.yml` no es exactamente igual al creado durante la instalación, InfluxDB lo rechazará.

**Cómo resolverlo:**
1. Abre http://localhost:8086 → Load Data → Buckets: copia el nombre exacto del bucket
2. Abre InfluxDB → ícono de persona (arriba izquierda) → About: copia el nombre exacto de la org
3. Pega esos valores en `config.yml`:
   ```yaml
   influxdb:
     org: IDC Ingenieria        # ← exactamente como aparece en InfluxDB
     bucket: Rotorkit           # ← exactamente como aparece en InfluxDB
   ```
4. Verifica que `.env` tenga los mismos valores:
   ```
   INFLUXDB_ORG=IDC Ingenieria
   INFLUXDB_BUCKET=Rotorkit
   ```

---

#### Error: formato de fecha incorrecto (`time_format`)

**Síntoma:** el script avisa `no se pudo parsear la fecha 'VALOR' con formato 'FORMATO'` o todos los puntos se insertan sin timestamp.

**Causa:** el patrón en `time_format` no coincide con cómo está escrita la fecha en el CSV.

**Cómo diagnosticarlo:** abre el CSV con el Bloc de notas y busca la primera fila de datos. Luego busca tu patrón en la tabla:

| Si tu fecha se ve así | Usa este `time_format` |
|-----------------------|------------------------|
| `2024-01-15 14:30:00` | `"%Y-%m-%d %H:%M:%S"` |
| `2024-01-15 14:30:00+00:00` | `"%Y-%m-%d %H:%M:%S%z"` |
| `2024-01-15 14:30:00-05:00` | `"%Y-%m-%d %H:%M:%S%z"` |
| `15/01/2024 14:30` | `"%d/%m/%Y %H:%M"` |
| `15/01/2024 14:30:00` | `"%d/%m/%Y %H:%M:%S"` |
| `2024-01-15T14:30:00Z` | `"%Y-%m-%dT%H:%M:%SZ"` |
| `2024-01-15T14:30:00` | `"%Y-%m-%dT%H:%M:%S"` |
| `01/15/2024 14:30` | `"%m/%d/%Y %H:%M"` |

> Si tu fecha no aparece en la tabla, busca en Google el patrón `strftime` que corresponde a tu formato.

---

#### Error: Grafana no conecta a InfluxDB (datasource error rojo)

**Síntoma:** al abrir Grafana en http://localhost:3000, el datasource InfluxDB aparece con un punto rojo o muestra "Data source connected, but no default bucket found".

**Causa frecuente:** las variables `${INFLUXDB_TOKEN}`, `${INFLUXDB_ORG}`, `${INFLUXDB_BUCKET}` del archivo `grafana/provisioning/datasources/influxdb.yml` no se resolvieron correctamente — esto pasa cuando el contenedor se creó antes de que el `.env` tuviera los valores definitivos.

**Cómo resolverlo:**
1. Ejecuta `stop.bat`
2. Verifica que `.env` tenga el token, org y bucket correctos
3. Ejecuta `setup.bat` de nuevo (los contenedores se recrean y leen el `.env` actualizado)

> No reemplaces `${INFLUXDB_ORG}` con el valor directamente en `influxdb.yml` — déjalo con el `${}` y que lo tome del `.env`.

---

#### Error: InfluxDB pide "Get Started" aunque ya lo configuraste antes

**Síntoma:** al abrir http://localhost:8086 aparece el asistente de configuración inicial como si fuera la primera vez.

**Causa:** el campo `INFLUXDB_TOKEN` en `.env` estaba vacío o con el valor de ejemplo (`TU_TOKEN_DE_INFLUXDB_AQUI`) cuando se ejecutó `setup.bat` por primera vez. InfluxDB requiere que el token inicial esté definido para completar la inicialización automática.

**Cómo resolverlo:**
1. Ejecuta `stop.bat`
2. Abre `.env` y pon un token real (puede ser cualquier cadena larga, por ejemplo 32 caracteres aleatorios)
3. Ejecuta `setup.bat` de nuevo
4. Una vez dentro de InfluxDB, copia el token desde Load Data → API Tokens y actualiza `config.yml`

---

## Estructura de archivos

```
influx-grafana-stack/
├── .env                     ← Tus credenciales reales (NO subir a internet)
├── .env.example             ← Plantilla con valores de ejemplo (sí se puede compartir)
├── config.yml               ← Configuración de carga de CSV (editar antes de subir datos)
├── docker-compose.yml       ← Define cómo corren InfluxDB y Grafana (no tocar)
├── upload_csv.py            ← Script para subir archivos CSV
├── requirements.txt         ← Lista de librerías Python que se instalan automáticamente
├── setup.bat                ← Instalación completa (ejecutar una sola vez)
├── start.bat                ← Enciende los servicios
├── stop.bat                 ← Apaga los servicios
└── grafana/
    └── provisioning/
        └── datasources/
            └── influxdb.yml ← Conecta Grafana con InfluxDB automáticamente (no tocar)
```

---

## Notas de seguridad

- El archivo `.env` contiene tus contraseñas reales. **Nunca lo subas a GitHub ni lo compartas.**
- Para compartir el proyecto, comparte `.env.example` (que tiene valores de ejemplo, no reales)
- El `.gitignore` ya está configurado para que git ignore el `.env` automáticamente

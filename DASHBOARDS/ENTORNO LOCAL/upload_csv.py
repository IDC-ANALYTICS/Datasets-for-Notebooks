#!/usr/bin/env python3
"""
=========================================================
  Cargador de CSV a InfluxDB 2.x  —  con soporte de
  archivos pesados mediante procesamiento por chunks
=========================================================
Uso:
    python upload_csv.py                     # modo interactivo
    python upload_csv.py ruta/al/archivo.csv # modo directo
"""

import sys
import os
import time
import math
import yaml
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# ──────────────────────────────────────────────
#  Colores para la terminal (Windows compatible)
# ──────────────────────────────────────────────
try:
    import colorama
    colorama.init(autoreset=True)
    GREEN  = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    RED    = colorama.Fore.RED
    CYAN   = colorama.Fore.CYAN
    BOLD   = colorama.Style.BRIGHT
    RESET  = colorama.Style.RESET_ALL
except ImportError:
    GREEN = YELLOW = RED = CYAN = BOLD = RESET = ""


def log_message(message: str, level: str = "info", use_tqdm: bool = True):
    """Imprime mensajes con prefijo y color, evitando mezclar salida con la barra de progreso."""
    level = level.lower().strip()
    prefixes = {
        "info": "INFO",
        "ok": "OK",
        "warn": "AVISO",
        "error": "ERROR",
    }
    colors = {
        "info": CYAN,
        "ok": GREEN,
        "warn": YELLOW,
        "error": RED,
    }
    prefix = prefixes.get(level, "INFO")
    color = colors.get(level, CYAN)
    text = f"{color}[{prefix}] {message}{RESET}"
    if use_tqdm:
        tqdm.write(text)
    else:
        print(text)


def banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════╗
║       Cargador CSV → InfluxDB 2.x            ║
║       Soporte para archivos grandes          ║
╚══════════════════════════════════════════════╝{RESET}
""")


def load_config(config_path: str = "config.yml") -> dict:
    """Carga la configuracion desde config.yml."""
    if not os.path.exists(config_path):
        log_message(f"No se encontro el archivo '{config_path}'.", "error", use_tqdm=False)
        log_message("Ejecuta este script desde la carpeta del proyecto.", "warn", use_tqdm=False)
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_config(config: dict):
    """Detecta valores de placeholder que el usuario olvido cambiar."""
    PLACEHOLDERS = {
        "TU_TOKEN_DE_INFLUXDB_AQUI": (
            "influxdb → token en config.yml",
            "Copia el token desde InfluxDB (PASO 2) y pegalo en config.yml y en .env"
        ),
        "NombreDeTuOrganizacion": (
            "influxdb → org en config.yml",
            "Escribe el nombre exacto de tu organización (el mismo que usaste en .env)"
        ),
        "NombreDeTuBucket": (
            "influxdb → bucket en config.yml",
            "Escribe el nombre exacto de tu bucket (el mismo que usaste en .env)"
        ),
    }

    errors_found = []
    db = config.get("influxdb", {})
    for field in ("token", "org", "bucket"):
        val = str(db.get(field, "")).strip()
        if val in PLACEHOLDERS:
            label, hint = PLACEHOLDERS[val]
            errors_found.append((label, hint))
        elif not val:
            errors_found.append((
                f"influxdb → {field} en config.yml",
                f"El campo '{field}' está vacío. Complétalo antes de continuar."
            ))

    if errors_found:
        print(f"{RED}{'═'*55}")
        print(f"  ERROR: config.yml tiene valores sin configurar")
        print(f"{'═'*55}{RESET}")
        for label, hint in errors_found:
            print(f"{YELLOW}  • {label}")
            print(f"    → {hint}{RESET}")
        print(f"\n  Abre config.yml y corrige los campos indicados antes de continuar.")
        print(f"  Consulta el README, sección PASO 1 y PASO 2, para más detalle.\n")
        sys.exit(1)


def get_csv_path() -> str:
    """Pide al usuario la ruta del archivo CSV si no se paso como argumento."""
    if len(sys.argv) > 1:
        path = sys.argv[1].strip('"').strip("'")
        if not os.path.exists(path):
            print(f"{RED}ERROR: No se encontro el archivo: {path}{RESET}")
            sys.exit(1)
        return path

    print(f"{YELLOW}Arrastra y suelta el archivo CSV aqui, o escribe la ruta completa:{RESET}")
    path = input("  Ruta del CSV: ").strip().strip('"').strip("'")
    if not os.path.exists(path):
        log_message(f"No se encontro el archivo: {path}", "error", use_tqdm=False)
        sys.exit(1)
    return path


def estimate_rows(filepath: str, sep: str, encoding: str) -> int:
    """Estima el numero de filas contando saltos de linea (rapido para archivos grandes)."""
    try:
        size = os.path.getsize(filepath)
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            # Lee las primeras 1000 lineas para estimar el tamano promedio por fila
            sample_lines = 0
            sample_bytes = 0
            for line in f:
                sample_bytes += len(line.encode(encoding, errors="replace"))
                sample_lines += 1
                if sample_lines >= 1000:
                    break
        if sample_lines == 0:
            return 0
        avg_bytes_per_row = sample_bytes / sample_lines
        return max(1, int(size / avg_bytes_per_row) - 1)  # -1 por el header
    except Exception:
        return 0


def preview_csv(filepath: str, sep: str, encoding: str):
    """Muestra las primeras filas y el tipo de cada columna."""
    try:
        df = pd.read_csv(filepath, sep=sep, encoding=encoding, nrows=3)
        print(f"\n{CYAN}Primeras filas del CSV (sep='{sep}', encoding='{encoding}'):{RESET}")
        print(df.to_string(index=False))
        print(f"\n{CYAN}Columnas detectadas ({len(df.columns)}):{RESET}")
        for col in df.columns:
            dtype = df[col].dtype
            print(f"  • {col:<30} [{dtype}]")
        if len(df.columns) == 1:
            single_col = str(df.columns[0])
            if "," in single_col and sep != ",":
                log_message(
                    f"Pandas solo detecto una columna y el encabezado contiene comas. El separador real probablemente es ',' en lugar de '{sep}'.",
                    "warn",
                    use_tqdm=False,
                )
            elif ";" in single_col and sep != ";":
                log_message(
                    f"Pandas solo detecto una columna y el encabezado contiene punto y coma. El separador real probablemente es ';' en lugar de '{sep}'.",
                    "warn",
                    use_tqdm=False,
                )
        return list(df.columns)
    except Exception as e:
        log_message(
            f"No se pudo leer el CSV con sep='{sep}' y encoding='{encoding}': {e}",
            "error",
            use_tqdm=False,
        )
        log_message(
            "Revisa el separador, el encoding y que la primera fila sea un encabezado válido.",
            "warn",
            use_tqdm=False,
        )
        sys.exit(1)


def resolve_columns(cfg_csv: dict, all_columns: list) -> tuple:
    """
    Determina columnas de tag y field.
    Si no estan configuradas, auto-detecta por tipo de dato.
    """
    time_col   = cfg_csv.get("time_column", "").strip()
    tag_cols   = cfg_csv.get("tag_columns", []) or []
    field_cols = cfg_csv.get("field_columns", []) or []

    remaining = [c for c in all_columns if c != time_col]

    if not tag_cols and not field_cols:
        # Auto-deteccion: necesitamos leer unas filas para inferir tipos
        return None, None  # se resolvera en el primer chunk

    if not field_cols:
        field_cols = [c for c in remaining if c not in tag_cols]
    if not tag_cols:
        tag_cols = [c for c in remaining if c not in field_cols]

    return tag_cols, field_cols


def auto_detect_columns(chunk: pd.DataFrame, time_col: str, tag_cols: list, field_cols: list):
    """Infiere tags y fields a partir del tipo de dato del chunk."""
    if tag_cols is not None and field_cols is not None:
        return tag_cols, field_cols

    remaining = [c for c in chunk.columns if c != time_col]
    detected_tags   = []
    detected_fields = []

    for col in remaining:
        if pd.api.types.is_numeric_dtype(chunk[col]):
            detected_fields.append(col)
        else:
            # Intentar coercionar a numérico (maneja números guardados como strings)
            normalized = chunk[col].astype(str).str.replace(" ", "", regex=False)
            normalized = normalized.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            coerced = pd.to_numeric(normalized, errors='coerce')
            non_null = chunk[col].notna().sum()
            if non_null > 0 and coerced.notna().sum() / non_null >= 0.8:
                detected_fields.append(col)
            else:
                detected_tags.append(col)

    return detected_tags, detected_fields


def sanitize_column_name(name: str) -> str:
    """Reemplaza espacios y caracteres especiales en nombres de columnas."""
    # Reemplaza espacios con guiones bajos
    name = name.replace(" ", "_")
    # Reemplaza otros caracteres problemáticos
    name = name.replace("-", "_")
    name = name.replace(".", "_")
    name = name.replace("+", "plus")
    return name


def parse_timestamp_to_ns(value, time_format: str):
    """Convierte un valor de fecha a nanosegundos Unix usando varios intentos."""
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    parsers = []
    if time_format:
        parsers.append(lambda: pd.to_datetime(text, format=time_format))
    parsers.extend([
        lambda: pd.to_datetime(text, utc=True, dayfirst=True),
        lambda: pd.to_datetime(text, utc=False, dayfirst=False),
    ])

    for parser in parsers:
        try:
            ts = parser()
            if pd.isna(ts):
                continue
            return int(pd.Timestamp(ts).value)
        except Exception:
            continue

    return None


def parse_field_value(value):
    """Convierte valores de campo a numero o string compatible con line protocol."""
    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace(" ", "")
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    else:
        normalized = normalized.replace(",", ".")

    try:
        return float(normalized)
    except (ValueError, TypeError):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'


def chunk_to_line_protocol(chunk: pd.DataFrame,
                            measurement: str,
                            tag_cols: list,
                            field_cols: list,
                            time_col: str,
                            time_format: str) -> list:
    """Convierte un DataFrame chunk a lista de puntos en line protocol."""
    records = []

    for row_idx, (_, row) in enumerate(chunk.iterrows()):
        try:
            # Timestamp
            if time_col and time_col in row.index and pd.notna(row[time_col]):
                try:
                    ts_ns = parse_timestamp_to_ns(row[time_col], time_format)
                    if ts_ns is None and row_idx == 0:
                        log_message(
                            f"No se pudo parsear la fecha '{row[time_col]}' en la columna '{time_col}'. Se enviara sin timestamp.",
                            "warn",
                        )
                except Exception:
                    ts_ns = None
                    if row_idx == 0:
                        log_message(
                            f"No se pudo parsear la fecha '{row[time_col]}' en la columna '{time_col}' con time_format='{time_format}'.",
                            "warn",
                        )
            else:
                ts_ns = None

            # Tags (con nombres sanitizados)
            tags = {}
            for tc in tag_cols:
                if tc in row.index and pd.notna(row[tc]):
                    sanitized_name = sanitize_column_name(tc)
                    tags[sanitized_name] = str(row[tc]).replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")

            # Fields (con nombres sanitizados)
            fields = {}
            for fc in field_cols:
                if fc in row.index and pd.notna(row[fc]):
                    val = parse_field_value(row[fc])
                    if val is None:
                        continue
                    sanitized_name = sanitize_column_name(fc)
                    fields[sanitized_name] = val

            if not fields:
                continue  # omitir filas sin fields validos

            # Construir line protocol
            tag_str = ""
            if tags:
                tag_str = "," + ",".join(f"{k}={v}" for k, v in tags.items())

            field_str = ",".join(
                f"{k}={v}i" if isinstance(v, int) else
                f"{k}={v}" if isinstance(v, float) else
                f"{k}={v}"
                for k, v in fields.items()
            )

            line = f"{measurement}{tag_str} {field_str}"
            if ts_ns is not None:
                line += f" {ts_ns}"

            records.append(line)
        except Exception as row_err:
            # Si falla una fila, loguear pero continuar
            log_message(
                f"Fila {row_idx + 1} omitida por error: {row_err}. Revisa tipos de dato, columnas vacias o caracteres inesperados.",
                "warn",
            )
            continue

    return records


def upload_csv(filepath: str, config: dict):
    """Proceso principal de carga con chunks y barra de progreso."""
    cfg_db  = config["influxdb"]
    cfg_csv = config["csv"]

    url         = cfg_db["url"]
    token       = cfg_db["token"]
    org         = cfg_db["org"]
    bucket      = cfg_db["bucket"]
    measurement = cfg_csv.get("measurement", "datos")
    chunk_size  = int(cfg_csv.get("chunk_size", 50000))
    sep         = cfg_csv.get("separator", ",")
    encoding    = cfg_csv.get("encoding", "utf-8")
    time_col    = cfg_csv.get("time_column", "").strip()
    time_format = cfg_csv.get("time_format", "")

    # ── Validar que no queden placeholders sin reemplazar ──
    validate_config(config)

    # ── Preview ──
    all_columns = preview_csv(filepath, sep, encoding)
    tag_cols, field_cols = resolve_columns(cfg_csv, all_columns)

    # ── Estimacion de filas ──
    est_rows = estimate_rows(filepath, sep, encoding)
    est_chunks = max(1, math.ceil(est_rows / chunk_size))
    size_mb = os.path.getsize(filepath) / (1024 * 1024)

    print(f"\n{CYAN}Archivo: {BOLD}{os.path.basename(filepath)}{RESET}")
    print(f"  Tamaño estimado : {size_mb:.1f} MB")
    print(f"  Filas estimadas : {est_rows:,}")
    print(f"  Chunks de       : {chunk_size:,} filas")
    print(f"  InfluxDB bucket : {bucket}  |  measurement: {measurement}")
    print(f"  URL InfluxDB    : {url}\n")
    log_message(
        f"CSV detectado con time_column='{time_col}', separator='{sep}' y encoding='{encoding}'.",
        "info",
        use_tqdm=False,
    )

    respuesta = input(f"{YELLOW}¿Comenzar la carga? (s/n): {RESET}").strip().lower()
    if respuesta not in ("s", "si", "sí", "y", "yes"):
        log_message("Carga cancelada por el usuario.", "warn", use_tqdm=False)
        sys.exit(0)

    # ── Conexion a InfluxDB ──
    log_message("Conectando a InfluxDB...", "info", use_tqdm=False)
    try:
        client = InfluxDBClient(url=url, token=token, org=org, timeout=30000)
        health = client.health()
        if health.status != "pass":
            raise ConnectionError(f"InfluxDB no responde correctamente: {health.status}")
        log_message("Conexion exitosa.", "ok", use_tqdm=False)
    except Exception as e:
        error_msg = str(e)
        log_message(f"No se pudo conectar con InfluxDB: {error_msg}", "error", use_tqdm=False)
        if "Connection refused" in error_msg or "Failed to establish" in error_msg or "10061" in error_msg:
            log_message("El servicio InfluxDB no esta corriendo. Ejecuta start.bat y reintenta.", "warn", use_tqdm=False)
        elif "401" in error_msg or "Unauthorized" in error_msg:
            log_message("Token incorrecto o sin permisos (HTTP 401).", "warn", use_tqdm=False)
            log_message("Verifica que el token en config.yml coincida con el de InfluxDB y tenga acceso al bucket.", "warn", use_tqdm=False)
        elif "timed out" in error_msg or "timeout" in error_msg.lower():
            log_message("Timeout de conexion. Docker puede estar iniciando todavia.", "warn", use_tqdm=False)
        else:
            log_message("Verifica que Docker Desktop este abierto y que hayas ejecutado start.bat.", "warn", use_tqdm=False)
        sys.exit(1)

    write_api = client.write_api(write_options=SYNCHRONOUS)

    # ── Validar bucket ──
    log_message(f"Validando bucket '{bucket}'...", "info", use_tqdm=False)
    try:
        query_api = client.query_api()
        query_api.query(f'from(bucket:"{bucket}") |> range(start: -1h) |> limit(n:1)')
        log_message("Bucket accesible.", "ok", use_tqdm=False)
    except Exception as be:
        be_msg = str(be)
        if "404" in be_msg or "not found" in be_msg.lower() or "bucket" in be_msg.lower():
            log_message(f"El bucket '{bucket}' no existe o no es accesible.", "error", use_tqdm=False)
            log_message("Revisa nombre exacto del bucket, organizacion y permisos del token.", "warn", use_tqdm=False)
            client.close()
            sys.exit(1)
        elif "401" in be_msg or "Unauthorized" in be_msg:
            log_message("Token invalido para acceder al bucket (HTTP 401).", "error", use_tqdm=False)
            log_message("Verifica que el token sea un All-Access Token o tenga permisos sobre el bucket.", "warn", use_tqdm=False)
            client.close()
            sys.exit(1)
        else:
            log_message(f"Advertencia al validar bucket: {be_msg[:120]}", "warn", use_tqdm=False)
            log_message("El script intentara continuar de todas formas.", "warn", use_tqdm=False)

    # ── Carga por chunks ──
    total_rows   = 0
    total_errors = 0
    skipped_rows = 0
    start_time   = time.time()
    first_chunk_sample = True  # Para mostrar muestra de line protocol

    reader = pd.read_csv(
        filepath,
        sep=sep,
        encoding=encoding,
        chunksize=chunk_size,
        low_memory=False
    )

    log_message("Iniciando carga por chunks...", "info", use_tqdm=False)
    with tqdm(total=est_rows, unit="filas", unit_scale=True, colour="green",
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} filas  [{elapsed}<{remaining}]") as pbar:

        for chunk_idx, chunk in enumerate(reader):
            # Auto-detectar columnas en el primer chunk si no estan configuradas
            if tag_cols is None or field_cols is None:
                tag_cols, field_cols = auto_detect_columns(chunk, time_col, tag_cols, field_cols)
                if chunk_idx == 0:
                    log_message(f"Tags detectados: {tag_cols}", "info", use_tqdm=False)
                    log_message(f"Fields detectados: {field_cols}", "info", use_tqdm=False)

            # Intentar escribir el chunk con reintentos
            max_retries = 3
            retry_count = 0
            chunk_written = False

            while retry_count < max_retries and not chunk_written:
                try:
                    lines = chunk_to_line_protocol(
                        chunk, measurement, tag_cols, field_cols, time_col, time_format
                    )
                    
                    # Mostrar muestra de line protocol en el primer chunk exitoso
                    if first_chunk_sample and lines:
                        first_chunk_sample = False
                        sample_lines = lines[:3]  # mostrar primeras 3 lineas
                        log_message("Muestra del formato enviado a InfluxDB:", "info")
                        for sample in sample_lines:
                            log_message(f"  {sample[:120]}{'...' if len(sample) > 120 else ''}", "info")
                    
                    if lines:
                        # Escribir en lotes más pequeños para evitar que InfluxDB se ahogue
                        batch_size = 1000  # 1000 líneas por lote
                        for batch_idx in range(0, len(lines), batch_size):
                            batch = lines[batch_idx:batch_idx + batch_size]
                            write_api.write(bucket=bucket, org=org, record=batch,
                                            write_precision="ns")
                        chunk_written = True
                        total_rows += len(chunk)
                        pbar.update(len(chunk))
                    else:
                        log_message(f"Chunk {chunk_idx + 1}: no genero filas validas. Todas las filas fueron omitidas.", "warn")
                        if chunk_idx == 0:
                            log_message(f"field_cols detectados: {field_cols}", "warn")
                            log_message(f"tag_cols detectados: {tag_cols}", "warn")
                            log_message(f"Columnas y tipos: { {c: str(chunk[c].dtype) for c in chunk.columns} }", "warn")
                            if len(chunk) > 0:
                                sample = dict(list(chunk.iloc[0].items())[:6])
                                log_message(f"Primera fila (hasta 6 cols): {sample}", "warn")
                        total_rows += len(chunk)
                        pbar.update(len(chunk))
                        chunk_written = True

                except Exception as e:
                    retry_count += 1
                    error_msg = str(e)
                    
                    # Detectar error de conexión abortada
                    if "10053" in error_msg or "Connection aborted" in error_msg:
                        log_message("Conexion abortada por InfluxDB (10053).", "error")
                        log_message("Posibles causas: memoria insuficiente, timeout agotado o reinicio del servidor.", "warn")
                        if retry_count < max_retries:
                            wait_time = 3 * retry_count  # esperas más largas para reconectar
                            log_message(f"Esperando {wait_time}s y reintentando ({retry_count}/{max_retries})...", "warn")
                            time.sleep(wait_time)
                        else:
                            log_message(f"Abortando despues de {max_retries} intentos.", "error")
                            total_errors += 1
                            chunk_written = True
                    
                    # Detectar error 401 (Unauthorized)
                    elif "401" in error_msg or "Unauthorized" in error_msg:
                        log_message(f"HTTP 401 - Token invalido o sin permisos para el bucket '{bucket}'.", "error")
                        log_message("Genera o copia un token con permisos de escritura y actualiza config.yml.", "warn")
                        total_errors += 1
                        chunk_written = True  # no tiene sentido reintentar con el mismo token

                    # Detectar error 404 (Not Found)
                    elif "404" in error_msg or "not found" in error_msg.lower():
                        log_message(f"HTTP 404 - Recurso no encontrado para bucket '{bucket}' o org '{org}'.", "error")
                        log_message("Verifica el nombre exacto de org y bucket en InfluxDB.", "warn")
                        total_errors += 1
                        chunk_written = True

                    # Detectar error 400 (Bad Request)
                    elif "400" in error_msg or "Bad Request" in error_msg:
                        log_message("HTTP 400 - Bad Request al escribir el chunk.", "error")
                        log_message("Revisa time_format, nombres de columnas y campos nulos en el CSV.", "warn")
                        if retry_count < max_retries:
                            log_message(f"Reintentando ({retry_count}/{max_retries})...", "warn")
                            time.sleep(2)
                        else:
                            log_message(f"Abortando despues de {max_retries} intentos.", "error")
                            total_errors += 1
                            chunk_written = True
                    else:
                        if retry_count < max_retries:
                            wait_time = 2 ** (retry_count - 1)  # backoff exponencial
                            log_message(
                                f"Chunk {chunk_idx + 1} reintentando ({retry_count}/{max_retries}) en {wait_time}s: {error_msg[:120]}",
                                "warn",
                            )
                            time.sleep(wait_time)
                        else:
                            total_errors += 1
                            log_message(f"Error en chunk {chunk_idx + 1} despues de agotar reintentos: {error_msg[:160]}", "error")
                            chunk_written = True

    # ── Resumen final ──
    elapsed = time.time() - start_time
    client.close()

    speed = total_rows / elapsed if elapsed > 0 else 0

    print(f"""
{GREEN}{BOLD}═══════════════════════════════════════
  CARGA COMPLETADA
═══════════════════════════════════════{RESET}
  Filas procesadas : {total_rows:,}
  Errores de chunk : {total_errors}
  Tiempo total     : {elapsed:.1f} segundos
  Velocidad media  : {speed:,.0f} filas/seg

{CYAN}Abre Grafana en: http://localhost:3000{RESET}
  Usuario: (el que pusiste en .env)
""")


# ──────────────────────────────────────────────
#  Punto de entrada
# ──────────────────────────────────────────────
if __name__ == "__main__":
    try:
        banner()
        config   = load_config("config.yml")
        filepath = get_csv_path()
        upload_csv(filepath, config)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Operacion cancelada por el usuario.{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}ERROR FATAL: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

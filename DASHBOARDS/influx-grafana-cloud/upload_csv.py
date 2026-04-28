#!/usr/bin/env python3
"""
=========================================================
  Cargador de CSV a InfluxDB Cloud  —  con soporte de
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


def banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════╗
║     Cargador CSV → InfluxDB Cloud            ║
║     Soporte para archivos grandes            ║
╚══════════════════════════════════════════════╝{RESET}
""")


def load_config(config_path: str = "config.yml") -> dict:
    if not os.path.exists(config_path):
        print(f"{RED}ERROR: No se encontro el archivo '{config_path}'.")
        print(f"Asegurate de ejecutar este script desde la carpeta del proyecto.{RESET}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_config(cfg: dict):
    """Verifica que los campos obligatorios de config.yml esten completos."""
    placeholders = [
        "TU-REGION.aws.cloud2.influxdata.com",
        "PEGA-AQUI-TU-API-TOKEN",
        "PEGA-AQUI-TU-EMAIL-O-NOMBRE-DE-ORG",
    ]
    db = cfg.get("influxdb", {})
    for key in ("url", "token", "org", "bucket"):
        val = str(db.get(key, "")).strip()
        if not val or any(p in val for p in placeholders):
            print(f"""
{RED}ERROR: El campo '{key}' en config.yml no ha sido configurado.

Abre config.yml con el Bloc de notas y completa:
  url    -> URL de tu organizacion en InfluxDB Cloud
  token  -> tu API Token con permiso de escritura
  org    -> nombre de tu organizacion (generalmente tu email)
  bucket -> nombre del bucket donde guardar los datos

Lee el README.md para instrucciones paso a paso.{RESET}
""")
            sys.exit(1)


def get_csv_path() -> str:
    if len(sys.argv) > 1:
        path = sys.argv[1].strip('"').strip("'")
        if not os.path.exists(path):
            print(f"{RED}ERROR: No se encontro el archivo: {path}{RESET}")
            sys.exit(1)
        return path

    print(f"{YELLOW}Arrastra y suelta el archivo CSV aqui, o escribe la ruta completa:{RESET}")
    path = input("  Ruta del CSV: ").strip().strip('"').strip("'")
    if not os.path.exists(path):
        print(f"{RED}ERROR: No se encontro el archivo: {path}{RESET}")
        sys.exit(1)
    return path


def estimate_rows(filepath: str, encoding: str) -> int:
    try:
        size = os.path.getsize(filepath)
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            sample_bytes = 0
            sample_lines = 0
            for line in f:
                sample_bytes += len(line.encode(encoding, errors="replace"))
                sample_lines += 1
                if sample_lines >= 1000:
                    break
        if sample_lines == 0:
            return 0
        return max(1, int(size / (sample_bytes / sample_lines)) - 1)
    except Exception:
        return 0


def preview_csv(filepath: str, sep: str, encoding: str) -> list:
    try:
        df = pd.read_csv(filepath, sep=sep, encoding=encoding, nrows=3)
        print(f"\n{CYAN}Primeras filas del CSV:{RESET}")
        print(df.to_string(index=False))
        print(f"\n{CYAN}Columnas detectadas:{RESET}")
        for col in df.columns:
            print(f"  • {col:<30} [{df[col].dtype}]")
        return list(df.columns)
    except Exception as e:
        print(f"{RED}Error al leer el CSV: {e}{RESET}")
        sys.exit(1)


def resolve_columns(cfg_csv: dict, all_columns: list):
    time_col   = cfg_csv.get("time_column", "").strip()
    tag_cols   = cfg_csv.get("tag_columns", []) or []
    field_cols = cfg_csv.get("field_columns", []) or []
    remaining  = [c for c in all_columns if c != time_col]

    if not tag_cols and not field_cols:
        return None, None  # auto-detectar en primer chunk

    if not field_cols:
        field_cols = [c for c in remaining if c not in tag_cols]
    if not tag_cols:
        tag_cols = [c for c in remaining if c not in field_cols]

    return tag_cols, field_cols


def auto_detect_columns(chunk: pd.DataFrame, time_col: str, tag_cols, field_cols):
    if tag_cols is not None and field_cols is not None:
        return tag_cols, field_cols
    remaining = [c for c in chunk.columns if c != time_col]
    detected_tags   = [c for c in remaining if not pd.api.types.is_numeric_dtype(chunk[c])]
    detected_fields = [c for c in remaining if pd.api.types.is_numeric_dtype(chunk[c])]
    return detected_tags, detected_fields


def chunk_to_line_protocol(chunk, measurement, tag_cols, field_cols, time_col, time_format):
    records = []
    for _, row in chunk.iterrows():
        # Timestamp
        ts_ns = None
        if time_col and time_col in row.index and pd.notna(row[time_col]):
            try:
                ts = pd.to_datetime(row[time_col], format=time_format if time_format else None)
                ts_ns = int(ts.value)
            except Exception:
                ts_ns = None

        # Tags
        tags = {}
        for tc in tag_cols:
            if tc in row.index and pd.notna(row[tc]):
                val = str(row[tc]).replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")
                tags[tc] = val

        # Fields
        fields = {}
        for fc in field_cols:
            if fc in row.index and pd.notna(row[fc]):
                try:
                    fields[fc] = float(row[fc])
                except (ValueError, TypeError):
                    fields[fc] = f'"{str(row[fc])}"'

        if not fields:
            continue

        tag_str   = ("," + ",".join(f"{k}={v}" for k, v in tags.items())) if tags else ""
        field_str = ",".join(
            f"{k}={v}" if isinstance(v, float) else f"{k}={v}"
            for k, v in fields.items()
        )
        line = f"{measurement}{tag_str} {field_str}"
        if ts_ns is not None:
            line += f" {ts_ns}"
        records.append(line)
    return records


def upload_csv(filepath: str, config: dict):
    cfg_db  = config["influxdb"]
    cfg_csv = config["csv"]

    url         = cfg_db["url"].rstrip("/")
    token       = cfg_db["token"]
    org         = cfg_db["org"]
    bucket      = cfg_db["bucket"]
    measurement = cfg_csv.get("measurement", "datos")
    chunk_size  = int(cfg_csv.get("chunk_size", 20000))
    sep         = cfg_csv.get("separator", ",")
    encoding    = cfg_csv.get("encoding", "utf-8")
    time_col    = cfg_csv.get("time_column", "").strip()
    time_format = cfg_csv.get("time_format", "")

    # Preview
    all_columns = preview_csv(filepath, sep, encoding)
    tag_cols, field_cols = resolve_columns(cfg_csv, all_columns)

    # Estimacion
    est_rows   = estimate_rows(filepath, encoding)
    size_mb    = os.path.getsize(filepath) / (1024 * 1024)

    print(f"\n{CYAN}Archivo     : {BOLD}{os.path.basename(filepath)}{RESET}")
    print(f"  Tamaño    : {size_mb:.1f} MB")
    print(f"  Filas est.: {est_rows:,}")
    print(f"  Chunk     : {chunk_size:,} filas por lote")
    print(f"  Destino   : {url}")
    print(f"  Bucket    : {bucket}  |  Measurement: {measurement}\n")

    respuesta = input(f"{YELLOW}¿Comenzar la carga? (s/n): {RESET}").strip().lower()
    if respuesta not in ("s", "si", "sí", "y", "yes"):
        print("Carga cancelada.")
        sys.exit(0)

    # Conexion
    print(f"\n{CYAN}Conectando a InfluxDB Cloud...{RESET}")
    try:
        client = InfluxDBClient(url=url, token=token, org=org)
        health = client.health()
        if health.status != "pass":
            raise ConnectionError(f"Estado: {health.status}")
        print(f"{GREEN}✓ Conexion exitosa{RESET}")
    except Exception as e:
        print(f"""
{RED}ERROR al conectar con InfluxDB Cloud: {e}

Verifica en config.yml:
  • url    - debe ser la URL completa de tu organizacion (ej: https://us-east-1-1.aws.cloud2.influxdata.com)
  • token  - debe tener permisos de escritura (Write) sobre el bucket
  • org    - debe coincidir exactamente con el nombre de tu organizacion en InfluxDB Cloud{RESET}
""")
        sys.exit(1)

    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Carga
    total_rows = total_errors = 0
    start_time = time.time()

    reader = pd.read_csv(
        filepath, sep=sep, encoding=encoding,
        chunksize=chunk_size, low_memory=False
    )

    print(f"\n{CYAN}Iniciando carga hacia la nube...{RESET}")
    with tqdm(total=est_rows, unit="filas", unit_scale=True, colour="green",
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:

        for chunk_idx, chunk in enumerate(reader):
            if tag_cols is None or field_cols is None:
                tag_cols, field_cols = auto_detect_columns(chunk, time_col, tag_cols, field_cols)
                if chunk_idx == 0:
                    print(f"\n  Tags  : {tag_cols}")
                    print(f"  Fields: {field_cols}\n")

            try:
                lines = chunk_to_line_protocol(
                    chunk, measurement, tag_cols, field_cols, time_col, time_format
                )
                if lines:
                    write_api.write(bucket=bucket, org=org, record=lines, write_precision="ns")
                total_rows += len(chunk)
                pbar.update(len(chunk))
            except Exception as e:
                total_errors += 1
                tqdm.write(f"{RED}  Error en chunk {chunk_idx + 1}: {e}{RESET}")
                if total_errors >= 5:
                    tqdm.write(f"{RED}  Demasiados errores. Abortando.{RESET}")
                    break

    elapsed = time.time() - start_time
    client.close()

    print(f"""
{GREEN}{BOLD}═══════════════════════════════════════
  CARGA COMPLETADA
═══════════════════════════════════════{RESET}
  Filas subidas  : {total_rows:,}
  Errores        : {total_errors}
  Tiempo total   : {elapsed:.1f} segundos
  Velocidad media: {total_rows / elapsed if elapsed > 0 else 0:,.0f} filas/seg

{CYAN}Abre tu dashboard en Grafana Cloud para ver los datos.{RESET}
""")


# ── Punto de entrada ──────────────────────────────────
if __name__ == "__main__":
    banner()
    config = load_config("config.yml")
    validate_config(config)
    filepath = get_csv_path()
    upload_csv(filepath, config)

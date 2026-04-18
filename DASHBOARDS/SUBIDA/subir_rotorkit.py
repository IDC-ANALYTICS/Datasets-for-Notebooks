import csv
import re
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
PORT         = 8086
INFLUX_URLS  = [          # se prueban en orden hasta que uno responda
    f"http://localhost:{PORT}",
    f"http://127.0.0.1:{PORT}",
]
TOKEN  = "UGXt9OG9R5k9BJcWQg7RmH7TD1oDHAfYguXT1LE1WzsUGpnpv-fc0xKPtMr1LXShSZx07GWQ93tdyiG9VMezjA=="
ORG    = "IDC Ingeniería de Confiabilidad S.A.S"
BUCKET = "rotorkit_data"
FILE   = r"D:\Datasets-for-Notebooks\PROYECTO INTEGRADOR UTP\Proyecto 1. Cuantificación de Desempeño — Desfibradora de Caña\DATA\Data_desf_processed.csv"
# ─────────────────────────────────────────────────────────────────────────────

BATCH_SIZE      = 2000   # lotes más pequeños → menos datos por timeout
TIMEOUT_MS      = 30_000 # 30 s por petición HTTP
MAX_RETRIES     = 2      # reintentos por lote antes de rendirse
RETRY_BASE_S    = 1      # espera base entre reintentos (se duplica cada vez)

_DATE_HINTS = re.compile(
    r"fecha|time|timestamp|date|hora|datetime",
    re.IGNORECASE,
)

_DATE_FORMATS = [
    None,
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%Y-%m-%dT%H:%M:%S",
]


def detect_encoding(path: str) -> str:
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with open(path, encoding=enc) as fh:
                fh.read(4096)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin-1"


def find_date_column(fields: list[str]) -> str | None:
    for col in fields:
        if _DATE_HINTS.search(col):
            return col
    return None


def parse_timestamp(value: str) -> datetime | None:
    value = value.strip()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass
    for fmt in _DATE_FORMATS[1:]:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def parse_float(val: str) -> float | None:
    try:
        return float(val.strip().replace(",", "."))
    except (ValueError, AttributeError):
        return None


def clean_col_name(col: str) -> str:
    return (
        col
        .replace("[", "")
        .replace("]", "")
        .replace("º", "deg")
        .replace("°", "deg")
        .replace(" ", "_")
        .strip("_")
    )


def write_with_retry(write_api, bucket: str, org: str, batch: list, batch_num: int):
    """Escribe un lote con reintentos y backoff exponencial."""
    wait = RETRY_BASE_S
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            write_api.write(bucket=bucket, org=org, record=batch)
            return  # éxito
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"  [Lote {batch_num}] FALLO permanente tras {MAX_RETRIES} intentos: {e}")
                raise
            print(f"  [Lote {batch_num}] Intento {attempt}/{MAX_RETRIES} falló ({e}). "
                  f"Reintentando en {wait}s...")
            time.sleep(wait)
            wait = min(wait * 2, 60)  # backoff exponencial, máx 60 s


def connect_influx() -> InfluxDBClient:
    """Prueba cada URL con timeout corto; usa la primera que responda."""
    last_err = None
    for url in INFLUX_URLS:
        print(f"Probando {url} ...", end=" ", flush=True)
        # Timeout de 3 s solo para el health-check; las escrituras usan TIMEOUT_MS
        probe = InfluxDBClient(url=url, token=TOKEN, org=ORG, timeout=3_000, retries=0)
        try:
            health = probe.health()
            probe.close()
            if health.status != "pass":
                print(f"no lista (status={health.status})")
                continue
            print(f"OK")
            return InfluxDBClient(url=url, token=TOKEN, org=ORG, timeout=TIMEOUT_MS, retries=0)
        except Exception as e:
            probe.close()
            print(f"sin respuesta")
            last_err = e
    raise ConnectionError(f"Ninguna URL respondió. Último error: {last_err}")


def main():
    encoding = detect_encoding(FILE)
    print(f"Encoding detectado: {encoding}")

    try:
        client = connect_influx()
    except ConnectionError as e:
        print(f"\nERROR: {e}")
        return

    write_api = client.write_api(write_options=SYNCHRONOUS)

    batch, total, errores, lotes_fallidos, batch_num = [], 0, 0, 0, 0

    with open(FILE, encoding=encoding, errors="replace") as f:
        sample = f.read(4096)
        f.seek(0)
        delimiter = ";" if sample.count(";") > sample.count(",") else ","

        reader = csv.DictReader(f, delimiter=delimiter)
        fields = reader.fieldnames or []

        date_col = find_date_column(fields)
        if date_col is None:
            print("ERROR: no se encontró columna de fecha/timestamp.")
            print(f"  Columnas disponibles: {fields}")
            return
        print(f"Columna de fecha detectada: '{date_col}' | Delimitador: '{delimiter}'")
        print(f"Batch size: {BATCH_SIZE} | Timeout HTTP: {TIMEOUT_MS//1000}s | Max reintentos: {MAX_RETRIES}\n")

        for i, row in enumerate(reader):
            try:
                raw_ts = row.get(date_col, "").strip()
                dt = parse_timestamp(raw_ts)
                if dt is None:
                    raise ValueError(f"Fecha no reconocida: '{raw_ts}'")

                field_dict = {}
                for col in fields:
                    if col == date_col:
                        continue
                    val = parse_float(row[col])
                    if val is not None:
                        field_dict[clean_col_name(col)] = val

                if not field_dict:
                    continue

                batch.append({
                    "measurement": "vibracion",
                    "time": dt,
                    "fields": field_dict,
                })

                if len(batch) >= BATCH_SIZE:
                    batch_num += 1
                    try:
                        write_with_retry(write_api, BUCKET, ORG, batch, batch_num)
                        total += len(batch)
                        print(f"  Lote {batch_num} OK — total subidos: {total} registros")
                    except Exception:
                        lotes_fallidos += 1
                    batch = []

            except Exception as e:
                errores += 1
                if errores <= 10:
                    print(f"  Fila {i+2} con error: {e}")

    # Último lote parcial
    if batch:
        batch_num += 1
        try:
            write_with_retry(write_api, BUCKET, ORG, batch, batch_num)
            total += len(batch)
            print(f"  Lote {batch_num} OK — total subidos: {total} registros")
        except Exception:
            lotes_fallidos += 1

    client.close()
    print(f"\n✅ Listo. {total} registros subidos. "
          f"{errores} filas con error de parseo. "
          f"{lotes_fallidos} lotes fallidos.")


if __name__ == "__main__":
    main()

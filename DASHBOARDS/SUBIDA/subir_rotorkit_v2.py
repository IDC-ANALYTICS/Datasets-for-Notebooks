import csv
from collections import defaultdict
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# ─── CONFIGURACION BASE ──────────────────────────────────────────────────────
URL = "http://localhost:8086"
TOKEN = ""
ORG = ""
BUCKET = ""
FILE = r""
# ─────────────────────────────────────────────────────────────────────────────

BATCH_SIZE = 5000  # puntos por lote
DEFAULT_MEASUREMENT = "datos_generales"

# Overrides por nombre exacto de columna (prioridad mas alta)
COLUMN_MEASUREMENT_OVERRIDES = {
    # "Velocidad": "rotacion",
    # "Temp Motor [C]": "temperatura",
}

# Reglas por tipo de variable (si no hay override)
# Cada tipo tiene palabras clave para detectar columnas por nombre.
COLUMN_TYPE_RULES = {
    "vibracion": ["vib", "acel", "mm/s", "g", "rms"],
    "temperatura": ["temp", "temperatura", "deg", "c"],
    "rotacion": ["rpm", "velocidad", "speed"],
    "presion": ["presion", "bar", "psi"],
}

# Mapeo tipo -> measurement final en Influx
MEASUREMENT_BY_TYPE = {
    "vibracion": "vibracion",
    "temperatura": "temperatura",
    "rotacion": "rotacion",
    "presion": "presion",
}

# Opcional: etiquetas estaticas para todos los puntos
COMMON_TAGS = {
    # "equipo": "rotorkit",
    # "planta": "linea_1",
}


def parse_float(value):
    if value is None:
        return None

    text = str(value).strip()
    if text == "":
        return None

    # Soporta formato decimal con coma.
    text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def clean_field_name(name):
    return (
        str(name)
        .replace("[", "")
        .replace("]", "")
        .replace("º", "deg")
        .replace("°", "deg")
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


def normalize_text(value):
    return value.lower().replace("_", " ")


def infer_variable_type(column_name):
    normalized = normalize_text(column_name)

    for var_type, keywords in COLUMN_TYPE_RULES.items():
        for keyword in keywords:
            if keyword.lower() in normalized:
                return var_type

    return None


def infer_measurement(column_name):
    # 1) Prioridad a override exacto
    if column_name in COLUMN_MEASUREMENT_OVERRIDES:
        return COLUMN_MEASUREMENT_OVERRIDES[column_name]

    # 2) Buscar por tipo de variable
    var_type = infer_variable_type(column_name)
    if var_type and var_type in MEASUREMENT_BY_TYPE:
        return MEASUREMENT_BY_TYPE[var_type]

    # 3) Fallback
    return DEFAULT_MEASUREMENT


def build_points_for_row(row, fieldnames):
    ts_raw = (row.get("Fecha") or "").strip()
    if not ts_raw:
        raise ValueError("La columna 'Fecha' esta vacia")

    dt = datetime.fromisoformat(ts_raw)

    # Agrupar fields por measurement
    fields_by_measurement = defaultdict(dict)

    for col in fieldnames:
        if col == "Fecha":
            continue

        val = parse_float(row.get(col))
        if val is None:
            continue

        measurement = infer_measurement(col)
        clean_col = clean_field_name(col)
        fields_by_measurement[measurement][clean_col] = val

    points = []
    for measurement, fields in fields_by_measurement.items():
        if not fields:
            continue

        point = {
            "measurement": measurement,
            "time": dt,
            "fields": fields,
        }

        if COMMON_TAGS:
            point["tags"] = COMMON_TAGS

        points.append(point)

    return points


def main():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    batch = []
    total_points = 0
    total_rows = 0
    errores = 0

    print("Leyendo archivo (v2)...")

    with open(FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = reader.fieldnames or []

        if "Fecha" not in fieldnames:
            raise ValueError("El CSV debe tener la columna 'Fecha'")

        for i, row in enumerate(reader, start=2):
            total_rows += 1
            try:
                points = build_points_for_row(row, fieldnames)
                if not points:
                    continue

                batch.extend(points)

                if len(batch) >= BATCH_SIZE:
                    write_api.write(bucket=BUCKET, org=ORG, record=batch)
                    total_points += len(batch)
                    print(f"  Subidos: {total_points} puntos (filas procesadas: {total_rows})")
                    batch = []

            except Exception as exc:
                errores += 1
                if errores <= 5:
                    print(f"  Fila {i} con error: {exc}")

    if batch:
        write_api.write(bucket=BUCKET, org=ORG, record=batch)
        total_points += len(batch)

    client.close()
    print(
        f"\nListo v2. {total_points} puntos subidos. "
        f"{total_rows} filas procesadas. {errores} filas con error."
    )


if __name__ == "__main__":
    main()

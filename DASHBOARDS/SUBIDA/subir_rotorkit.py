import csv
from datetime import datetime
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
URL    = "http://localhost:8086"
TOKEN  = ""
ORG    = ""
BUCKET = ""
FILE   = r""
# ─────────────────────────────────────────────────────────────────────────────

BATCH_SIZE = 5000  # filas por lote

def parse_float(val):
    try:
        return float(val.replace(",", "."))
    except:
        return None

def main():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    batch = []
    total = 0
    errores = 0

    print("Leyendo archivo...")

    with open(FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        fields = reader.fieldnames

        for i, row in enumerate(reader):
            try:
                # Timestamp
                ts = row["Fecha"].strip()
                # influxdb_client acepta ISO 8601 con timezone directamente
                dt = datetime.fromisoformat(ts)

                # Construir fields dict (todos los campos numéricos)
                field_dict = {}
                for col in fields:
                    if col == "Fecha":
                        continue
                    val = parse_float(row[col])
                    if val is not None:
                        # Limpiar nombre de campo: quitar caracteres especiales
                        clean_col = (col
                            .replace("[", "")
                            .replace("]", "")
                            .replace("º", "deg")
                            .replace(" ", "_"))
                        field_dict[clean_col] = val

                point = {
                    "measurement": "vibracion",
                    "time": dt,
                    "fields": field_dict
                }
                batch.append(point)

                if len(batch) >= BATCH_SIZE:
                    write_api.write(bucket=BUCKET, org=ORG, record=batch)
                    total += len(batch)
                    print(f"  Subidos: {total} registros...")
                    batch = []

            except Exception as e:
                errores += 1
                if errores <= 5:
                    print(f"  Fila {i+2} con error: {e}")

    # Subir el último lote
    if batch:
        write_api.write(bucket=BUCKET, org=ORG, record=batch)
        total += len(batch)

    client.close()
    print(f"\n✅ Listo. {total} registros subidos. {errores} filas con error.")

if __name__ == "__main__":
    main()

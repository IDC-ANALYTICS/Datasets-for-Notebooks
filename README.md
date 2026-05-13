# Diplomado en Analitica Aplicada al Sector Industrial

Repositorio academico para centralizar datasets, documentacion y entregables de proyectos aplicados al sector industrial.

## 1. Objetivo

Este repositorio organiza el material del diplomado por etapas de trabajo para que puedas:

- Ubicar rapidamente datos crudos, datos procesados y documentacion;
- reutilizar datasets en notebooks y ejercicios de modelado;
- consultar el contexto tecnico de cada proyecto integrador;
- desplegar entornos de visualizacion con InfluxDB + Grafana (local o cloud).

## 2. Estructura actual del repositorio

```text
Datasets-for-Notebooks/
├── README.md
├── DASHBOARDS/
│   ├── ENTORNO EN CLOUD/
│   │   ├── README.md
│   │   ├── config.yml
│   │   ├── requirements.txt
│   │   ├── setup.bat
│   │   └── upload_csv.py
│   ├── ENTORNO LOCAL/
│   │   ├── README.md
│   │   ├── config.yml
│   │   ├── docker-compose.yml
│   │   ├── requirements.txt
│   │   ├── setup.bat
│   │   ├── start.bat
│   │   ├── stop.bat
│   │   ├── upload_csv.py
│   │   └── grafana/provisioning/datasources/influxdb.yml
│   └── IMAGENES/
├── DATASETS CRUDOS - PRACTICA/
│   ├── Desfibradora_crudo.csv
│   └── Desfibradora_rejilla_temporal.csv
│   └── Turbogenerador_crudo.csv.csv
├── PREPROCESING - ROTORKIT/
│   ├── Rotorkit.csv
│   └── Variables_proceso.csv
├── PROYECTO INTEGRADOR UTP/
│   ├── Proyecto 1. Cuantificacion de Desempeno - Desfibradora de Cana/
│   │   ├── DATA/
│   │   └── DOCUMENTATION/
│   ├── Proyecto 2. Cuantificacion de Desempeno - Turbogenerador de Vapor/
│   │   ├── DATA/
│   │   └── DOCUMENTATION/
│   ├── Proyecto 4. Machine Learning para Clasificacion - BPC Estacion de Bombeo/
│   │   ├── DATA/
│   │   └── DOCUMENTATION/
│   ├── Proyecto 5. Deteccion de Anomalias - BPC Estacion de Bombeo/
│   │   ├── DATA/
│   │   └── DOCUMENTATION/
│   └── Proyecto 6. Clustering de Modos de Consumo Energetico/
│       ├── DATA/
│       └── DOCUMENTATION/
└── UNDERSTANDING - DESFIBRADORA Y PICADORA/
    ├── DATOS_DESFIBRADORA_CLEANED.csv
    └── DATOS_PICADORA_CLEANED.csv
```

## 3. Descripcion rapida por modulo

- DASHBOARDS: paquetes para cargar CSV a InfluxDB y visualizar en Grafana.
  - ENTORNO LOCAL: stack local con Docker (InfluxDB + Grafana).
  - ENTORNO EN CLOUD: carga a InfluxDB Cloud y visualizacion en Grafana Cloud.
- DATASETS CRUDOS - PRACTICA: datos fuente sin procesar para ejercicios de limpieza y transformacion.
- UNDERSTANDING - DESFIBRADORA Y PICADORA: datasets limpios para fase de entendimiento.
- PREPROCESING - ROTORKIT: datos y variables de referencia para preprocesamiento.
- PROYECTO INTEGRADOR UTP: casos aplicados por proyecto, con separacion entre datos y documentacion.

## 4. Ruta de uso recomendada


1. Comenzar con la lectura de los notebooks UNDERSTANDING y PREPROCESING para tener una noción de cómo trabajar variables y su limpieza.
2. Continuar con DATASETS CRUDOS - PRACTICA para aplicar la teoría aprendida.
3. Revisar PROYECTO INTEGRADOR UTP para analitica aplicada por caso de uso.
4. Si quieres tableros operativos, usar DASHBOARDS (local o cloud).

## 5. Guia de navegacion rapida

Si necesitas... usa esta ruta:

- Datos crudos para practicar: DATASETS CRUDOS - PRACTICA/
- datos limpios de desfibradora y picadora: UNDERSTANDING - DESFIBRADORA Y PICADORA/
- variables de proceso de Rotorkit: PREPROCESING - ROTORKIT/Variables_proceso.csv
- datasets finales por proyecto: PROYECTO INTEGRADOR UTP/<Proyecto>/DATA/
- fichas y entregables: PROYECTO INTEGRADOR UTP/<Proyecto>/DOCUMENTATION/
- levantar visualizacion local: DASHBOARDS/ENTORNO LOCAL/README.md
- visualizacion en la nube: DASHBOARDS/ENTORNO EN CLOUD/README.md

## 6. Convenciones de archivos

- Data_*_processed*.csv: datasets procesados listos para analisis.
- Entrega_Dataset_Proyecto*.pdf/.docx: documento de entrega tecnica por proyecto.
- Proyecto * - Ficha.pdf: resumen ejecutivo y contexto del caso.
- config.yml: parametros de carga de CSV hacia InfluxDB.

## 7. Notas importantes

- La carpeta DASHBOARDS contiene scripts y configuracion operativa. Sigue su README interno antes de ejecutar .bat o scripts de carga.
- Mantener consistencia entre org, bucket y token al usar InfluxDB (especialmente en entorno local).
- Evitar modificar nombres de columnas de tiempo en CSV sin ajustar config.yml.

## 8. Contacto

Carlos Camacho Castano  
Analista de Desarrollos Predictivos  
analyticscbm@idc-confiabilidad.com  
LinkedIn: https://linkedin.com/in/carlos-camacho-c-111a95286

---

Ultima actualizacion: 2026-05-07

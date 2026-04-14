# Diplomado en Analítica Aplicada al Sector Industrial

Repositorio académico que centraliza datasets, material documental y entregables de proyectos del diplomado. Este README funciona como punto de entrada único para comprender la estructura, el propósito de cada módulo y la forma recomendada de uso de los recursos.

## 1. Propósito del repositorio

Este repositorio está diseñado para:

- Organizar de forma trazable el material del diplomado por fases de trabajo analítico.
- Conectar fundamentos de preparación de datos con proyectos aplicados en contexto industrial.
- Facilitar la reutilización de datasets procesados para análisis descriptivo, modelado y validación de resultados.
- Servir como evidencia técnica y documental del avance de cada proyecto.

En términos prácticos, aquí conviven dos tipos de activos:

- Activos de datos: archivos CSV y XLSX para análisis cuantitativo.
- Activos de soporte: fichas, entregas y documentación metodológica en PDF/DOCX.

## 2. Audiencia y cómo aprovecharlo

Este repositorio es útil para:

- Estudiantes del diplomado que necesitan una guía clara de dónde está cada material.
- Docentes o tutores que requieren revisar entregables por proyecto.
- Profesionales industriales que desean replicar ejercicios de analítica aplicada.

Ruta sugerida de lectura:

1. Revisar módulos de entendimiento y preprocesamiento.
2. Avanzar a proyectos integradores por caso de uso.
3. Consultar documentación de cada proyecto para interpretar contexto, alcance y criterios.

## 3. Estructura general del repositorio (índice jerárquico)

```text
Datasets-for-Notebooks/
├── gitignore
├── PREPROCESING - ROTORKIT/
│   ├── Notebooks Preprocesing.pdf
│   ├── Rotorkit.csv
│   └── Variables_proceso.csv
├── UNDERSTANDING - DESFIBRADORA Y PICADORA/
│   ├── DATOS_DESFIBRADORA_CLEANED.csv
│   ├── DATOS_PICADORA_CLEANED.csv
│   └── Notebooks Preprocesing.pdf
└── PROYECTO INTEGRADOR UTP/
    ├── Proyecto 1. Cuantificación de Desempeño — Desfibradora de Caña/
    │   ├── DATA/
    │   │   ├── Data_desf_processed.csv
    │   │   ├── Data_desf_processed_2.csv
    │   │   └── Pesos Ponderados - Proyecto1.xlsx
    │   └── DOCUMENTATION/
    │       ├── Entrega_Dataset_Proyecto1.docx
    │       ├── Entrega_Dataset_Proyecto1.pdf
    │       └── Proyecto 1 - Ficha.pdf
    ├── Proyecto 2. Cuantificación de Desempeño — Turbogenerador de Vapor/
    │   ├── DATA/
    │   │   ├── Data_turbine_processed.csv
    │   │   ├── Data_turbine_processed_2.csv
    │   │   └── Pesos Ponderados - Proyecto2.xlsx
    │   └── DOCUMENTATION/
    │       ├── Entrega_Dataset_Proyecto2.docx
    │       ├── Entrega_Dataset_Proyecto2.pdf
    │       └── Proyecto 2 - Ficha.pdf
    ├── Proyecto 4. Machine Learning para Clasificación — BPC  Estación de Bombeo/
    │   ├── DATA/
    │   │   ├── Data_BPC_processed.csv
    │   │   ├── Entrega_Dataset_Proyecto4.docx
    │   │   └── Pesos Ponderados - Proyecto4.xlsx
    │   └── DOCUMENTATION/
    │       ├── Entrega_Dataset_Proyecto4.pdf
    │       └── Proyecto 4 - Ficha.pdf
    ├── Proyecto 5. Detección de Anomalías — BPC Estación de Bombeo/
    │   ├── DATA/
    │   │   ├── Data_BPC_processed.csv
    │   │   └── Pesos Ponderados - Proyecto5.xlsx
    │   └── DOCUMENTATION/
    │       ├── Entrega_Dataset_Proyecto5.docx
    │       ├── Entrega_Dataset_Proyecto5.pdf
    │       └── Proyecto 5 - Ficha.pdf
    └── Proyecto 6. Clustering de Modos de Consumo Energético/
        ├── DATA/
        │   ├── Data_EBR_processed.csv
        │   └── Pesos Ponderados - Proyecto6.xlsx
        └── DOCUMENTATION/
            ├── Entrega_Dataset_Proyecto6.docx
            ├── Entrega_Dataset_Proyecto6.pdf
            └── Proyecto 6 - Ficha.pdf
```

## 4. ¿Qué contiene cada módulo y por qué existe?

### 4.1 PREPROCESING - ROTORKIT

Propósito:

- Consolidar insumos de preprocesamiento para el entorno Rotorkit.
- Definir variables de proceso y base de datos inicial para estandarizar etapas posteriores.

Contenido típico del módulo:

- `Rotorkit.csv`: dataset base del proceso.
- `Variables_proceso.csv`: diccionario o lista de variables de interés operativo.
- `Notebooks Preprocesing.pdf`: soporte metodológico del tratamiento de datos.

Relación con otros módulos:

- Alimenta las decisiones de limpieza y selección de variables en proyectos integradores.
- Sirve como referencia para asegurar consistencia entre casos.

### 4.2 UNDERSTANDING - DESFIBRADORA Y PICADORA

Propósito:

- Fase de entendimiento de datos para dos equipos industriales (desfibradora y picadora).
- Proveer versiones limpias listas para análisis exploratorio y modelado.

Contenido del módulo:

- `DATOS_DESFIBRADORA_CLEANED.csv`.
- `DATOS_PICADORA_CLEANED.csv`.
- Documento de preprocesamiento para trazabilidad.

Relación con otros módulos:

- Funciona como puente entre diagnóstico inicial y proyectos de cuantificación de desempeño.

### 4.3 PROYECTO INTEGRADOR UTP

Propósito:

- Reunir los casos aplicados del diplomado con estructura uniforme por proyecto.
- Separar datos (`DATA`) de soporte técnico (`DOCUMENTATION`) para facilitar revisión.

Patrón estructural por proyecto:

- `DATA`: datasets procesados y archivos auxiliares de ponderación.
- `DOCUMENTATION`: fichas de proyecto y entregables narrativos.

Interpretación de la secuencia de proyectos:

- Proyecto 1 y 2: cuantificación de desempeño (métrica operativa y evaluación comparativa).
- Proyecto 4: clasificación con machine learning (predicción de clases/estados).
- Proyecto 5: detección de anomalías (identificación de comportamientos atípicos).
- Proyecto 6: clustering de consumo energético (segmentación de modos de operación).

## 5. Guía de navegación rápida

Si necesitas... usa esta ruta:

- Iniciar el análisis desde datos crudos (fase Understanding): ir a `UNDERSTANDING - DESFIBRADORA Y PICADORA/`.
- Dejar la data lista para analizar (fase Preprocesing): ir a `PREPROCESING - ROTORKIT/Variables_proceso.csv`.
- Revisar datos listos para modelado por caso: ir a `PROYECTO INTEGRADOR UTP/<Proyecto>/DATA/`.
- Consultar objetivos, alcance y entregables: ir a `PROYECTO INTEGRADOR UTP/<Proyecto>/DOCUMENTATION/`.

Convención útil para orientarte:

- Archivos `Data_*_processed*.csv`: versiones procesadas para análisis.
- Archivos `Pesos Ponderados - Proyecto*.xlsx`: ponderaciones o criterios de evaluación.
- Archivos `Proyecto * - Ficha.pdf`: resumen ejecutivo/técnico del caso.
- Archivos `Entrega_Dataset_Proyecto*`: descripción formal del dataset y su entrega.

## 6. Cómo usar los recursos de forma práctica

### 6.1 Datasets CSV

Uso recomendado:

1. Cargar en entorno de análisis.
2. Validar tipos de datos, nulos y unidades.
3. Replicar o adaptar el flujo analítico del proyecto.

Ejemplo mínimo en Python:

```python
import pandas as pd

df = pd.read_csv("PROYECTO INTEGRADOR UTP/Proyecto 2. Cuantificación de Desempeño — Turbogenerador de Vapor/DATA/Data_turbine_processed.csv")
print(df.head())
print(df.info())
```

### 6.2 Archivos XLSX de pesos ponderados

Uso recomendado:

- Interpretar criterios de ponderación para métricas de desempeño.
- Validar cómo se priorizan variables o indicadores por proyecto.
- Reproducir cálculos en Python o Excel antes de comparar resultados.

### 6.3 Documentación PDF/DOCX

Uso recomendado:

- Leer primero la ficha de proyecto para entender objetivo, alcance y contexto industrial.
- Luego contrastar con dataset y ponderaciones para reconstruir la lógica analítica completa.

---

En caso de dudas, inquietudes o sugerencias, contactar a:

CARLOS CAMACHO CASTAÑO  
Analista de Desarrollos Predictivos  
analyticscbm@idc-confiabilidad.com

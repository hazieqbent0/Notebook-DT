# Digital Twin Data Pipeline & Visualization

A set of Jupyter notebooks and supporting configs that build up an end-to-end digital twin data pipeline: generating/loading digital twin data, transmitting it over HTTP REST and MQTT, persisting it in a time-series store (with Kafka as a stream manager), visualizing it in Grafana, and training/validating classification and regression AI models on lab data.

## Overview

Each notebook in this repo tackles one stage of a digital twin's data lifecycle. Together they demonstrate a full loop: **generate → transmit → store → visualize → model**.

| # | Notebook | Stage |
|---|----------|-------|
| 1 | `01_data_transmission.ipynb` | Load digital twin data and transmit/receive it over HTTP REST and MQTT |
| 2 | `02_data_storage.ipynb` | Store and retrieve digital twin state and sensor streams (time-series DB + Kafka) |
| 3 | Grafana dashboards (`grafana/`) | Visualize time series with periodic aggregation/transformation |
| 4 | NVIDIA Omniverse scene (`omniverse/`) | 3D visualization of digital twin state (translation/orientation) |
| 5 | `03_ai_models.ipynb` | Train and validate classification and regression models |

## 1. Data Transmission — `01_data_transmission.ipynb`

**Goal:** Load two types of digital twin–relevant data (e.g. numeric sensor readings and spatial coordinates/pose data) and demonstrate that both can be transmitted and received reliably.

**What it covers:**
- **Data format justification** — why each data type (numeric time series vs. structured coordinate/pose data) is represented the way it is (e.g. JSON payloads with timestamp, source ID, units, and schema versioning) so it's directly usable by a digital twin state store.
- **HTTP REST demo** — two independent data sources asynchronously POST/PUT updates to a REST endpoint (built with FastAPI/Flask), simulating out-of-band, on-demand digital twin updates. A client polls/fetches (GET) to confirm receipt.
- **MQTT demo** — two independent data sources publish to separate topics on a broker (e.g. Mosquitto/HiveMQ) at fixed intervals, simulating continuous sensor streaming; subscribers consume the stream in real time.
- **Parallel transmission & verification** — all four sources (2 REST + 2 MQTT) run concurrently (via `asyncio`/threading), and received payloads are checksummed/compared against what was sent to verify correctness (no data loss, no corruption, correct ordering).
- Data can be randomly generated (with reproducible seeds) or loaded from pre-saved sample files (CSV/JSON) included in `data/`.

## 2. Data Storage — `02_data_storage.ipynb`

**Goal:** Set up a persistent store for digital twin state and sensor history, and prove state variables can be written and read back correctly.

**What it covers:**
- **Digital twin state variable design** — definition and justification of state variables (e.g. position, orientation, temperature, operational status, last-update timestamp) that represent the twin's condition at any point in time.
- **Store setup** — a time-series database (e.g. InfluxDB/TimescaleDB) for high-frequency sensor streams, alongside a simple key-value/document store for discrete state variables.
- **Update/retrieve demo** — multiple state variables and sensor streams are written and then queried back, with results compared to the source data to confirm correctness.
- **Kafka as stream manager** — sensor streams are published to Kafka topics and consumed into the time-series store, decoupling producers (sensors/REST/MQTT sources) from the storage layer and demonstrating a production-style ingestion pipeline.

## 3. Visualization — Grafana

**Goal:** Visualize digital twin data over time, with periodic refresh sourced from the store built in notebook 2.

**What it covers:**
- Dashboards for **at least two different time series** (e.g. one sensor stream, one digital twin state variable).
- **At least two aggregations/transformations** per series (e.g. moving average, min/max/mean over a rolling window, rate of change).
- Each panel documents its **data source** (which store/table/measurement it reads from) so the digital twin vs. sensor-stream origin is traceable.
- **Update period justification** — the dashboard refresh interval is chosen and justified against the underlying write frequency of the data source (with evidence, e.g. comparing write timestamps to panel refresh timestamps) so updates are neither too sparse nor wastefully frequent.

## 4. 3D Visualization — NVIDIA Omniverse

**Goal:** Drive a 3D object's transform in Omniverse from live digital twin state.

**What it covers:**
- A scene with one object whose **translation and orientation** are bound to state variables (position/rotation) held in the data store.
- A connector/script that polls or subscribes to the store and pushes updates into the USD stage.
- Verification that the visualized transform matches the source data at each update (source values are logged alongside screenshots/recordings to prove correctness).

## 5. AI Models — `03_ai_models.ipynb`

**Goal:** Train and validate one classification model and one regression model using the Self Guided Lab dataset(s).

**What it covers:**
- **Train/validation split** — a proper hold-out or k-fold cross-validation split, stratified where appropriate for the classification task.
- **Classification model** — training, cross-validation, and evaluation using metrics such as accuracy, precision/recall, F1, and confusion matrix.
- **Regression model** — training, cross-validation, and evaluation using metrics such as RMSE, MAE, and R².
- **Interpretation** — a comparison of performance measures across folds/models, discussing what the metrics imply about generalization, bias/variance trade-offs, and any tuning decisions.

## Repository Structure

```
.
├── 01_data_transmission.ipynb
├── 02_data_storage.ipynb
├── 03_ai_models.ipynb
├── data/                  # pre-saved sample data (CSV/JSON)
├── grafana/               # dashboard JSON exports, provisioning configs
├── omniverse/             # USD scene + connector script
├── docker-compose.yml     # brokers/DBs used across notebooks (MQTT, Kafka, InfluxDB, Grafana)
└── README.md
```

## Tech Stack

- **Transmission:** HTTP REST (FastAPI/Flask), MQTT (Paho-MQTT, Mosquitto broker)
- **Storage:** Time-series DB (InfluxDB/TimescaleDB), Kafka
- **Visualization:** Grafana, NVIDIA Omniverse
- **Modeling:** scikit-learn (classification + regression)
- **Language:** Python 3, Jupyter Notebook

## Getting Started

1. Clone the repo and install dependencies: `pip install -r requirements.txt`
2. Start supporting services: `docker-compose up -d` (spins up MQTT broker, Kafka, and the time-series DB)
3. Run notebooks in order: `01_data_transmission.ipynb` → `02_data_storage.ipynb` → `03_ai_models.ipynb`
4. Import dashboards from `grafana/` into a running Grafana instance pointed at the time-series DB
5. Open the Omniverse scene in `omniverse/` and run the connector script to see live state updates

## License

MIT (or update to match your course/institution requirements).

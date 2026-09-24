# Digital Twin Pipeline: Grafana + Omniverse

One data store (InfluxDB), two consumers: a Grafana dashboard and an
Omniverse 3D visualization. Both read the same `twin_data` bucket that
`simulator.py` writes to.

```
simulator.py  --writes-->  InfluxDB (twin_data bucket)
                                |--> sensor_data  (temperature, vibration)
                                |--> twin_state   (x, y, z, yaw)
                                        |
                                        |--> Grafana dashboard (reads via Flux)
                                        |--> Omniverse script (polls via Flux)
```

## 1. Start the data store + Grafana

```bash
cd digital-twin-pipeline
docker compose up -d
```

This starts:
- **InfluxDB** on `localhost:8086` (org `digitaltwin`, bucket `twin_data`,
  admin token `my-super-secret-token` - already baked into all the scripts
  so nothing else to configure)
- **Grafana** on `localhost:3000` (login `admin` / `admin`), with the
  InfluxDB datasource and the dashboard already auto-provisioned from
  `grafana/provisioning/` and `grafana/dashboards/`.

## 2. Run the simulator

```bash
pip install -r requirements.txt
python simulator.py
```

This writes a new point to `sensor_data` and `twin_state` every
`WRITE_INTERVAL = 1.0s`. Leave it running.

## 3. View the Grafana dashboard

Open `http://localhost:3000`, find **"Digital Twin - Sensor Dashboard"**.
You should see 5 live panels:

| Panel | Source | What it shows |
|---|---|---|
| Raw Temperature | `sensor_data.temperature` | Time series 1 (raw) |
| Raw Vibration | `sensor_data.vibration` | Time series 2 (raw) |
| Temperature - 10s Moving Average | `sensor_data.temperature` | Aggregation 1 (`aggregateWindow(fn: mean)`) |
| Vibration - 10s Max | `sensor_data.vibration` | Aggregation 2 (`aggregateWindow(fn: max)`) |
| Digital Twin Position | `twin_state.x/y/z` | The digital twin state stream, shown separately from sensor data to make the two source types explicit |

The dashboard is set to **refresh every 5s**.

## 4. Drive the Omniverse object

1. Open Omniverse (Code, or your built `kit-app-template` app).
2. Create a Cube at `/World/TwinObject` (Create > Mesh > Cube, rename/move it).
3. Open the Script Editor and paste in `omniverse_update_twin.py`, then run it.
4. Watch the cube orbit and spin as `simulator.py` keeps writing new
   `twin_state` points - it's reading the identical rows Grafana's bottom
   panel is charting.

## Justifying the update period (for the rubric)

- `simulator.py` writes new data every **1s** (`WRITE_INTERVAL`).
- Grafana is set to refresh every **5s** - by Nyquist-style reasoning you
  only need to poll at roughly the same rate data arrives to avoid staleness;
  5s keeps the dashboard visibly current without hammering InfluxDB with
  needless queries (5x fewer requests than polling every 1s, with at most
  ~5s of staleness, which is imperceptible against the ~200s period of the
  simulated temperature/position cycles).
- The Omniverse script polls every **1s** (`POLL_INTERVAL`), matching the
  write interval exactly, since smooth animation needs tighter sync than a
  glance-able dashboard does.
- For your notebook: capture a screenshot/plot comparing data timestamp vs.
  panel refresh timestamp (Grafana's panel inspector shows query execution
  time) to show the actual observed staleness matches this reasoning - that's
  your "evidence," not just the assertion.

## Rubric mapping

- **Grafana (Skilled tier)**: dashboard shows aggregation (mean) AND
  transformation... two panels labeled `(AGGREGATION)` with different `fn`
  cover the "2 different aggregations/transformations" requirement; raw
  temperature + raw vibration cover "2 different time series."
- **Omniverse (Skilled tier)**: `apply_transform()` updates both translate
  AND rotate ops each poll, sourced from the same store, satisfying "update
  of object properties in animation from a data store."
- **Visualization update (Skilled tier)**: both consumers poll on a fixed,
  justified interval tied to `WRITE_INTERVAL` - document the reasoning above
  plus a screenshot as your evidence.

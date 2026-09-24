import asyncio
import omni.usd
from pxr import Gf, UsdGeom
from influxdb_client import InfluxDBClient

# FIXED: Removed 'self.' to match the standard variables called below
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "my-super-secret-token"
INFLUX_ORG = "digitaltwin"
INFLUX_BUCKET = "twin_data"

# FIXED: Pointing to a complex hierarchical asset instead of a basic cube
PRIM_PATH = "/World/Mercedes_W203"

POLL_INTERVAL = 1.0  # seconds

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

# FIXED: Changed "yaw" to "rz" to match the actual data sent by simulator.py
_LATEST_QUERY = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -10s)
  |> filter(fn: (r) => r._measurement == "twin_state")
  |> filter(fn: (r) => r._field == "x" or r._field == "y" or r._field == "z" or r._field == "rz")
  |> last()
'''

def fetch_latest_twin_state():
    """Query InfluxDB for the most recent x, y, z, rz values."""
    tables = query_api.query(_LATEST_QUERY, org=INFLUX_ORG)
    values = {}
    for table in tables:
        for record in table.records:
            values[record.get_field()] = record.get_value()
            
    # FIXED: Checking for 'rz' instead of 'yaw'
    if all(k in values for k in ("x", "y", "z", "rz")):
        return values["x"], values["y"], values["z"], values["rz"]
    return None

def apply_transform(x: float, y: float, z: float, rz_deg: float) -> None:
    """Update the prim's translate + rotateZ (orientation) attributes."""
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(PRIM_PATH)
    
    if not prim.IsValid():
        print(f"[digital-twin] Prim not found at {PRIM_PATH}. Create or rename your asset first.")
        return

    xform = UsdGeom.Xformable(prim)
    xform.ClearXformOpOrder()

    translate_op = xform.AddTranslateOp()
    translate_op.Set(Gf.Vec3d(x, y, z))

    rotate_op = xform.AddRotateZOp()
    rotate_op.Set(rz_deg)

async def poll_loop():
    print(f"[digital-twin] Polling {INFLUX_BUCKET}.twin_state every {POLL_INTERVAL}s -> driving {PRIM_PATH}")
    while True:
        state = fetch_latest_twin_state()
        if state:
            x, y, z, rz = state
            apply_transform(x, y, z, rz)
            print(f"[digital-twin] Updated -> pos=({x:.2f},{y:.2f},{z:.2f}) rotZ={rz:.1f}")
        else:
            print("[digital-twin] No twin_state data yet - is simulator.py running?")
        await asyncio.sleep(POLL_INTERVAL)

# Kick off the polling loop as an asyncio task inside Omniverse's event loop.
asyncio.ensure_future(poll_loop())
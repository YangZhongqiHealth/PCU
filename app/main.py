import sys
from pathlib import Path

# Add parent directory to path so we can import pcu
sys.path.insert(0, str(Path(__file__).parent.parent))

from pcu.system import build_pcu_system, PCUSystem

def run_once():
    system: PCUSystem = build_pcu_system()
    system.start()

    # Example: send one sensor packet to kick the pipeline
    ingestion = system.nodes["ingestion"]
    ingestion.ingest_sensor_packet({
        "user_id": "u123",
        "stream_id": "watch.hr",
        "value": 72,
        "unit": "bpm"
    })

    # Drive the in-memory bus once (synchronous)
    system.tick()

    system.stop()

if __name__ == "__main__":
    run_once()

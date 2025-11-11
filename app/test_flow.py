"""
Minimal functional test for the PCU skeleton.

This simulates one sensor reading (heart rate = 72 bpm)
and tracks how it moves through the PCU layers:
Ingestion -> Personicle -> State -> Context -> Guidance -> Safety -> Orchestrator -> Interface
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import pcu
sys.path.insert(0, str(Path(__file__).parent.parent))

from pcu.system import build_pcu_system, PCUSystem
from pcu.core.topics import Topic
from pcu.core.message import Message


def attach_dummy_behaviors(system: PCUSystem):
    """Monkey-patch simple print behaviors so we can visualize message flow."""

    def wrap(node_name, func):
        def wrapper(msg: Message):
            print(f"[{node_name}] received {msg.topic.value} payload={msg.payload}")
            func(msg)
        return wrapper

    # --- PersonicleNode: transforms sensor → event ---
    personicle = system.nodes["personicle"]
    def personicle_logic(msg):
        event_payload = {"event": "hr_measurement", "avg_hr": msg.payload["value"]}
        system.bus.publish(Message(topic=Topic.EVENTS, payload=event_payload))
    personicle.on_message = wrap("Personicle", personicle_logic)

    # --- StateNode: transforms event → state vector ---
    state = system.nodes["state"]
    def state_logic(msg):
        if msg.topic == Topic.EVENTS:
            # Process events from PersonicleNode
            state_payload = {"phys_state": {"heart_rate": msg.payload["avg_hr"], "status": "normal"}}
            system.bus.publish(Message(topic=Topic.STATE, payload=state_payload))
        elif msg.topic == Topic.RAW_SENSORS:
            # Optionally handle raw sensors directly (if needed)
            # For now, just skip since PersonicleNode will transform it
            pass
    # FEEDBACK messages can be ignored for this test
    # --- ContextNode: adds context info ---
    context = system.nodes["context"]
    def context_logic(msg):
        context_payload = {"context": "resting", "goal": "stay healthy"}
        system.bus.publish(Message(topic=Topic.CONTEXT, payload=context_payload))
    context.on_message = wrap("Context", context_logic)

    # --- GuidanceNode: creates guidance plan ---
    guidance = system.nodes["guidance"]
    def guidance_logic(msg):
        plan = {"nudge": "Take a short walk to improve circulation."}
        system.bus.publish(Message(topic=Topic.GUIDANCE_PLAN, payload=plan))
    guidance.on_message = wrap("Guidance", guidance_logic)

    # --- SafetyNode: forwards if safe ---
    safety = system.nodes["safety"]
    def safety_logic(msg):
        proposal = {"safe_nudge": msg.payload["nudge"]}
        system.bus.publish(Message(topic=Topic.ORCH_PROPOSAL, payload=proposal))
    safety.on_message = wrap("Safety", safety_logic)

    # --- OrchestratorNode: final decision ---
    orchestrator = system.nodes["orchestrator"]
    def orch_logic(msg):
        # Only process ORCH_PROPOSAL messages from SafetyNode
        if msg.topic != Topic.ORCH_PROPOSAL:
            return  # Ignore CONTEXT, STATE, and FEEDBACK messages
        
        decision = {"final_action": msg.payload["safe_nudge"]}
        system.bus.publish(Message(topic=Topic.GUIDANCE_OUT, payload=decision))
    # --- InterfaceNode: delivers to user ---
    interface = system.nodes["interface"]
    def interface_logic(msg):
        print(f"[Interface] Delivered guidance: {msg.payload['final_action']}")
    interface.on_message = wrap("Interface", interface_logic)


def run_minimal_flow():
    system: PCUSystem = build_pcu_system()
    system.start()
    attach_dummy_behaviors(system)

    # Inject a fake sensor packet
    ingestion = system.nodes["ingestion"]
    ingestion.ingest_sensor_packet({
        "user_id": "u123",
        "stream_id": "watch.hr",
        "value": 72,
        "unit": "bpm"
    })
    print("Ingested sensor packet")
    # Route all pending messages
    system.tick()
    print("Driven the in-memory bus")
    system.stop()
    print("Stopped the system")


if __name__ == "__main__":
    run_minimal_flow()

from dataclasses import dataclass
from typing import Dict
from ..core.bus import InMemoryBus
from ..core.node import Node
from ..core.validator import DataflowValidator
from ..nodes import (
    IngestionNode, PersonicleNode, StateNode, KBNode, ContextNode,
    GuidanceNode, SafetyNode, OrchestratorNode, InterfaceNode,
    ObservabilityNode, AgentNode
)

@dataclass
class PCUSystem:
    """Encapsulates the PCU runtime: bus, nodes, lifecycle helpers."""
    bus: InMemoryBus
    nodes: Dict[str, Node]

    def start(self) -> None:
        for n in self.nodes.values():
            n.start()

    def stop(self) -> None:
        for n in self.nodes.values():
            n.stop()

    def tick(self) -> None:
        """Drive the in-memory bus (for local mode/testing)."""
        self.bus.route()

    def validate(self) -> None:
        """Run the dataflow validator and raise if critical issues exist."""
        issues = DataflowValidator(self.nodes, self.bus).validate()
        errors = [i for i in issues if i.level == "ERROR"]
        if errors:
            lines = [f"[{i.level}] {i.code}: {i.detail}" for i in issues]
            raise RuntimeError("Dataflow validation failed:\n" + "\n".join(lines))
        # Optionally log warnings
        for i in issues:
            if i.level == "WARN":
                print(f"[WARN] {i.code}: {i.detail}")

def build_pcu_system() -> PCUSystem:
    bus = InMemoryBus()

    # Instantiate all layers
    ingestion = IngestionNode("ingestion", bus)
    personicle = PersonicleNode("personicle", bus)
    state = StateNode("state", bus)
    kb = KBNode("kb", bus)
    context = ContextNode("context", bus)
    guidance = GuidanceNode("guidance", bus, kb=kb)
    safety = SafetyNode("safety", bus)
    orchestrator = OrchestratorNode("orchestrator", bus)
    interface = InterfaceNode("interface", bus)
    observability = ObservabilityNode("observability", bus)

    # Domain agents
    agent_sleep = AgentNode("agent.sleep", bus, "sleep")
    agent_activity = AgentNode("agent.activity", bus, "activity")
    agent_mood = AgentNode("agent.mood", bus, "mood")
    orchestrator.register_agent(agent_sleep)
    orchestrator.register_agent(agent_activity)
    orchestrator.register_agent(agent_mood)

    nodes = {
        n.name: n for n in [
            ingestion, personicle, state, kb, context,
            guidance, safety, orchestrator, interface,
            observability, agent_sleep, agent_activity, agent_mood
        ]
    }

    system = PCUSystem(bus=bus, nodes=nodes)

    # Register subscriptions now so the validator can inspect them
    system.start()
    try:
        # Run validation to ensure all declared outputs have consumers, etc.
        system.validate()
    finally:
        # Keep system running in real usage; stop for a clean builder example
        system.stop()

    return system

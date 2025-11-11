from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from .node import Node
from .topics import Topic
from .bus import InMemoryBus

@dataclass
class DataflowIssue:
    level: str   # "ERROR" or "WARN"
    code: str    # e.g., "UNSUBSCRIBED_OUTPUT"
    detail: str  # human-readable description

class DataflowValidator:
    """
    Validates wiring and discoverability:
      1) Each node's declared inputs are actually subscribed.
      2) Each declared output has at least one subscriber (no dead-ends),
         except for permitted sink topics (e.g., AUDIT).
      3) Basic reachability along the main spine.
    """
    SINK_TOPICS: Set[Topic] = {Topic.AUDIT}

    def __init__(self, nodes: Dict[str, Node], bus: InMemoryBus) -> None:
        self.nodes = nodes
        self.bus = bus

    def validate(self) -> List[DataflowIssue]:
        issues: List[DataflowIssue] = []

        # 1) Inputs are subscribed (the bus should know every input topic->node)
        actual_subs = self.bus.subscriptions  # Topic -> [Node]
        for node in self.nodes.values():
            for t in node.inputs:
                if node not in actual_subs.get(t, []):
                    issues.append(DataflowIssue(
                        "ERROR", "MISSING_SUBSCRIPTION",
                        f"{node.name} declares input {t} but is not subscribed."
                    ))

        # Create a reverse map: topic -> list of nodes that declare it in outputs
        output_decls: Dict[Topic, List[str]] = {}
        for node in self.nodes.values():
            for t in node.outputs:
                output_decls.setdefault(t, []).append(node.name)

        # 2) Outputs must have at least one subscriber unless it's a sink
        for topic, producers in output_decls.items():
            if topic in self.SINK_TOPICS:
                continue
            subscribers = actual_subs.get(topic, [])
            if not subscribers:
                issues.append(DataflowIssue(
                    "ERROR", "UNSUBSCRIBED_OUTPUT",
                    f"Topic {topic} produced by {producers} has no subscribers."
                ))

        # 3) Quick reachability check for main lineage (optional, conservative)
        # Define a minimal expected path: RAW_SENSORS -> EVENTS -> STATE -> CONTEXT -> GUIDANCE_PLAN -> ORCH_DECISION/GUIDANCE_OUT
        required_chain: List[Topic] = [
            Topic.RAW_SENSORS, Topic.EVENTS, Topic.STATE, Topic.CONTEXT, Topic.GUIDANCE_PLAN
        ]
        for i in range(len(required_chain) - 1):
            a, b = required_chain[i], required_chain[i+1]
            if not actual_subs.get(b):
                issues.append(DataflowIssue(
                    "WARN", "FRAGILE_CHAIN",
                    f"No subscribers for {b}; chain {a} -> {b} may be broken."
                ))

        return issues

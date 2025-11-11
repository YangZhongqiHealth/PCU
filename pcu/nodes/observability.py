from typing import List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class ObservabilityNode(Node):
    """Collects AUDIT telemetry and pushes to logging/metrics stores."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.OBSERVABILITY, bus)

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.AUDIT]

    @property
    def outputs(self) -> List[Topic]:
        return []

    def on_message(self, msg: Message) -> None:
        # TODO: ship to observability backend.
        pass

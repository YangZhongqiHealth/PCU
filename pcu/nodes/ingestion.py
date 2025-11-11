from typing import Dict, Any, List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class IngestionNode(Node):
    """Collects raw multimodal data and publishes standardized packets."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.INGEST, bus)

    @property
    def inputs(self) -> List[Topic]:
        return []  # no upstream inputs

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.RAW_SENSORS, Topic.AUDIT]

    def on_message(self, msg: Message) -> None:
        # Ingestion is event-driven by external API calls, not by subscribed topics.
        pass

    def ingest_sensor_packet(self, payload: Dict[str, Any]) -> None:
        """External entrypoint: push normalized sensor packet onto the bus."""
        self.bus.publish(Message(topic=Topic.RAW_SENSORS, payload=payload, provenance={"node": self.name}))

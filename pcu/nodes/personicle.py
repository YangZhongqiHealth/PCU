from typing import List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class PersonicleNode(Node):
    """Transforms continuous streams into discrete life events."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.PERSONICLE, bus)

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.RAW_SENSORS]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.EVENTS, Topic.AUDIT]

    def on_message(self, msg: Message) -> None:
        # TODO: detect events (e.g., sleep, meals) from raw streams, then publish EVENTS.
        pass

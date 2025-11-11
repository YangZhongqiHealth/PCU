from typing import List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class StateNode(Node):
    """Maintains user physiological/behavioral/emotional state."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.STATE, bus)

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.EVENTS, Topic.RAW_SENSORS, Topic.FEEDBACK]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.STATE, Topic.AUDIT]

    def on_message(self, msg: Message) -> None:
        # TODO: update and publish latent state vector.
        pass

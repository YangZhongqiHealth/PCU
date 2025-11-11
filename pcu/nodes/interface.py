from typing import List, Dict, Any
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class InterfaceNode(Node):
    """Delivers messages to user/caregiver and collects feedback."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.INTERFACE, bus)

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.GUIDANCE_OUT, Topic.ORCH_DECISION]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.FEEDBACK, Topic.AUDIT]

    def on_message(self, msg: Message) -> None:
        # TODO: push to UI; may emit FEEDBACK asynchronously later.
        pass

    def submit_feedback(self, payload: Dict[str, Any]) -> None:
        self.bus.publish(Message(topic=Topic.FEEDBACK, payload=payload, provenance={"node": self.name}))

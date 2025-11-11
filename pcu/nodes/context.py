from typing import List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class ContextNode(Node):
    """Infers situation, goals, interruptibility, risk; may query KB."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.CONTEXT, bus)

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.STATE, Topic.EVENTS, Topic.RAW_SENSORS, Topic.FEEDBACK]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.CONTEXT, Topic.AUDIT, Topic.KB_QUERY]

    def on_message(self, msg: Message) -> None:
        # TODO: infer context and optionally publish KB_QUERY.
        pass

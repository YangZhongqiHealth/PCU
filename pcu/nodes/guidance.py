from typing import List, Optional
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message
from .kb import KBNode

class GuidanceNode(Node):
    """Generates nudges/explanations; can query KB synchronously if needed."""
    def __init__(self, name, bus, kb: Optional[KBNode] = None):
        super().__init__(name, NodeRole.GUIDANCE, bus)
        self.kb = kb

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.STATE, Topic.CONTEXT, Topic.KB_RESULT]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.GUIDANCE_PLAN, Topic.AUDIT, Topic.ORCH_PROPOSAL]

    def on_message(self, msg: Message) -> None:
        # TODO: synthesize guidance; may call self.kb.call("retrieve", ...)
        pass

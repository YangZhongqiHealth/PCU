from typing import List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class SafetyNode(Node):
    """Applies guardrails; only forwards safe/approved plans."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.SAFETY, bus)

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.GUIDANCE_PLAN, Topic.KB_RESULT]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.ORCH_PROPOSAL, Topic.AUDIT]

    def on_message(self, msg: Message) -> None:
        # TODO: validate safety; forward as ORCH_PROPOSAL or refuse.
        pass

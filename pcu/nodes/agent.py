from typing import List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class AgentNode(Node):
    """Template for domain agents (sleep, activity, mood, etc.)."""
    def __init__(self, name, bus, domain: str):
        super().__init__(name, NodeRole.AGENT, bus)
        self.domain = domain

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.STATE, Topic.CONTEXT, Topic.KB_RESULT, Topic.CONTROL]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.ORCH_PROPOSAL, Topic.AUDIT, Topic.KB_QUERY]

    def on_message(self, msg: Message) -> None:
        # TODO: evaluate domain-specific logic and publish proposals.
        pass

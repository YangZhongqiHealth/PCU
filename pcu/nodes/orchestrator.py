from typing import List
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class OrchestratorNode(Node):
    """Resolves conflicts between agent proposals; emits final decision/outbound."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.ORCHESTRATOR, bus)
        self._agents: List["Node"] = []

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.ORCH_PROPOSAL, Topic.CONTEXT, Topic.STATE, Topic.FEEDBACK]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.ORCH_DECISION, Topic.GUIDANCE_OUT, Topic.AUDIT]

    def register_agent(self, agent: "Node") -> None:
        self._agents.append(agent)

    def on_message(self, msg: Message) -> None:
        # TODO: prioritize and pick final action; publish GUIDANCE_OUT/ORCH_DECISION.
        pass

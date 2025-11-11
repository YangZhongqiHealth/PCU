from typing import List, Any
from ..core.node import Node
from ..core.topics import Topic, NodeRole
from ..core.message import Message

class KBNode(Node):
    """Retrieves evidence, rules, and policies given a query."""
    def __init__(self, name, bus):
        super().__init__(name, NodeRole.KB, bus)

    @property
    def inputs(self) -> List[Topic]:
        return [Topic.KB_QUERY]

    @property
    def outputs(self) -> List[Topic]:
        return [Topic.KB_RESULT, Topic.AUDIT]

    def on_message(self, msg: Message) -> None:
        # TODO: perform retrieval/reasoning and publish KB_RESULT.
        pass

    # Optional synchronous RPC hook for direct lookups
    def call(self, method: str, **kwargs: Any) -> Any:
        if method == "retrieve":
            return {"results": []}
        return super().call(method, **kwargs)

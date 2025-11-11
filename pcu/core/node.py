from abc import ABC, abstractmethod
from typing import List, Any
from .topics import Topic, NodeRole
from .bus import EventBus

class Node(ABC):
    """
    Abstract base (ABC) enforces each node exposes:
      - inputs: topics it subscribes to
      - outputs: topics it may publish on
      - on_message: handler for inbound messages
    Using ABC prevents accidental instantiation of incomplete nodes.
    """
    def __init__(self, name: str, role: NodeRole, bus: EventBus) -> None:
        self.name = name
        self.role = role
        self.bus = bus

    @property
    @abstractmethod
    def inputs(self) -> List[Topic]:
        ...

    @property
    @abstractmethod
    def outputs(self) -> List[Topic]:
        ...

    def start(self) -> None:
        """Register subscriptions at runtime start."""
        self.bus.subscribe(self, self.inputs)

    def stop(self) -> None:
        """Clean up resources if needed."""
        pass

    @abstractmethod
    def on_message(self, msg) -> None:
        """Main reactive entrypoint."""
        ...

    # Optional synchronous RPC-style hook
    def call(self, method: str, **kwargs: Any) -> Any:
        raise NotImplementedError(f"{self.name} has no RPC method '{method}'")

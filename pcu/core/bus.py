from typing import Dict, List, Iterable, Protocol
from .message import Message
from .topics import Topic

class EventBus(Protocol):
    def publish(self, msg: Message) -> None: ...
    def subscribe(self, node: "Node", topics: Iterable[Topic]) -> None: ...
    def route(self) -> None: ...

class InMemoryBus:
    """
    Minimal pub/sub for local dev and unit tests.
    Swap with Kafka/NATS in production using same interface.
    """
    def __init__(self) -> None:
        self._subs: Dict[Topic, List["Node"]] = {}
        self._queue: List[Message] = []

    def publish(self, msg: Message) -> None:
        self._queue.append(msg)

    def subscribe(self, node: "Node", topics: Iterable[Topic]) -> None:
        for t in topics:
            self._subs.setdefault(t, []).append(node)

    def route(self) -> None:
        while self._queue:
            msg = self._queue.pop(0)
            for node in self._subs.get(msg.topic, []):
                node.on_message(msg)

    # Introspection used by the validator
    @property
    def subscriptions(self) -> Dict[Topic, List["Node"]]:
        return self._subs

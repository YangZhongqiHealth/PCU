from dataclasses import dataclass, field
from typing import Any, Dict
import time, uuid
from .topics import Topic

@dataclass(frozen=True)
class Message:
    """
    Immutable envelope for all inter-node communication.
    - topic: routing channel
    - payload: domain data (dict for flexibility)
    - ts, correlation_id: observability & tracing
    - provenance: model versions, sources, policy matches
    """
    topic: Topic
    payload: Dict[str, Any]
    ts: float = field(default_factory=lambda: time.time())
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provenance: Dict[str, Any] = field(default_factory=dict)

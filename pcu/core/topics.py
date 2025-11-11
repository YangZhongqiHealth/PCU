from enum import Enum, auto

class Topic(str, Enum):
    """Logical message channels connecting nodes."""
    RAW_SENSORS = "raw.sensors"
    EVENTS = "personicle.events"
    STATE = "state.vector"
    KB_QUERY = "kb.query"
    KB_RESULT = "kb.result"
    CONTEXT = "context.situation"
    GUIDANCE_PLAN = "guidance.plan"
    GUIDANCE_OUT = "guidance.outbound"
    ORCH_PROPOSAL = "orchestrator.proposal"
    ORCH_DECISION = "orchestrator.decision"
    FEEDBACK = "feedback.user"
    AUDIT = "audit.provenance"
    CONTROL = "control"

class NodeRole(Enum):
    """Role tags for documentation / monitoring."""
    INGEST = auto()
    PERSONICLE = auto()
    STATE = auto()
    KB = auto()
    CONTEXT = auto()
    GUIDANCE = auto()
    ORCHESTRATOR = auto()
    INTERFACE = auto()
    AGENT = auto()
    SAFETY = auto()
    OBSERVABILITY = auto()

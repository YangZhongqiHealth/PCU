# PCU (Personal Care Utility)

A layered, message-driven architecture for a Personal Care Utility system. This skeleton provides a modular framework for processing sensor data through multiple layers: Ingestion → Personicle → State → Context → Guidance → Safety → Orchestrator → Interface.

## Architecture

The PCU system is built on a pub/sub message bus architecture where each layer is a `Node` that:
- Subscribes to specific message topics (inputs)
- Processes messages and publishes to other topics (outputs)
- Communicates asynchronously via an `EventBus`

### Layers

1. **Ingestion**: Receives raw sensor data
2. **Personicle**: Transforms sensor data into events
3. **State**: Maintains physiological/behavioral state
4. **Context**: Infers situation, goals, and risk
5. **Guidance**: Generates nudges and recommendations
6. **Safety**: Applies guardrails and validates safety
7. **Orchestrator**: Resolves conflicts and makes final decisions
8. **Interface**: Delivers guidance to users

## Installation

This project uses only Python standard library modules. No external dependencies are required.

**Requirements:**
- Python 3.8+ (required for `typing.Protocol` support)

## Usage

### Basic Example

```bash
# Run the main example
python app/main.py

# Run the test flow
python app/test_flow.py
```

### Building a System

```python
from pcu.system import build_pcu_system, PCUSystem

# Build and start the system
system = build_pcu_system()
system.start()

# Ingest sensor data
ingestion = system.nodes["ingestion"]
ingestion.ingest_sensor_packet({
    "user_id": "u123",
    "stream_id": "watch.hr",
    "value": 72,
    "unit": "bpm"
})

# Process messages
system.tick()

# Stop the system
system.stop()
```

## Project Structure

```
PCU_repo/
├── app/                    # Application code and examples
│   ├── main.py            # Basic usage example
│   └── test_flow.py       # Full pipeline test
├── pcu/                    # Core PCU framework
│   ├── core/              # Core abstractions (Node, Bus, Message, Topics)
│   ├── nodes/             # Node implementations
│   └── system/            # System builder and validator
├── requirements.txt       # Python dependencies (none required)
└── README.md             # This file
```

## Key Concepts

### Nodes

Each layer is a `Node` subclass that must implement:
- `inputs`: List of topics the node subscribes to
- `outputs`: List of topics the node can publish to
- `on_message(msg)`: Handler for incoming messages

### Message Bus

The `EventBus` provides pub/sub messaging:
- **InMemoryBus**: Current implementation for local dev/testing
- **Production**: Can be swapped with Kafka, NATS, or other message brokers

### Dataflow Validation

The `DataflowValidator` ensures:
- All declared inputs are subscribed
- All declared outputs have subscribers (except sink topics)
- Basic reachability along the main pipeline

## Development

The system is designed to be extensible:
- Add new nodes by subclassing `Node`
- Implement custom message handlers
- Swap the bus implementation for production use
- Add domain-specific agents to the orchestrator

## License

pass


# PCU Skeleton

A layered, message-driven skeleton for a Personal Care Utility (PCU).

## Key ideas
- Each layer is a `Node` subclass with `inputs`, `outputs`, and `on_message`.
- Nodes communicate via an `EventBus` (in-memory now; swap to Kafka later).
- `DataflowValidator` ensures declared outputs have subscribers, inputs are subscribed, and spine reachability exists.

## Run
```bash
python -m app.main





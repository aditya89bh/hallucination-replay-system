# Memory Reconstruction Example

This example shows the metadata shape used to reconstruct memory state at a replay step.

```json
{
  "metadata": {
    "memory": [
      {
        "step_index": 0,
        "event": {
          "event_type": "write",
          "key": "research_goal",
          "value": "summarize trace evidence",
          "timestamp": "2026-01-01T00:00:00Z"
        }
      },
      {
        "step_index": 1,
        "event": {
          "event_type": "read",
          "key": "research_goal",
          "value": "summarize trace evidence",
          "timestamp": "2026-01-01T00:01:00Z"
        }
      }
    ]
  }
}
```

Use `reconstruct_memory(trace, step_index)` to recover reads, writes, and memory state.

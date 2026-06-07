# Tool Reconstruction Example

This example shows the metadata shape used to reconstruct tool calls and results.

```json
{
  "metadata": {
    "tools": [
      {
        "step_index": 1,
        "call": {
          "tool_name": "search",
          "arguments": {"query": "trace replay"},
          "invocation_time": "2026-01-01T00:01:00Z",
          "step_id": "step-2"
        },
        "result": {
          "tool_name": "search",
          "success": true,
          "output": {"hits": 3},
          "execution_time_ms": 12.5,
          "step_id": "step-2"
        }
      }
    ]
  }
}
```

Use `reconstruct_tools(trace, step_index)` to recover calls, results, and timeline state.

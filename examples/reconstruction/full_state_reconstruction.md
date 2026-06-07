# Full-State Reconstruction Example

Given a trace with replay steps and reconstruction metadata, call:

```python
from hallucination_replay.reconstruction import reconstruct_state

state = reconstruct_state(trace, step_index=2)
```

The returned state aggregates:

- context available at the step
- prompt state and prompt inputs
- memory reads, writes, and state
- retrieval events and retrieved documents
- tool calls, results, and timeline state
- validation activity and results
- reasoning summaries and confidence evolution

It intentionally does not perform failure analysis or hallucination detection.

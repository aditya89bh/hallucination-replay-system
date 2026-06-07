# Trace Schema

The Phase 2 trace schema defines the foundational entities used to record, replay, debug, and analyze AI agent executions. The schema is intentionally implementation-neutral: it captures observable events and metadata without implementing replay behavior.

## Entity Relationships

```text
RunTrace
├── TraceMetadata
└── AgentStep[]
    ├── ToolCall[]
    ├── ToolResult[]
    ├── RetrievalEvent[]
    ├── MemoryEvent[]
    ├── ValidationEvent[]
    └── ReasoningEvent[]
```

A `RunTrace` represents one agent execution. `AgentStep` records the ordered timeline of work inside that execution. Event models attach evidence to the relevant step by `step_id` where the event is directly step-scoped.

## Field Descriptions

### RunTrace

| Field | Description |
| --- | --- |
| `run_id` | Stable identifier for a single recorded run. |
| `started_at` | Timestamp when the run began. |
| `completed_at` | Optional timestamp when the run finished. |
| `status` | Run state: `running`, `completed`, or `failed`. |
| `metadata` | Additional JSON-compatible run metadata. |

### AgentStep

| Field | Description |
| --- | --- |
| `step_id` | Stable identifier for this step. |
| `step_index` | Zero-based ordering index in the trace timeline. |
| `step_type` | Step category: `model`, `tool`, `retrieval`, `memory`, `validation`, or `reasoning`. |
| `timestamp` | Timestamp when the step occurred. |
| `description` | Human-readable step summary. |

### ToolCall

| Field | Description |
| --- | --- |
| `tool_name` | Tool being invoked. |
| `arguments` | JSON-compatible argument mapping sent to the tool. |
| `invocation_time` | Timestamp when invocation began. |
| `step_id` | Agent step associated with the call. |

### ToolResult

| Field | Description |
| --- | --- |
| `tool_name` | Tool that returned the result. |
| `success` | Strict boolean success flag. |
| `output` | JSON-compatible tool output or error payload. |
| `execution_time_ms` | Non-negative tool execution duration in milliseconds. |
| `step_id` | Agent step associated with the result. |

### RetrievalEvent

| Field | Description |
| --- | --- |
| `query` | Retrieval query issued by the agent or orchestration layer. |
| `retrieved_documents` | List of JSON-compatible retrieved document records. |
| `retrieval_time_ms` | Non-negative retrieval duration in milliseconds. |
| `source` | Retrieval backend or corpus name. |

### MemoryEvent

| Field | Description |
| --- | --- |
| `event_type` | Memory action: `read` or `write`. |
| `key` | Memory key or namespace path. |
| `value` | JSON-compatible value read or written. |
| `timestamp` | Timestamp when the memory operation occurred. |

### ValidationEvent

| Field | Description |
| --- | --- |
| `validator_name` | Name of the validator that ran. |
| `passed` | Strict boolean validation result. |
| `findings` | List of validation observations or failures. |
| `timestamp` | Timestamp when validation occurred. |

### ReasoningEvent

| Field | Description |
| --- | --- |
| `reasoning_type` | Summary category: `planning`, `reflection`, `decision`, or `error_analysis`. |
| `summary` | Concise reasoning summary. Chain-of-thought is not stored. |
| `confidence` | Confidence score from `0` to `1`. |
| `timestamp` | Timestamp when the reasoning summary was recorded. |

### TraceMetadata

| Field | Description |
| --- | --- |
| `agent_name` | Agent name or service identifier. |
| `agent_version` | Agent version, release, or commit identifier. |
| `framework` | Agent framework or runtime. |
| `environment` | Runtime environment: `development`, `test`, `staging`, or `production`. |
| `tags` | Free-form labels for filtering and reporting. |

## Example Trace Payload

```json
{
  "run": {
    "run_id": "run-2026-001",
    "started_at": "2026-01-01T00:00:00Z",
    "completed_at": "2026-01-01T00:00:12Z",
    "status": "failed",
    "metadata": {
      "incident_id": "INC-42"
    }
  },
  "metadata": {
    "agent_name": "research-agent",
    "agent_version": "1.2.3",
    "framework": "langgraph",
    "environment": "production",
    "tags": ["retrieval", "hallucination"]
  },
  "steps": [
    {
      "step_id": "step-1",
      "step_index": 0,
      "step_type": "retrieval",
      "timestamp": "2026-01-01T00:00:01Z",
      "description": "Retrieve supporting documents for answer generation."
    }
  ],
  "retrieval_events": [
    {
      "query": "contract renewal date",
      "retrieved_documents": [
        {
          "id": "doc-7",
          "title": "Account notes",
          "score": 0.82
        }
      ],
      "retrieval_time_ms": 18.4,
      "source": "vector-store"
    }
  ],
  "tool_calls": [
    {
      "tool_name": "crm_lookup",
      "arguments": {
        "account_id": "acct-123"
      },
      "invocation_time": "2026-01-01T00:00:02Z",
      "step_id": "step-2"
    }
  ],
  "tool_results": [
    {
      "tool_name": "crm_lookup",
      "success": true,
      "output": {
        "renewal_date": "2026-03-15"
      },
      "execution_time_ms": 44.2,
      "step_id": "step-2"
    }
  ],
  "memory_events": [
    {
      "event_type": "read",
      "key": "account.acct-123.preferences",
      "value": {
        "timezone": "Asia/Kolkata"
      },
      "timestamp": "2026-01-01T00:00:03Z"
    }
  ],
  "validation_events": [
    {
      "validator_name": "citation-checker",
      "passed": false,
      "findings": ["Final answer cited no retrieved document."],
      "timestamp": "2026-01-01T00:00:11Z"
    }
  ],
  "reasoning_events": [
    {
      "reasoning_type": "error_analysis",
      "summary": "The answer relied on an unsupported date after retrieval returned incomplete evidence.",
      "confidence": 0.76,
      "timestamp": "2026-01-01T00:00:12Z"
    }
  ]
}
```

## Design Rationale

- **Pydantic v2 models** provide validation, serialization, and deserialization for trace payloads.
- **Strict enums** make failure categories and lifecycle states predictable for replay and reporting.
- **Strict booleans** avoid accidental coercion in success and validation fields.
- **JSON-compatible helpers** make trace records suitable for files, APIs, CI artifacts, and future storage adapters.
- **Reasoning summaries only** preserve useful debugging evidence without storing chain-of-thought.
- **Step identifiers** allow events to be linked to the replay timeline without forcing all entities into one large nested object too early.

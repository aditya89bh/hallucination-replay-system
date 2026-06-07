"""OpenAPI metadata for the debugging platform API."""

from __future__ import annotations

OPENAPI_TAGS: list[dict[str, str]] = [
    {"name": "system", "description": "Health and package version endpoints."},
    {"name": "traces", "description": "Load, list, and create trace records."},
    {
        "name": "replay",
        "description": "Load and navigate deterministic replay sessions.",
    },
    {
        "name": "reconstruction",
        "description": "Reconstruct context, memory, and full execution state.",
    },
    {
        "name": "analysis",
        "description": "Run deterministic failure analysis and retrieve reports.",
    },
    {
        "name": "hallucination",
        "description": "Run deterministic hallucination analysis and retrieve reports.",
    },
    {
        "name": "comparison",
        "description": "Compare executions and retrieve comparison reports.",
    },
]

API_DESCRIPTION = """
Interactive debugging APIs for hallucination replay workflows.

Typical flow:
1. Create or load traces with `/traces`.
2. Start replay with `/replay/load` and navigate via `/replay/next`,
   `/replay/previous`, or `/replay/jump`.
3. Inspect reconstructed state with `/reconstruction/context`,
   `/reconstruction/memory`, and `/reconstruction/state`.
4. Run deterministic failure analysis with `/analysis/run` and hallucination
   analysis with `/hallucination/run`.
5. Compare two executions with `/compare`.
""".strip()

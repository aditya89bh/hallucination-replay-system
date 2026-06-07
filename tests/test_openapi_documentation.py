from __future__ import annotations

from pathlib import Path

from hallucination_replay.api import create_app


def test_openapi_schema_documents_platform_endpoints() -> None:
    schema = create_app().openapi()
    paths = set(schema["paths"])

    assert "/traces" in paths
    assert "/replay/load" in paths
    assert "/reconstruction/state" in paths
    assert "/analysis/run" in paths
    assert "/hallucination/run" in paths
    assert "/compare" in paths
    assert {tag["name"] for tag in schema["tags"]} >= {
        "traces",
        "replay",
        "reconstruction",
        "analysis",
        "hallucination",
        "comparison",
    }


def test_openapi_usage_guide_lists_endpoints_and_examples() -> None:
    guide = Path("docs/openapi.md").read_text(encoding="utf-8")

    assert "POST /replay/load" in guide
    assert "POST /hallucination/run" in guide
    assert "Schema examples" in guide
    assert "curl -X POST" in guide

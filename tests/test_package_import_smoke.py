from __future__ import annotations

import importlib

PACKAGE_IMPORTS = [
    "hallucination_replay.models",
    "hallucination_replay.storage",
    "hallucination_replay.replay",
    "hallucination_replay.reconstruction",
    "hallucination_replay.analysis",
    "hallucination_replay.hallucination",
    "hallucination_replay.diffing",
    "hallucination_replay.api",
    "hallucination_replay.dashboard",
]

EXPECTED_EXPORTS = {
    "hallucination_replay.models": "RunTrace",
    "hallucination_replay.storage": "TraceRepository",
    "hallucination_replay.replay": "ReplayController",
    "hallucination_replay.reconstruction": "reconstruct_state",
    "hallucination_replay.analysis": "FailureFinding",
    "hallucination_replay.hallucination": "score_hallucinations",
    "hallucination_replay.diffing": "compare_executions",
    "hallucination_replay.api": "create_app",
    "hallucination_replay.dashboard": "DashboardService",
}


def test_public_package_imports_are_available() -> None:
    for module_name in PACKAGE_IMPORTS:
        module = importlib.import_module(module_name)

        assert module.__doc__


def test_public_package_exports_are_available() -> None:
    for module_name, export_name in EXPECTED_EXPORTS.items():
        module = importlib.import_module(module_name)

        assert hasattr(module, export_name)

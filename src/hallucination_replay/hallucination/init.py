"""Hallucination detection package."""

from hallucination_replay.hallucination.claims import (
    Claim,
    extract_claims_from_outputs,
    extract_claims_from_text,
)
from hallucination_replay.hallucination.contradictions import (
    ContradictionFinding,
    detect_contradictions,
)
from hallucination_replay.hallucination.coverage import (
    EvidenceCoverageScore,
    score_evidence_coverage,
)
from hallucination_replay.hallucination.evidence import Evidence, extract_evidence
from hallucination_replay.hallucination.matching import (
    EvidenceMatch,
    match_claim_to_evidence,
    match_claims_to_evidence,
)
from hallucination_replay.hallucination.normalization import (
    normalize_claim,
    normalize_claims,
    normalize_evidence,
    normalize_evidence_records,
    normalize_text,
)
from hallucination_replay.hallucination.scoring import (
    HallucinationScore,
    score_hallucinations,
)
from hallucination_replay.hallucination.severity import (
    HallucinationSeverity,
    rank_hallucination_severity,
)
from hallucination_replay.hallucination.unsupported import (
    UnsupportedClaimFinding,
    detect_unsupported_claims,
)

__all__ = [
    "Claim",
    "ContradictionFinding",
    "Evidence",
    "EvidenceCoverageScore",
    "EvidenceMatch",
    "HallucinationScore",
    "HallucinationSeverity",
    "UnsupportedClaimFinding",
    "detect_contradictions",
    "detect_unsupported_claims",
    "extract_claims_from_outputs",
    "extract_claims_from_text",
    "extract_evidence",
    "match_claim_to_evidence",
    "match_claims_to_evidence",
    "normalize_claim",
    "normalize_claims",
    "normalize_evidence",
    "normalize_evidence_records",
    "normalize_text",
    "rank_hallucination_severity",
    "score_evidence_coverage",
    "score_hallucinations",
]

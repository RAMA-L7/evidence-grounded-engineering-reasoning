"""EGER Evidence — Structured evidence contracts (P137)."""

from .schemas import Finding, EvidenceArtifact, FindingSummary
from .normalizer import EvidenceNormalizer

__all__ = ["Finding", "EvidenceArtifact", "FindingSummary", "EvidenceNormalizer"]

"""
Tests for Insight Confidence Framework (TKT-094)
=================================================
Owner: N'Golo Kante (QA / Stats Integrity)
Epic: EPIC-014 (Foundation Fortification)

Validates the InsightConfidence scorer and InsightScore dataclass.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.analysis.insight_confidence import InsightConfidence


@pytest.fixture
def scorer():
    return InsightConfidence()


def test_high_confidence_grade_a(scorer):
    """5000 samples, 0.9 consistency, 0.95 recency, cross_val=True -> Grade A."""
    result = scorer.score(
        sample_size=5000,
        consistency=0.9,
        recency_weight=0.95,
        cross_validation=True,
    )
    assert result.grade == "A", (
        f"Expected Grade A, got {result.grade} (confidence={result.confidence})"
    )


def test_medium_confidence_grade_b(scorer):
    """200 samples, 0.7 consistency, 0.7 recency, cross_val=False -> Grade B or C."""
    result = scorer.score(
        sample_size=200,
        consistency=0.7,
        recency_weight=0.7,
        cross_validation=False,
    )
    assert result.grade in ("B", "C"), (
        f"Expected Grade B or C, got {result.grade} (confidence={result.confidence})"
    )


def test_low_sample_grade_d(scorer):
    """10 samples, 0.3 consistency, 0.2 recency, cross_val=False -> Grade D."""
    result = scorer.score(
        sample_size=10,
        consistency=0.3,
        recency_weight=0.2,
        cross_validation=False,
    )
    assert result.grade == "D", (
        f"Expected Grade D, got {result.grade} (confidence={result.confidence})"
    )


def test_flags_low_sample(scorer):
    """20 samples -> flags contain 'LOW_SAMPLE'."""
    result = scorer.score(
        sample_size=20,
        consistency=0.5,
        recency_weight=0.5,
        cross_validation=True,
    )
    assert "LOW_SAMPLE" in result.flags, f"Expected LOW_SAMPLE flag, got {result.flags}"


def test_flags_no_cross_validation(scorer):
    """cross_val=False -> flags contain 'NO_CROSS_VALIDATION'."""
    result = scorer.score(
        sample_size=500,
        consistency=0.9,
        recency_weight=0.9,
        cross_validation=False,
    )
    assert "NO_CROSS_VALIDATION" in result.flags, (
        f"Expected NO_CROSS_VALIDATION flag, got {result.flags}"
    )


def test_score_clamped_0_100(scorer):
    """Ensure score is between 0 and 100 for all inputs."""
    test_cases = [
        (0, 0.0, 0.0, False),
        (999999, 1.0, 1.0, True),
        (10, 0.1, 0.1, False),
        (300, 0.5, 0.5, True),
        (1, 0.0, 0.0, False),
    ]
    for sample_size, consistency, recency, cross_val in test_cases:
        result = scorer.score(
            sample_size=sample_size,
            consistency=consistency,
            recency_weight=recency,
            cross_validation=cross_val,
        )
        assert 0 <= result.confidence <= 100, (
            f"Score {result.confidence} out of bounds for inputs "
            f"({sample_size}, {consistency}, {recency}, {cross_val})"
        )


def test_sample_tier_high(scorer):
    """500 samples -> tier 'HIGH'."""
    result = scorer.score(
        sample_size=500,
        consistency=0.8,
        recency_weight=0.8,
        cross_validation=True,
    )
    assert result.sample_tier == "HIGH", f"Expected sample tier HIGH, got {result.sample_tier}"


def test_recommendation_not_empty(scorer):
    """All scores have non-empty recommendation."""
    test_cases = [
        (5000, 0.9, 0.95, True),  # Grade A
        (200, 0.7, 0.7, False),  # Grade B/C
        (10, 0.3, 0.2, False),  # Grade D
        (50, 0.5, 0.5, True),  # Grade C
    ]
    for sample_size, consistency, recency, cross_val in test_cases:
        result = scorer.score(
            sample_size=sample_size,
            consistency=consistency,
            recency_weight=recency,
            cross_validation=cross_val,
        )
        assert result.recommendation, (
            f"Empty recommendation for inputs ({sample_size}, {consistency}, {recency}, {cross_val})"
        )


def test_to_dict(scorer):
    """InsightScore.to_dict() returns correct keys."""
    result = scorer.score(
        sample_size=300,
        consistency=0.8,
        recency_weight=0.8,
        cross_validation=True,
    )
    d = result.to_dict()
    expected_keys = {"confidence", "grade", "sample_tier", "flags", "recommendation"}
    assert set(d.keys()) == expected_keys, f"Expected keys {expected_keys}, got {set(d.keys())}"
    assert isinstance(d["confidence"], float)
    assert isinstance(d["grade"], str)
    assert isinstance(d["sample_tier"], str)
    assert isinstance(d["flags"], list)
    assert isinstance(d["recommendation"], str)

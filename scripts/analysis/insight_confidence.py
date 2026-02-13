"""
Cricket Playbook - Insight Confidence Framework (TKT-094)
=========================================================
Owner: Andy Flower (Cricket Domain Expert)
Epic: EPIC-014 (Foundation Fortification)

Scores how much editorial confidence we should have in any analytical insight.
Built on top of TKT-145's ConfidenceCalculator (confidence_intervals.py).

Instead of just computing CIs, this framework answers the editorial question:
"Should we publish this insight confidently, or add caveats?"

Scoring breakdown (0-100):
    - Sample size:       40% weight (capped at 300 balls/innings)
    - Consistency:       25% weight (metric stability across sub-samples)
    - Recency:           20% weight (how recent the underlying data is)
    - Cross-validation:  15% weight (holds across conditions?)

Usage:
    from scripts.analysis.insight_confidence import InsightConfidence

    scorer = InsightConfidence()
    result = scorer.score(
        sample_size=450,
        consistency=0.85,
        recency_weight=0.9,
        cross_validation=True,
    )
    print(f"Grade: {result.grade} ({result.confidence:.1f}/100)")
    print(f"Recommendation: {result.recommendation}")
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from scripts.analysis.confidence_intervals import CIResult


@dataclass
class InsightScore:
    """Result of scoring an analytical insight for editorial confidence."""

    confidence: float
    grade: str
    sample_tier: str
    flags: list[str] = field(default_factory=list)
    recommendation: str = ""

    def __str__(self) -> str:
        flag_str = ", ".join(self.flags) if self.flags else "none"
        return (
            f"Grade {self.grade} ({self.confidence:.1f}/100) | "
            f"Sample: {self.sample_tier} | Flags: {flag_str}"
        )

    def to_dict(self) -> dict:
        return {
            "confidence": round(self.confidence, 2),
            "grade": self.grade,
            "sample_tier": self.sample_tier,
            "flags": self.flags,
            "recommendation": self.recommendation,
        }


class InsightConfidence:
    """Score editorial confidence in analytical insights.

    Combines sample size, consistency, recency, and cross-validation
    into a single 0-100 confidence score with letter grades and flags.
    """

    # Sample tier thresholds
    SAMPLE_HIGH = 300
    SAMPLE_MEDIUM = 100
    SAMPLE_LOW = 30

    # Grade boundaries
    GRADE_A = 85
    GRADE_B = 70
    GRADE_C = 55

    # Flag thresholds
    FLAG_LOW_SAMPLE = 30
    FLAG_SMALL_SAMPLE = 100
    FLAG_HIGH_VARIANCE = 0.4
    FLAG_RECENCY_BIAS = 0.3

    def score(
        self,
        sample_size: int,
        consistency: float,
        recency_weight: float,
        cross_validation: bool,
    ) -> InsightScore:
        """Score an analytical insight for editorial confidence.

        Args:
            sample_size: Number of balls or innings in the sample.
            consistency: How consistent the metric is across sub-samples (0-1).
                         E.g., SR in first half vs second half of career.
            recency_weight: How recent the data is (0-1).
                            1.0 = all from 2025, 0.5 = mix of 2023-2025.
            cross_validation: Whether the insight holds across different
                              conditions (home/away, bat first/second).

        Returns:
            InsightScore with confidence, grade, sample tier, flags,
            and editorial recommendation.
        """
        # Clamp inputs to valid ranges
        sample_size = max(0, sample_size)
        consistency = max(0.0, min(1.0, consistency))
        recency_weight = max(0.0, min(1.0, recency_weight))

        # --- Scoring formula ---
        base = min(sample_size / 300, 1.0) * 40
        consistency_score = consistency * 25
        recency_score = recency_weight * 20
        cross_val_score = 15 if cross_validation else 5
        confidence = base + consistency_score + recency_score + cross_val_score

        # Clamp final score to 0-100
        confidence = max(0.0, min(100.0, confidence))

        # --- Grade ---
        grade = self._grade(confidence)

        # --- Sample tier ---
        sample_tier = self._sample_tier(sample_size)

        # --- Flags ---
        flags = self._flags(sample_size, consistency, recency_weight, cross_validation)

        # --- Editorial recommendation ---
        recommendation = self._recommendation(grade, flags)

        return InsightScore(
            confidence=confidence,
            grade=grade,
            sample_tier=sample_tier,
            flags=flags,
            recommendation=recommendation,
        )

    @classmethod
    def from_confidence_interval(
        cls,
        ci_result: CIResult,
        recency_weight: float = 0.5,
        cross_validation: bool = False,
    ) -> InsightScore:
        """Bridge method: derive an InsightScore from a CIResult.

        Infers consistency from the CI width relative to the estimate.
        A narrow CI (small margin relative to the estimate) implies
        high consistency; a wide CI implies low consistency.

        Args:
            ci_result: A CIResult from ConfidenceCalculator.
            recency_weight: How recent the data is (0-1).
            cross_validation: Whether the insight holds across conditions.

        Returns:
            InsightScore derived from the CI properties.
        """
        sample_size = ci_result.n_samples

        # Infer consistency from CI width relative to estimate.
        # coefficient of variation of the CI: margin / |estimate|
        # Narrow CI -> low CV -> high consistency
        if ci_result.estimate != 0 and not math.isinf(ci_result.margin):
            cv = ci_result.margin / abs(ci_result.estimate)
            # Map CV to consistency: CV=0 -> 1.0, CV>=1.0 -> 0.0
            consistency = max(0.0, min(1.0, 1.0 - cv))
        elif ci_result.margin == 0:
            # Zero margin means either single data point or perfect uniformity
            consistency = 1.0 if sample_size > 1 else 0.5
        else:
            # Infinite margin (e.g., not-out average) -> low consistency
            consistency = 0.2

        scorer = cls()
        return scorer.score(
            sample_size=sample_size,
            consistency=consistency,
            recency_weight=recency_weight,
            cross_validation=cross_validation,
        )

    @staticmethod
    def _grade(confidence: float) -> str:
        """Map confidence score to letter grade."""
        if confidence >= InsightConfidence.GRADE_A:
            return "A"
        if confidence >= InsightConfidence.GRADE_B:
            return "B"
        if confidence >= InsightConfidence.GRADE_C:
            return "C"
        return "D"

    @staticmethod
    def _sample_tier(sample_size: int) -> str:
        """Classify sample size into tiers."""
        if sample_size >= InsightConfidence.SAMPLE_HIGH:
            return "HIGH"
        if sample_size >= InsightConfidence.SAMPLE_MEDIUM:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _flags(
        sample_size: int,
        consistency: float,
        recency_weight: float,
        cross_validation: bool,
    ) -> list[str]:
        """Generate warning flags for the insight."""
        flags: list[str] = []
        if sample_size < InsightConfidence.FLAG_LOW_SAMPLE:
            flags.append("LOW_SAMPLE")
        elif sample_size < InsightConfidence.FLAG_SMALL_SAMPLE:
            flags.append("SMALL_SAMPLE")
        if consistency < InsightConfidence.FLAG_HIGH_VARIANCE:
            flags.append("HIGH_VARIANCE")
        if recency_weight < InsightConfidence.FLAG_RECENCY_BIAS:
            flags.append("RECENCY_BIAS")
        if not cross_validation:
            flags.append("NO_CROSS_VALIDATION")
        return flags

    @staticmethod
    def _recommendation(grade: str, flags: list[str]) -> str:
        """Generate editorial recommendation based on grade and flags."""
        if grade == "A":
            return "Publish with confidence"
        if grade == "B":
            if flags:
                return "Publish with minor caveats: " + ", ".join(flags)
            return "Publish with confidence"
        if grade == "C":
            return "Add sample size caveat and note limitations"
        # Grade D
        if "LOW_SAMPLE" in flags:
            return "Insufficient data — do not publish as standalone insight"
        return "Low confidence — use only as supporting evidence, not a headline"


if __name__ == "__main__":
    from scripts.analysis.confidence_intervals import ConfidenceCalculator

    print("Insight Confidence Framework (TKT-094)")
    print("=" * 50)

    scorer = InsightConfidence()

    # High confidence example: Kohli IPL career batting
    high = scorer.score(
        sample_size=5430,
        consistency=0.88,
        recency_weight=0.9,
        cross_validation=True,
    )
    print(f"\nKohli Career Batting: {high}")
    print(f"  Recommendation: {high.recommendation}")

    # Medium confidence: emerging player
    medium = scorer.score(
        sample_size=150,
        consistency=0.65,
        recency_weight=0.95,
        cross_validation=False,
    )
    print(f"\nEmerging Player:      {medium}")
    print(f"  Recommendation: {medium.recommendation}")

    # Low confidence: tiny sample debut player
    low = scorer.score(
        sample_size=18,
        consistency=0.3,
        recency_weight=0.2,
        cross_validation=False,
    )
    print(f"\nDebut Player:         {low}")
    print(f"  Recommendation: {low.recommendation}")

    # Bridge from CI
    print("\n--- Bridge from ConfidenceCalculator ---")
    calc = ConfidenceCalculator()
    sr_ci = calc.strike_rate_ci(runs=7263, balls=5430)
    bridged = InsightConfidence.from_confidence_interval(
        sr_ci, recency_weight=0.8, cross_validation=True
    )
    print(f"Kohli SR CI -> Insight: {bridged}")
    print(f"  Recommendation: {bridged.recommendation}")

"""
Cricket Playbook - Confidence Interval Calculator (TKT-145)
===========================================================
Owner: Stephen Curry (Analytics Lead)
Epic: EPIC-014 (Foundation Fortification)

Adds confidence intervals to all computed metrics using bootstrap resampling.
Instead of just "SR = 145", produces "SR = 145 ± 8 (95% CI: 137-153)".

Supports:
- Bootstrap CI for any aggregated metric (mean, rate, percentage)
- Wilson score interval for proportions (boundary%, dot ball%)
- Configurable confidence levels (default: 95%)

Usage:
    from scripts.analysis.confidence_intervals import ConfidenceCalculator

    calc = ConfidenceCalculator(confidence=0.95)
    result = calc.bootstrap_ci(data, metric_fn=np.mean, n_bootstrap=1000)
    print(f"Mean: {result['estimate']:.1f} ± {result['margin']:.1f}")
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


@dataclass
class CIResult:
    """Confidence interval result for a metric."""

    estimate: float
    lower: float
    upper: float
    margin: float
    confidence: float
    method: str
    n_samples: int

    def __str__(self) -> str:
        return (
            f"{self.estimate:.2f} ± {self.margin:.2f} "
            f"({self.confidence * 100:.0f}% CI: {self.lower:.2f}-{self.upper:.2f})"
        )

    def to_dict(self) -> dict:
        return {
            "estimate": round(self.estimate, 4),
            "lower": round(self.lower, 4),
            "upper": round(self.upper, 4),
            "margin": round(self.margin, 4),
            "confidence": self.confidence,
            "method": self.method,
            "n": self.n_samples,
        }


class ConfidenceCalculator:
    """Calculate confidence intervals for cricket metrics."""

    def __init__(self, confidence: float = 0.95, random_seed: int = 42):
        self.confidence = confidence
        self.rng = np.random.RandomState(random_seed)

    def bootstrap_ci(
        self,
        data: Sequence[float] | np.ndarray,
        metric_fn: Callable = np.mean,
        n_bootstrap: int = 1000,
    ) -> CIResult:
        """Calculate bootstrap confidence interval for any metric.

        Args:
            data: Raw data values (e.g., runs per innings, balls faced)
            metric_fn: Function to compute the metric (default: mean)
            n_bootstrap: Number of bootstrap resamples

        Returns:
            CIResult with estimate, bounds, and margin of error
        """
        data = np.asarray(data, dtype=float)
        data = data[~np.isnan(data)]
        n = len(data)

        if n < 2:
            val = float(metric_fn(data)) if n == 1 else 0.0
            return CIResult(val, val, val, 0.0, self.confidence, "bootstrap", n)

        # Point estimate
        estimate = float(metric_fn(data))

        # Bootstrap resamples
        boot_stats = np.zeros(n_bootstrap)
        for i in range(n_bootstrap):
            sample = self.rng.choice(data, size=n, replace=True)
            boot_stats[i] = metric_fn(sample)

        # Percentile method
        alpha = 1 - self.confidence
        lower = float(np.percentile(boot_stats, alpha / 2 * 100))
        upper = float(np.percentile(boot_stats, (1 - alpha / 2) * 100))
        margin = (upper - lower) / 2

        return CIResult(estimate, lower, upper, margin, self.confidence, "bootstrap", n)

    def wilson_ci(self, successes: int, trials: int) -> CIResult:
        """Wilson score interval for proportions (e.g., boundary%, dot ball%).

        More accurate than normal approximation for extreme proportions
        or small sample sizes. Standard in cricket analytics.

        Args:
            successes: Number of events (e.g., boundaries hit)
            trials: Total attempts (e.g., balls faced)

        Returns:
            CIResult as percentage (0-100 scale)
        """
        if trials == 0:
            return CIResult(0.0, 0.0, 0.0, 0.0, self.confidence, "wilson", 0)

        p = successes / trials
        z = _z_score(self.confidence)
        n = trials

        denominator = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denominator
        spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

        lower = max(0.0, center - spread) * 100
        upper = min(1.0, center + spread) * 100
        estimate = p * 100
        margin = (upper - lower) / 2

        return CIResult(estimate, lower, upper, margin, self.confidence, "wilson", n)

    def strike_rate_ci(self, runs: int, balls: int, n_innings: int = 0) -> CIResult:
        """Confidence interval for batting strike rate.

        Uses bootstrap on per-ball run distribution if innings data available,
        otherwise uses Poisson approximation.
        """
        if balls == 0:
            return CIResult(0.0, 0.0, 0.0, 0.0, self.confidence, "strike_rate", 0)

        sr = (runs / balls) * 100
        # Poisson CI for rate: SR ± z * sqrt(SR^2 / balls)
        z = _z_score(self.confidence)
        se = sr / math.sqrt(balls)
        margin = z * se

        return CIResult(sr, sr - margin, sr + margin, margin, self.confidence, "poisson", balls)

    def economy_rate_ci(self, runs_conceded: int, balls_bowled: int) -> CIResult:
        """Confidence interval for bowling economy rate."""
        if balls_bowled == 0:
            return CIResult(0.0, 0.0, 0.0, 0.0, self.confidence, "economy", 0)

        overs = balls_bowled / 6
        economy = runs_conceded / overs
        z = _z_score(self.confidence)
        se = economy / math.sqrt(overs)
        margin = z * se

        return CIResult(
            economy,
            economy - margin,
            economy + margin,
            margin,
            self.confidence,
            "poisson",
            balls_bowled,
        )

    def average_ci(self, runs: int, dismissals: int) -> CIResult:
        """Confidence interval for batting/bowling average."""
        if dismissals == 0:
            return CIResult(
                float(runs),
                float(runs),
                float("inf"),
                float("inf"),
                self.confidence,
                "average",
                0,
            )

        avg = runs / dismissals
        z = _z_score(self.confidence)
        se = avg / math.sqrt(dismissals)
        margin = z * se

        return CIResult(
            avg,
            max(0, avg - margin),
            avg + margin,
            margin,
            self.confidence,
            "poisson",
            dismissals,
        )


def _z_score(confidence: float) -> float:
    """Get z-score for confidence level using common values."""
    z_table = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
    if confidence in z_table:
        return z_table[confidence]
    # Approximate using inverse normal
    from scipy.stats import norm

    return float(norm.ppf((1 + confidence) / 2))


if __name__ == "__main__":
    calc = ConfidenceCalculator()

    print("Confidence Interval Calculator (TKT-145)")
    print("=" * 50)

    # Example: Virat Kohli IPL career
    sr = calc.strike_rate_ci(runs=7263, balls=5430)
    print(f"\nStrike Rate:  {sr}")

    avg = calc.average_ci(runs=7263, dismissals=196)
    print(f"Batting Avg:  {avg}")

    boundary = calc.wilson_ci(successes=820, trials=5430)
    print(f"Boundary %:   {boundary}")

    econ = calc.economy_rate_ci(runs_conceded=450, balls_bowled=300)
    print(f"Economy Rate: {econ}")

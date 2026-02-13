"""
Cluster Label Position Guard Tests
====================================
Validates that top-order batters (avg_batting_position <= 2.5) never
receive the DEATH_FINISHER label, while middle/lower-order batters can.

Run with: pytest tests/test_cluster_labels.py -v
"""

import pandas as pd

from scripts.analysis.cross_tournament_enrichment import assign_label


# =============================================================================
# POSITION GUARD TESTS
# =============================================================================


class TestPositionGuard:
    """Test that position guard prevents top-order players from getting DEATH_FINISHER."""

    def test_opener_never_gets_finisher_label(self):
        """avg_pos=1.3, death_sr=180 -> NOT DEATH_FINISHER."""
        row = pd.Series(
            {
                "avg_batting_position": 1.3,
                "pp_sr": 160.0,
                "death_sr": 180.0,
                "death_boundary_pct": 25.0,
                "strike_rate": 145.0,
                "average": 30.0,
                "boundary_pct": 20.0,
            }
        )
        label = assign_label(row)
        assert label != "DEATH_FINISHER", (
            "Top-order batter (pos=1.3) got DEATH_FINISHER, expected different label"
        )
        assert label == "POWERPLAY_AGGRESSOR"

    def test_lower_order_gets_finisher_label(self):
        """avg_pos=5.0, death_sr=180 -> DEATH_FINISHER."""
        row = pd.Series(
            {
                "avg_batting_position": 5.0,
                "pp_sr": 130.0,
                "death_sr": 180.0,
                "death_boundary_pct": 25.0,
                "strike_rate": 145.0,
                "average": 25.0,
                "boundary_pct": 15.0,
            }
        )
        label = assign_label(row)
        assert label == "DEATH_FINISHER", (
            f"Lower-order batter (pos=5.0) should get DEATH_FINISHER, got {label}"
        )

    def test_position_threshold_boundary_at_2_5(self):
        """Edge case: avg_pos=2.5 (exactly at threshold) -> top-order, no DEATH_FINISHER."""
        row = pd.Series(
            {
                "avg_batting_position": 2.5,
                "pp_sr": 130.0,
                "death_sr": 180.0,
                "death_boundary_pct": 25.0,
                "strike_rate": 145.0,
                "average": 25.0,
                "boundary_pct": 20.0,
            }
        )
        label = assign_label(row)
        assert label != "DEATH_FINISHER", (
            f"Batter at threshold (pos=2.5) should NOT get DEATH_FINISHER, got {label}"
        )

    def test_position_threshold_just_above(self):
        """avg_pos=2.6 -> middle order, DEATH_FINISHER allowed."""
        row = pd.Series(
            {
                "avg_batting_position": 2.6,
                "pp_sr": 130.0,
                "death_sr": 180.0,
                "death_boundary_pct": 25.0,
                "strike_rate": 145.0,
                "average": 25.0,
                "boundary_pct": 15.0,
            }
        )
        label = assign_label(row)
        assert label == "DEATH_FINISHER", (
            f"Middle-order batter (pos=2.6) should get DEATH_FINISHER, got {label}"
        )

    def test_top_order_anchor(self):
        """Top-order with low SR and high avg -> ANCHOR."""
        row = pd.Series(
            {
                "avg_batting_position": 1.8,
                "pp_sr": 120.0,
                "death_sr": 140.0,
                "death_boundary_pct": 15.0,
                "strike_rate": 120.0,
                "average": 40.0,
                "boundary_pct": 14.0,
            }
        )
        label = assign_label(row)
        assert label == "ANCHOR"

    def test_top_order_boundary_hitter(self):
        """Top-order with high boundary% but not aggressive PP -> BOUNDARY_HITTER."""
        row = pd.Series(
            {
                "avg_batting_position": 2.0,
                "pp_sr": 140.0,
                "death_sr": 160.0,
                "death_boundary_pct": 22.0,
                "strike_rate": 140.0,
                "average": 28.0,
                "boundary_pct": 22.0,
            }
        )
        label = assign_label(row)
        assert label == "BOUNDARY_HITTER"

"""Tests for the Task Integrity Loop pipeline."""

from unittest.mock import MagicMock, patch

from scripts.claude_orchestrator.orchestration.pipeline import (
    GateResult,
    PipelineExecutor,
    PipelineResult,
    _parse_verdict,
)
from scripts.claude_orchestrator.orchestration.veto import (
    can_override,
    can_veto,
    get_veto_scope,
    outranks,
)


class TestParseVerdict:
    """Test verdict extraction from agent responses."""

    def test_approved(self):
        verdict, reason = _parse_verdict(
            "APPROVED: This improves the paid artifact directly.",
            ["APPROVED", "NOT APPROVED"],
        )
        assert verdict == "APPROVED"
        assert "improves" in reason.lower()

    def test_not_approved(self):
        verdict, reason = _parse_verdict(
            "NOT APPROVED: No buyer value.",
            ["APPROVED", "ANALYTICS ONLY", "NOT APPROVED"],
        )
        assert verdict == "NOT APPROVED"

    def test_yes(self):
        verdict, reason = _parse_verdict(
            "YES: Data is robust and baselines are clear.",
            ["YES", "NO", "FIX"],
        )
        assert verdict == "YES"

    def test_fix(self):
        verdict, reason = _parse_verdict(
            "FIX: Need to add sample size validation.",
            ["YES", "NO", "FIX"],
        )
        assert verdict == "FIX"
        assert "sample size" in reason.lower()

    def test_unknown_defaults(self):
        verdict, _ = _parse_verdict("Some random text", ["YES", "NO"])
        assert verdict == "UNKNOWN"


class TestGateResult:
    """Test GateResult passed logic."""

    def test_yes_passes(self):
        gate = GateResult(
            step=3,
            step_name="test",
            agent="test",
            verdict="YES",
            reason="",
            raw_response="",
        )
        assert gate.passed is True

    def test_approved_passes(self):
        gate = GateResult(
            step=1,
            step_name="test",
            agent="test",
            verdict="APPROVED",
            reason="",
            raw_response="",
        )
        assert gate.passed is True

    def test_analytics_only_passes(self):
        gate = GateResult(
            step=1,
            step_name="test",
            agent="test",
            verdict="ANALYTICS ONLY",
            reason="",
            raw_response="",
        )
        assert gate.passed is True

    def test_no_fails(self):
        gate = GateResult(
            step=3,
            step_name="test",
            agent="test",
            verdict="NO",
            reason="",
            raw_response="",
        )
        assert gate.passed is False

    def test_not_approved_fails(self):
        gate = GateResult(
            step=1,
            step_name="test",
            agent="test",
            verdict="NOT APPROVED",
            reason="",
            raw_response="",
        )
        assert gate.passed is False


class TestVetoRules:
    """Test veto rights enforcement."""

    def test_florentino_has_veto(self):
        assert can_veto("Florentino Perez") is True

    def test_kante_has_veto(self):
        assert can_veto("N'Golo Kante") is True

    def test_curry_no_veto(self):
        assert can_veto("Stephen Curry") is False

    def test_florentino_scope(self):
        scope = get_veto_scope("Florentino Perez")
        assert "paid artifact" in scope.lower()

    def test_founder_can_override_florentino(self):
        assert can_override("Founder", "Florentino Perez") is True

    def test_brady_can_override_flower(self):
        assert can_override("Tom Brady", "Andy Flower") is True

    def test_brady_cannot_override_florentino(self):
        assert can_override("Tom Brady", "Florentino Perez") is False

    def test_florentino_can_override_mourinho(self):
        assert can_override("Florentino Perez", "Jose Mourinho") is True

    def test_authority_hierarchy(self):
        assert outranks("Founder", "Florentino Perez")
        assert outranks("Florentino Perez", "Tom Brady")
        assert outranks("Tom Brady", "Stephen Curry")
        assert not outranks("Stephen Curry", "Tom Brady")


class TestPipelineResult:
    """Test pipeline result summary generation."""

    def test_summary_format(self):
        result = PipelineResult(ticket_id="TKT-042")
        result.gates.append(
            GateResult(
                step=1,
                step_name="Florentino Gate",
                agent="Florentino Perez",
                verdict="APPROVED",
                reason="Good for product",
                raw_response="APPROVED: Good",
            )
        )
        result.final_status = "PASSED"

        summary = result.summary()
        assert "TKT-042" in summary
        assert "PASSED" in summary
        assert "Florentino" in summary


class TestPipelineExecutor:
    """Test pipeline execution with mocked API calls."""

    @patch("scripts.claude_orchestrator.orchestration.pipeline.Coordinator")
    def test_full_pipeline_pass(self, MockCoordinator):
        """Simulate a full pipeline where all gates pass."""
        mock_coord = MockCoordinator.return_value

        # Mock chat responses for each gate
        responses = [
            # Step 1: Florentino
            ("APPROVED: Directly improves the magazine.", MagicMock()),
            # Step 3: Jose
            ("YES: Data is robust.", MagicMock()),
            # Step 3: Andy
            ("YES: Cricket-true.", MagicMock()),
            # Step 3: Pep
            ("YES: Structurally coherent.", MagicMock()),
            # Step 4: Tom Brady
            ("PASS: All checks verified.", MagicMock()),
            # Step 7: Kante
            ("PASS: Tests 253/253, Schema intact.", MagicMock()),
        ]
        mock_coord.chat.side_effect = responses

        executor = PipelineExecutor("TKT-042", coordinator=mock_coord)
        result = executor.run("Test PRD content", "Stephen Curry")

        assert result.final_status == "PASSED"
        assert len(result.gates) == 6

    @patch("scripts.claude_orchestrator.orchestration.pipeline.Coordinator")
    def test_pipeline_florentino_rejects(self, MockCoordinator):
        """Simulate Florentino rejecting at Step 1."""
        mock_coord = MockCoordinator.return_value
        mock_coord.chat.return_value = ("NOT APPROVED: No buyer value.", MagicMock())

        executor = PipelineExecutor("TKT-042", coordinator=mock_coord)
        result = executor.run("Test PRD", "Stephen Curry")

        assert result.final_status == "FAILED"
        assert len(result.gates) == 1
        assert result.gates[0].verdict == "NOT APPROVED"

    @patch("scripts.claude_orchestrator.orchestration.pipeline.Coordinator")
    def test_pipeline_domain_sanity_fix(self, MockCoordinator):
        """Simulate a FIX result from domain sanity."""
        mock_coord = MockCoordinator.return_value

        responses = [
            # Step 1: Florentino approves
            ("APPROVED: Good.", MagicMock()),
            # Step 3: Jose says FIX
            ("FIX: Need sample size validation.", MagicMock()),
            # Step 3: Andy approves
            ("YES: Cricket-true.", MagicMock()),
            # Step 3: Pep approves
            ("YES: Coherent.", MagicMock()),
        ]
        mock_coord.chat.side_effect = responses

        executor = PipelineExecutor("TKT-042", coordinator=mock_coord)
        result = executor.run("Test PRD", "Stephen Curry")

        assert result.final_status == "FIX_REQUIRED"

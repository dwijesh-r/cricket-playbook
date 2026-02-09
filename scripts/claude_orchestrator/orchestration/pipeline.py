"""
Execute the 8-step Task Integrity Loop as an automated pipeline.

Steps:
0. PRD (provided as input)
1. Florentino Gate
2. Build (assigned agent)
3. Domain Sanity (Jose + Andy + Pep — all must approve)
4. Enforcement Check (Tom Brady)
5. Commit & Ship (assigned agent)
6. Post Note (assigned agent)
7. System Check (Kante)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from scripts.claude_orchestrator.orchestration.coordinator import Coordinator


@dataclass
class GateResult:
    """Result from a single pipeline gate."""

    step: int
    step_name: str
    agent: str
    verdict: str  # YES, NO, FIX, APPROVED, NOT_APPROVED, PASS, FAIL
    reason: str
    raw_response: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    @property
    def passed(self) -> bool:
        return self.verdict.upper() in ("YES", "APPROVED", "PASS", "ANALYTICS ONLY")


@dataclass
class PipelineResult:
    """Full result from a pipeline execution."""

    ticket_id: str
    gates: list[GateResult] = field(default_factory=list)
    final_status: str = "PENDING"  # PASSED, FAILED, FIX_REQUIRED
    started_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.utcnow().isoformat() + "Z"

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"Pipeline Result: {self.ticket_id}",
            f"Status: {self.final_status}",
            f"Started: {self.started_at}",
            f"Completed: {self.completed_at or 'In Progress'}",
            "",
            "Gate Results:",
        ]
        for gate in self.gates:
            status = "PASS" if gate.passed else "FAIL"
            lines.append(
                f"  Step {gate.step} ({gate.step_name}): {status} — {gate.agent}: {gate.verdict}"
            )
            if gate.reason:
                lines.append(f"    Reason: {gate.reason}")
        return "\n".join(lines)


def _parse_verdict(response: str, valid_verdicts: list[str]) -> tuple[str, str]:
    """
    Extract a verdict and reason from an agent response.

    Looks for patterns like:
    - "APPROVED" / "NOT APPROVED"
    - "YES" / "NO" / "FIX: reason"
    - "PASS" / "FAIL"

    Returns:
        Tuple of (verdict, reason)
    """
    upper = response.upper()
    # Sort by length descending so "NOT APPROVED" matches before "APPROVED"
    for verdict in sorted(valid_verdicts, key=len, reverse=True):
        if verdict in upper:
            # Try to extract reason after the verdict
            idx = upper.index(verdict) + len(verdict)
            remainder = response[idx:].strip()
            # Clean up common separators
            for sep in (":", " - ", "\n"):
                if remainder.startswith(sep):
                    remainder = remainder[len(sep) :].strip()
            reason = remainder.split("\n")[0].strip() if remainder else ""
            return verdict, reason

    # Default: treat entire response as reason, verdict unknown
    return "UNKNOWN", response[:200]


class PipelineExecutor:
    """Execute the Task Integrity Loop for a ticket."""

    def __init__(self, ticket_id: str, coordinator: Optional[Coordinator] = None):
        self.ticket_id = ticket_id
        self.coordinator = coordinator or Coordinator()
        self.result = PipelineResult(ticket_id=ticket_id)

    def run(self, prd_content: str, assigned_agent: str) -> PipelineResult:
        """
        Execute the full 8-step pipeline.

        Args:
            prd_content: The PRD content (Step 0 input)
            assigned_agent: Agent assigned to build the ticket

        Returns:
            PipelineResult with all gate outcomes
        """
        print(f"\nStarting pipeline for {self.ticket_id}")
        print("=" * 50)

        # Step 1: Florentino Gate
        if not self._step1_florentino_gate(prd_content):
            self.result.final_status = "FAILED"
            self.result.completed_at = datetime.utcnow().isoformat() + "Z"
            return self.result

        # Step 2: Build (placeholder — actual build happens outside)
        print(f"\nStep 2: Build — Assigned to {assigned_agent}")
        print("(Build step is executed by the assigned agent outside the pipeline)")

        # Step 3: Domain Sanity
        if not self._step3_domain_sanity(prd_content, assigned_agent):
            # Check if any results are FIX
            fix_results = [g for g in self.result.gates if g.step == 3 and g.verdict == "FIX"]
            if fix_results:
                self.result.final_status = "FIX_REQUIRED"
            else:
                self.result.final_status = "FAILED"
            self.result.completed_at = datetime.utcnow().isoformat() + "Z"
            return self.result

        # Step 4: Enforcement Check
        if not self._step4_enforcement(prd_content):
            self.result.final_status = "FAILED"
            self.result.completed_at = datetime.utcnow().isoformat() + "Z"
            return self.result

        # Steps 5-6: Commit & Post Note (handled by assigned agent)
        print(f"\nStep 5-6: Commit & Post Note — {assigned_agent}")

        # Step 7: System Check
        if not self._step7_system_check():
            self.result.final_status = "FAILED"
            self.result.completed_at = datetime.utcnow().isoformat() + "Z"
            return self.result

        self.result.final_status = "PASSED"
        self.result.completed_at = datetime.utcnow().isoformat() + "Z"
        print(f"\nPipeline PASSED for {self.ticket_id}")
        return self.result

    def _step1_florentino_gate(self, prd_content: str) -> bool:
        """Step 1: Florentino Gate — does this improve the paid artifact?"""
        print("\nStep 1: Florentino Gate")
        prompt = (
            f"You are evaluating ticket {self.ticket_id} at the Florentino Gate.\n\n"
            f"## PRD Content\n\n{prd_content}\n\n"
            "## Your Decision\n\n"
            "Evaluate this task against these criteria:\n"
            "1. Who is the buyer?\n"
            "2. Why would they pay instead of reading free content?\n"
            "3. What preparation burden does this remove?\n"
            "4. If this feature is removed, does anyone notice?\n\n"
            "Respond with exactly one of:\n"
            "- APPROVED: [reason]\n"
            "- ANALYTICS ONLY: [reason]\n"
            "- NOT APPROVED: [reason]"
        )

        response, _ = self.coordinator.chat("Florentino Perez", prompt, ticket_id=self.ticket_id)
        verdict, reason = _parse_verdict(response, ["APPROVED", "ANALYTICS ONLY", "NOT APPROVED"])

        gate = GateResult(
            step=1,
            step_name="Florentino Gate",
            agent="Florentino Perez",
            verdict=verdict,
            reason=reason,
            raw_response=response,
        )
        self.result.gates.append(gate)
        print(f"  Verdict: {verdict}")
        return gate.passed

    def _step3_domain_sanity(self, prd_content: str, assigned_agent: str) -> bool:
        """Step 3: Domain Sanity — Jose, Andy, Pep must all approve."""
        print("\nStep 3: Domain Sanity Loop")

        reviewers = {
            "Jose Mourinho": "Is this robust with current data? Are baselines clear? Is this scalable?",
            "Andy Flower": "Would this make sense to a coach, analyst, or fan? Is it cricket-true?",
            "Pep Guardiola": "Is this structurally coherent? Does it contradict the system?",
        }

        all_passed = True
        for reviewer, question in reviewers.items():
            prompt = (
                f"You are reviewing ticket {self.ticket_id} for Domain Sanity.\n\n"
                f"## PRD Content\n\n{prd_content}\n\n"
                f"## Your Review Focus\n\n{question}\n\n"
                "Respond with exactly one of:\n"
                "- YES: [reason]\n"
                "- NO: [reason]\n"
                "- FIX: [specific fix needed]"
            )

            response, _ = self.coordinator.chat(reviewer, prompt, ticket_id=self.ticket_id)
            verdict, reason = _parse_verdict(response, ["YES", "NO", "FIX"])

            gate = GateResult(
                step=3,
                step_name=f"Domain Sanity ({reviewer})",
                agent=reviewer,
                verdict=verdict,
                reason=reason,
                raw_response=response,
            )
            self.result.gates.append(gate)
            print(f"  {reviewer}: {verdict}")

            if not gate.passed:
                all_passed = False

        return all_passed

    def _step4_enforcement(self, prd_content: str) -> bool:
        """Step 4: Enforcement Check — Tom Brady verifies process."""
        print("\nStep 4: Enforcement Check")

        # Summarize gate results so far
        gate_summary = "\n".join(
            f"- Step {g.step} ({g.agent}): {g.verdict}" for g in self.result.gates
        )

        prompt = (
            f"You are performing the Enforcement Check for {self.ticket_id}.\n\n"
            f"## PRD Content\n\n{prd_content}\n\n"
            f"## Gate Results So Far\n\n{gate_summary}\n\n"
            "## Checklist\n"
            "1. Was the Task Integrity Loop followed (Steps 0-3)?\n"
            "2. Were any FIX items resolved?\n"
            "3. Was only the approved scope built?\n"
            "4. Is documentation ready?\n\n"
            "Respond with:\n"
            "- PASS: [notes]\n"
            "- FAIL: [issues]"
        )

        response, _ = self.coordinator.chat("Tom Brady", prompt, ticket_id=self.ticket_id)
        verdict, reason = _parse_verdict(response, ["PASS", "FAIL"])

        gate = GateResult(
            step=4,
            step_name="Enforcement Check",
            agent="Tom Brady",
            verdict=verdict,
            reason=reason,
            raw_response=response,
        )
        self.result.gates.append(gate)
        print(f"  Verdict: {verdict}")
        return gate.passed

    def _step7_system_check(self) -> bool:
        """Step 7: System Check — Kante verifies technical integrity."""
        print("\nStep 7: System Check")

        prompt = (
            f"You are performing the System Check for {self.ticket_id}.\n\n"
            "## Checklist\n"
            "1. Is the schema intact (no breaking changes)?\n"
            "2. Are manifests updated?\n"
            "3. Are all tests passing?\n"
            "4. Are there any regressions?\n\n"
            "Respond with:\n"
            "- PASS: Tests [X/Y passing], Schema [status], Manifests [status]\n"
            "- FAIL: [issues]"
        )

        response, _ = self.coordinator.chat("N'Golo Kante", prompt, ticket_id=self.ticket_id)

        # Kante uses N'Golo Kanté in config but we normalize
        verdict, reason = _parse_verdict(response, ["PASS", "FAIL"])

        gate = GateResult(
            step=7,
            step_name="System Check",
            agent="N'Golo Kante",
            verdict=verdict,
            reason=reason,
            raw_response=response,
        )
        self.result.gates.append(gate)
        print(f"  Verdict: {verdict}")
        return gate.passed

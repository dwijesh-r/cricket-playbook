"""
Token usage tracking per agent, ticket, and sprint.

Append-only JSONL storage at .mission-control/token_usage/usage.jsonl.
Follows the audit.jsonl pattern from JsonStore._log_audit().
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from scripts.claude_orchestrator import TOKEN_DATA_DIR


class TokenTracker:
    """Track token usage across agents, tickets, and sprints."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or TOKEN_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._usage_file = self.data_dir / "usage.jsonl"

    def record(
        self,
        agent: str,
        input_tokens: int,
        output_tokens: int,
        ticket_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """
        Record a token usage event.

        Args:
            agent: Agent name
            input_tokens: Input tokens consumed
            output_tokens: Output tokens consumed
            ticket_id: Optional ticket ID (e.g., "TKT-042")
            sprint_id: Optional sprint ID (e.g., "SPRINT-004")
            model: Model ID used
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": agent,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "ticket_id": ticket_id,
            "sprint_id": sprint_id,
            "model": model,
        }

        with open(self._usage_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _load_entries(self) -> list[dict]:
        """Load all usage entries from JSONL."""
        if not self._usage_file.exists():
            return []
        entries = []
        with open(self._usage_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def report_by_agent(self) -> dict[str, dict]:
        """
        Aggregate token usage by agent.

        Returns:
            Dict mapping agent name -> {input_tokens, output_tokens, total_tokens, calls}
        """
        entries = self._load_entries()
        report: dict[str, dict] = {}
        for entry in entries:
            agent = entry["agent"]
            if agent not in report:
                report[agent] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "calls": 0,
                }
            report[agent]["input_tokens"] += entry["input_tokens"]
            report[agent]["output_tokens"] += entry["output_tokens"]
            report[agent]["total_tokens"] += entry["total_tokens"]
            report[agent]["calls"] += 1
        return report

    def report_by_ticket(self, ticket_id: Optional[str] = None) -> dict[str, dict]:
        """
        Aggregate token usage by ticket.

        Args:
            ticket_id: If provided, return only this ticket's data

        Returns:
            Dict mapping ticket_id -> {input_tokens, output_tokens, total_tokens, calls}
        """
        entries = self._load_entries()
        report: dict[str, dict] = {}
        for entry in entries:
            tid = entry.get("ticket_id")
            if not tid:
                continue
            if ticket_id and tid != ticket_id:
                continue
            if tid not in report:
                report[tid] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "calls": 0,
                }
            report[tid]["input_tokens"] += entry["input_tokens"]
            report[tid]["output_tokens"] += entry["output_tokens"]
            report[tid]["total_tokens"] += entry["total_tokens"]
            report[tid]["calls"] += 1
        return report

    def report_by_sprint(self, sprint_id: Optional[str] = None) -> dict[str, dict]:
        """
        Aggregate token usage by sprint.

        Args:
            sprint_id: If provided, return only this sprint's data

        Returns:
            Dict mapping sprint_id -> {input_tokens, output_tokens, total_tokens, calls}
        """
        entries = self._load_entries()
        report: dict[str, dict] = {}
        for entry in entries:
            sid = entry.get("sprint_id")
            if not sid:
                continue
            if sprint_id and sid != sprint_id:
                continue
            if sid not in report:
                report[sid] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "calls": 0,
                }
            report[sid]["input_tokens"] += entry["input_tokens"]
            report[sid]["output_tokens"] += entry["output_tokens"]
            report[sid]["total_tokens"] += entry["total_tokens"]
            report[sid]["calls"] += 1
        return report

    def total_usage(self) -> dict:
        """Get total token usage across all entries."""
        entries = self._load_entries()
        total = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "calls": len(entries),
        }
        for entry in entries:
            total["input_tokens"] += entry["input_tokens"]
            total["output_tokens"] += entry["output_tokens"]
            total["total_tokens"] += entry["total_tokens"]
        return total

"""
Scoreboard View for Mission Control.

Displays agent performance metrics and sprint progress.
"""

from typing import Optional
from collections import defaultdict
from scripts.mission_control.models.ticket import Ticket
from scripts.mission_control.models.sprint import Sprint
from scripts.mission_control.models.epic import Epic


class ScoreboardView:
    """Scoreboard visualization for sprint and agent metrics."""

    @classmethod
    def render(cls, sprint_id: Optional[str] = None) -> str:
        """
        Render the scoreboard.

        Args:
            sprint_id: Sprint to show (defaults to active sprint)

        Returns:
            Formatted string for display
        """
        # Get sprint
        if sprint_id:
            sprint = Sprint.get(sprint_id)
        else:
            sprint = Sprint.get_active()

        lines = []
        lines.append("")
        lines.append("=" * 70)
        lines.append("🏆 SCOREBOARD")
        lines.append("=" * 70)

        if sprint:
            lines.extend(cls._render_sprint_section(sprint))
            lines.extend(cls._render_agent_section(sprint))
            lines.extend(cls._render_epic_section(sprint))
        else:
            lines.append("")
            lines.append("No active sprint found.")
            lines.append("Use: mc sprint create --title '...' --start YYYY-MM-DD --end YYYY-MM-DD")

        lines.append("=" * 70)
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def _render_sprint_section(cls, sprint: Sprint) -> list[str]:
        """Render sprint metrics section."""
        lines = []

        lines.append("")
        lines.append(f"📅 {sprint.title}")
        lines.append(f"   {sprint.start_date} → {sprint.end_date}")
        lines.append("-" * 50)

        # Progress
        total_tickets = len(sprint.tickets)
        done_tickets = 0
        for ticket_id in sprint.tickets:
            ticket = Ticket.get(ticket_id)
            if ticket and ticket.state == "DONE":
                done_tickets += 1

        progress = (done_tickets / total_tickets * 100) if total_tickets > 0 else 0

        # Progress bar
        bar_width = 30
        filled = int(bar_width * progress / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        lines.append(f"   Progress: [{bar}] {progress:.1f}%")
        lines.append(f"   Tickets: {done_tickets}/{total_tickets} complete")

        # Velocity
        velocity = sprint.velocity
        if velocity.planned_points > 0:
            velocity_pct = velocity.completion_pct
            lines.append(
                f"   Velocity: {velocity.completed_points}/{velocity.planned_points} points ({velocity_pct:.1f}%)"
            )

        # LLM Budget
        budget = sprint.llm_budget
        budget_pct = budget.utilization_pct
        lines.append(
            f"   LLM Budget: {budget.used_tokens:,}/{budget.total_tokens:,} tokens ({budget_pct:.1f}%)"
        )

        return lines

    @classmethod
    def _render_agent_section(cls, sprint: Sprint) -> list[str]:
        """Render agent metrics section."""
        lines = []
        lines.append("")
        lines.append("👥 AGENT PERFORMANCE")
        lines.append("-" * 50)

        # Collect agent stats
        agent_stats = defaultdict(lambda: {"assigned": 0, "done": 0, "running": 0, "blocked": 0})

        for ticket_id in sprint.tickets:
            ticket = Ticket.get(ticket_id)
            if not ticket or not ticket.assignee:
                continue

            agent = ticket.assignee
            agent_stats[agent]["assigned"] += 1

            if ticket.state == "DONE":
                agent_stats[agent]["done"] += 1
            elif ticket.state == "RUNNING":
                agent_stats[agent]["running"] += 1
            elif ticket.state == "BLOCKED":
                agent_stats[agent]["blocked"] += 1

        if agent_stats:
            # Header
            lines.append(
                f"   {'Agent':<20} {'Done':<8} {'Running':<10} {'Blocked':<10} {'Total':<8}"
            )
            lines.append("   " + "-" * 56)

            # Sort by done count
            sorted_agents = sorted(agent_stats.items(), key=lambda x: x[1]["done"], reverse=True)

            for agent, stats in sorted_agents:
                lines.append(
                    f"   {agent:<20} "
                    f"{stats['done']:<8} "
                    f"{stats['running']:<10} "
                    f"{stats['blocked']:<10} "
                    f"{stats['assigned']:<8}"
                )
        else:
            lines.append("   No agent data available")

        return lines

    @classmethod
    def _render_epic_section(cls, sprint: Sprint) -> list[str]:
        """Render EPIC progress section."""
        lines = []
        lines.append("")
        lines.append("📊 EPIC PROGRESS")
        lines.append("-" * 50)

        if sprint.epics:
            for epic_id in sprint.epics:
                epic = Epic.get(epic_id)
                if epic:
                    epic.calculate_progress()
                    bar_width = 20
                    filled = int(bar_width * epic.progress_pct / 100)
                    bar = "█" * filled + "░" * (bar_width - filled)
                    lines.append(f"   {epic.id}: [{bar}] {epic.progress_pct}%")
                    lines.append(f"      {epic.title[:40]}")
        else:
            lines.append("   No EPICs in this sprint")

        return lines

    @classmethod
    def to_json(cls, sprint_id: Optional[str] = None) -> dict:
        """Export scoreboard as JSON."""
        if sprint_id:
            sprint = Sprint.get(sprint_id)
        else:
            sprint = Sprint.get_active()

        if not sprint:
            return {"error": "No sprint found"}

        # Calculate metrics
        agent_stats = defaultdict(lambda: {"assigned": 0, "done": 0, "running": 0})

        for ticket_id in sprint.tickets:
            ticket = Ticket.get(ticket_id)
            if ticket and ticket.assignee:
                agent_stats[ticket.assignee]["assigned"] += 1
                if ticket.state == "DONE":
                    agent_stats[ticket.assignee]["done"] += 1
                elif ticket.state == "RUNNING":
                    agent_stats[ticket.assignee]["running"] += 1

        return {
            "view": "scoreboard",
            "sprint": {
                "id": sprint.id,
                "title": sprint.title,
                "start_date": sprint.start_date,
                "end_date": sprint.end_date,
            },
            "velocity": sprint.velocity.to_dict(),
            "llm_budget": sprint.llm_budget.to_dict(),
            "agents": dict(agent_stats),
        }

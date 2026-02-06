"""
Kanban Board View for Mission Control.

Displays tickets organized by workflow state in a board format.
"""

from typing import Optional

from scripts.mission_control.models.sprint import Sprint
from scripts.mission_control.models.ticket import VALID_STATES, Ticket


class KanbanView:
    """Kanban board visualization."""

    # Column widths for display
    COL_WIDTH = 20
    STATES = VALID_STATES

    @classmethod
    def render(
        cls,
        sprint_id: Optional[str] = None,
        assignee: Optional[str] = None,
        compact: bool = False,
    ) -> str:
        """
        Render the Kanban board.

        Args:
            sprint_id: Filter by sprint
            assignee: Filter by assignee
            compact: Use compact view

        Returns:
            Formatted string for display
        """
        # Get tickets
        tickets = Ticket.list(sprint_id=sprint_id, assignee=assignee)

        # Group by state
        by_state = {state: [] for state in cls.STATES}
        for ticket in tickets:
            if ticket.state in by_state:
                by_state[ticket.state].append(ticket)

        # Build output
        lines = []

        # Header
        if sprint_id:
            sprint = Sprint.get(sprint_id)
            title = f"📋 Kanban Board - {sprint.title if sprint else sprint_id}"
        else:
            title = "📋 Kanban Board - All Tickets"

        lines.append("")
        lines.append("=" * 100)
        lines.append(title)
        lines.append("=" * 100)

        if compact:
            return cls._render_compact(lines, by_state)
        else:
            return cls._render_full(lines, by_state)

    @classmethod
    def _render_compact(cls, lines: list, by_state: dict) -> str:
        """Render compact view."""
        # State headers
        header = ""
        for state in cls.STATES:
            count = len(by_state[state])
            header += f"{state}({count})".ljust(14)
        lines.append(header)
        lines.append("-" * 100)

        # Find max tickets in any column
        max_tickets = max(len(tickets) for tickets in by_state.values())

        # Render rows
        for i in range(max_tickets):
            row = ""
            for state in cls.STATES:
                tickets = by_state[state]
                if i < len(tickets):
                    t = tickets[i]
                    cell = f"{t.id}"[:12].ljust(14)
                else:
                    cell = " " * 14
                row += cell
            lines.append(row)

        lines.append("=" * 100)
        return "\n".join(lines)

    @classmethod
    def _render_full(cls, lines: list, by_state: dict) -> str:
        """Render full view with details."""
        for state in cls.STATES:
            tickets = by_state[state]
            count = len(tickets)

            # State icon
            icon = cls._state_icon(state)

            lines.append("")
            lines.append(f"{icon} {state} ({count})")
            lines.append("-" * 50)

            if tickets:
                for t in tickets:
                    priority_icon = cls._priority_icon(t.priority)
                    assignee = t.assignee[:15] if t.assignee else "-"
                    title = t.title[:35] + ".." if len(t.title) > 35 else t.title
                    lines.append(f"  {priority_icon} {t.id}: {title}")
                    lines.append(f"      Assignee: {assignee} | Progress: {t.progress_pct}%")
            else:
                lines.append("  (empty)")

        lines.append("")
        lines.append("=" * 100)

        # Summary
        total = sum(len(tickets) for tickets in by_state.values())
        done = len(by_state["DONE"])
        in_progress = len(by_state["RUNNING"])
        blocked = len(by_state["BLOCKED"])

        lines.append(
            f"Total: {total} | Done: {done} | In Progress: {in_progress} | Blocked: {blocked}"
        )
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _state_icon(state: str) -> str:
        """Get icon for state."""
        icons = {
            "IDEA": "💡",
            "BACKLOG": "📝",
            "READY": "🎯",
            "RUNNING": "🔄",
            "BLOCKED": "🚫",
            "REVIEW": "👀",
            "VALIDATION": "⏳",
            "DONE": "✅",
        }
        return icons.get(state, "•")

    @staticmethod
    def _priority_icon(priority: str) -> str:
        """Get icon for priority."""
        icons = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "🟢"}
        return icons.get(priority, "⚪")

    @classmethod
    def to_json(cls, sprint_id: Optional[str] = None) -> dict:
        """
        Export Kanban view as JSON.

        Args:
            sprint_id: Filter by sprint

        Returns:
            Dict suitable for JSON serialization
        """
        tickets = Ticket.list(sprint_id=sprint_id)

        by_state = {state: [] for state in cls.STATES}
        for ticket in tickets:
            if ticket.state in by_state:
                by_state[ticket.state].append(
                    {
                        "id": ticket.id,
                        "title": ticket.title,
                        "priority": ticket.priority,
                        "assignee": ticket.assignee,
                        "progress_pct": ticket.progress_pct,
                    }
                )

        return {
            "view": "kanban",
            "sprint_id": sprint_id,
            "columns": by_state,
            "total_tickets": sum(len(t) for t in by_state.values()),
        }

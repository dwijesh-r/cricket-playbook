"""
Cockpit View for Mission Control.

Displays agent-centric view of current assignments and workload.
"""

from collections import defaultdict
from typing import Optional

from scripts.mission_control.models.ticket import Ticket
from scripts.mission_control.workflow.state_machine import StateMachine


class CockpitView:
    """Agent cockpit visualization."""

    # Role definitions for agents
    AGENT_ROLES = {
        "Florentino Perez": "Product Owner",
        "Tom Brady": "Delivery Owner",
        "Stephen Curry": "Executor",
        "Virat Kohli": "Executor",
        "Kevin de Bruyne": "Executor",
        "Brock Purdy": "Data Pipeline",
        "Jose Mourinho": "Validator",
        "Andy Flower": "Validator",
        "Pep Guardiola": "Validator",
        "N'Golo Kanté": "QA",
        "Brad Stevens": "Architect",
        "Ime Udoka": "ML Ops",
    }

    @classmethod
    def render(cls, agent: Optional[str] = None) -> str:
        """
        Render the cockpit view.

        Args:
            agent: Specific agent to show (None for all)

        Returns:
            Formatted string for display
        """
        lines = []
        lines.append("")
        lines.append("=" * 70)
        lines.append("🎮 AGENT COCKPIT")
        lines.append("=" * 70)

        if agent:
            lines.extend(cls._render_single_agent(agent))
        else:
            lines.extend(cls._render_all_agents())

        lines.append("=" * 70)
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def _render_single_agent(cls, agent: str) -> list[str]:
        """Render cockpit for a single agent."""
        lines = []

        role = cls.AGENT_ROLES.get(agent, "Unknown")
        lines.append("")
        lines.append(f"👤 {agent}")
        lines.append(f"   Role: {role}")
        lines.append("-" * 50)

        # Get assigned tickets
        tickets = Ticket.list(assignee=agent)

        if not tickets:
            lines.append("   No tickets assigned")
            return lines

        # Group by state
        by_state = defaultdict(list)
        for t in tickets:
            by_state[t.state].append(t)

        # Active work (RUNNING)
        if "RUNNING" in by_state:
            lines.append("")
            lines.append("   🔄 ACTIVE WORK:")
            for t in by_state["RUNNING"]:
                lines.append(f"      {t.id}: {t.title[:40]}")
                ti_status = StateMachine.get_task_integrity_status(t)
                lines.append(f"         Step: {ti_status['current_step']}")

        # Ready to pick up
        if "READY" in by_state:
            lines.append("")
            lines.append("   🎯 READY TO START:")
            for t in by_state["READY"]:
                lines.append(f"      {t.id}: {t.title[:40]} [{t.priority}]")

        # In review
        if "REVIEW" in by_state:
            lines.append("")
            lines.append("   👀 IN REVIEW:")
            for t in by_state["REVIEW"]:
                gate_summary = t.get_gate_summary()
                lines.append(f"      {t.id}: {t.title[:40]}")
                ds = gate_summary.get("domain_sanity", {})
                lines.append(f"         Domain Sanity: {ds.get('approvals', 0)}/3")

        # Blocked
        if "BLOCKED" in by_state:
            lines.append("")
            lines.append("   🚫 BLOCKED:")
            for t in by_state["BLOCKED"]:
                lines.append(f"      {t.id}: {t.title[:40]}")

        # Summary
        lines.append("")
        lines.append(f"   Total Assigned: {len(tickets)}")

        return lines

    @classmethod
    def _render_all_agents(cls) -> list[str]:
        """Render cockpit summary for all agents."""
        lines = []

        # Collect all ticket assignments
        all_tickets = Ticket.list()
        agent_work = defaultdict(lambda: {"running": 0, "ready": 0, "blocked": 0, "total": 0})

        for t in all_tickets:
            if not t.assignee:
                continue
            agent_work[t.assignee]["total"] += 1
            if t.state == "RUNNING":
                agent_work[t.assignee]["running"] += 1
            elif t.state == "READY":
                agent_work[t.assignee]["ready"] += 1
            elif t.state == "BLOCKED":
                agent_work[t.assignee]["blocked"] += 1

        lines.append("")
        lines.append(f"{'Agent':<25} {'Role':<15} {'Active':<8} {'Ready':<8} {'Blocked':<8}")
        lines.append("-" * 70)

        # Sort by active work
        sorted_agents = sorted(agent_work.items(), key=lambda x: x[1]["running"], reverse=True)

        for agent, stats in sorted_agents:
            role = cls.AGENT_ROLES.get(agent, "Unknown")[:14]
            status = "🟢" if stats["blocked"] == 0 else "🔴"
            lines.append(
                f"{status} {agent:<23} {role:<15} "
                f"{stats['running']:<8} {stats['ready']:<8} {stats['blocked']:<8}"
            )

        # Unassigned tickets
        unassigned = [t for t in all_tickets if not t.assignee]
        if unassigned:
            lines.append("")
            lines.append(f"⚠️  Unassigned Tickets: {len(unassigned)}")
            for t in unassigned[:5]:  # Show first 5
                lines.append(f"   • {t.id}: {t.title[:40]} [{t.state}]")
            if len(unassigned) > 5:
                lines.append(f"   ... and {len(unassigned) - 5} more")

        return lines

    @classmethod
    def to_json(cls, agent: Optional[str] = None) -> dict:
        """Export cockpit as JSON."""
        all_tickets = Ticket.list()

        if agent:
            tickets = [t for t in all_tickets if t.assignee == agent]
            by_state = defaultdict(list)
            for t in tickets:
                by_state[t.state].append({"id": t.id, "title": t.title, "priority": t.priority})

            return {
                "view": "cockpit",
                "agent": agent,
                "role": cls.AGENT_ROLES.get(agent, "Unknown"),
                "tickets_by_state": dict(by_state),
                "total": len(tickets),
            }
        else:
            agent_stats = defaultdict(lambda: {"running": 0, "ready": 0, "blocked": 0, "total": 0})

            for t in all_tickets:
                if t.assignee:
                    agent_stats[t.assignee]["total"] += 1
                    if t.state == "RUNNING":
                        agent_stats[t.assignee]["running"] += 1
                    elif t.state == "READY":
                        agent_stats[t.assignee]["ready"] += 1
                    elif t.state == "BLOCKED":
                        agent_stats[t.assignee]["blocked"] += 1

            return {
                "view": "cockpit",
                "agents": dict(agent_stats),
                "unassigned": len([t for t in all_tickets if not t.assignee]),
            }

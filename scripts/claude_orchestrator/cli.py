#!/usr/bin/env python3
"""
Claude Orchestrator CLI - Multi-agent orchestration for Cricket Playbook.

Usage:
    orchestrator agent list
    orchestrator agent chat <name> [--ticket TKT-XXX]
    orchestrator agent dispatch <ticket-id>
    orchestrator pipeline run <ticket-id> --prd <file> --agent <name>
    orchestrator token report [--by agent|ticket|sprint]
"""

import argparse
import sys

from scripts.claude_orchestrator import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="orchestrator",
        description="Claude Orchestrator - Multi-agent orchestration for Cricket Playbook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  orchestrator agent list
  orchestrator agent chat "Tom Brady"
  orchestrator agent chat "Stephen Curry" --ticket TKT-001
  orchestrator agent dispatch TKT-042
  orchestrator pipeline run TKT-042 --prd governance/tasks/TKT-042_prd.md --agent "Stephen Curry"
  orchestrator token report --by agent
        """,
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"Claude Orchestrator v{__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Agent subcommands
    agent_parser = subparsers.add_parser("agent", help="Agent operations")
    agent_sub = agent_parser.add_subparsers(dest="agent_command")

    # agent list
    agent_sub.add_parser("list", help="List all agents with config")

    # agent chat
    chat_parser = agent_sub.add_parser("chat", help="Chat with an agent")
    chat_parser.add_argument("name", help="Agent name (e.g., 'Tom Brady')")
    chat_parser.add_argument("--ticket", help="Ticket ID for context")

    # agent dispatch
    dispatch_parser = agent_sub.add_parser("dispatch", help="Dispatch ticket to agent")
    dispatch_parser.add_argument("ticket_id", help="Ticket ID (e.g., TKT-042)")

    # Pipeline subcommands
    pipeline_parser = subparsers.add_parser("pipeline", help="Pipeline operations")
    pipeline_sub = pipeline_parser.add_subparsers(dest="pipeline_command")

    # pipeline run
    run_parser = pipeline_sub.add_parser("run", help="Run Task Integrity Loop")
    run_parser.add_argument("ticket_id", help="Ticket ID")
    run_parser.add_argument("--prd", required=True, help="Path to PRD file")
    run_parser.add_argument("--agent", required=True, help="Assigned agent name")

    # Token subcommands
    token_parser = subparsers.add_parser("token", help="Token usage reporting")
    token_sub = token_parser.add_subparsers(dest="token_command")

    # token report
    report_parser = token_sub.add_parser("report", help="Show token usage report")
    report_parser.add_argument(
        "--by",
        choices=["agent", "ticket", "sprint", "total"],
        default="agent",
        help="Grouping for report",
    )

    return parser


def cmd_agent_list(args: argparse.Namespace) -> int:
    """List all agents with their configuration."""
    from scripts.claude_orchestrator.config.agent_parser import parse_all_agents
    from scripts.claude_orchestrator.config.model_mapping import resolve

    agents = parse_all_agents()

    print(f"\nClaude Orchestrator — {len(agents)} Agents")
    print(f"{'─' * 90}")
    print(f"{'Name':<22} {'Temp':>5} {'Model':<32} {'Veto':>5} {'Role Snippet'}")
    print(f"{'─' * 90}")

    for name in sorted(agents.keys()):
        config = agents[name]
        api_model = resolve(config.model)
        has_veto = "YES" if config.veto_authority else "—"
        # Truncate description for display
        snippet = (
            config.description[:35] + "..." if len(config.description) > 38 else config.description
        )

        print(f"{name:<22} {config.temperature:>5.2f} {api_model:<32} {has_veto:>5} {snippet}")

    print(f"{'─' * 90}\n")
    return 0


def cmd_agent_chat(args: argparse.Namespace) -> int:
    """Interactive chat with an agent."""
    from scripts.claude_orchestrator.orchestration.coordinator import Coordinator

    agent_name = args.name
    ticket_id = getattr(args, "ticket", None)

    print(f"\nChatting with {agent_name}")
    if ticket_id:
        print(f"Context: {ticket_id}")
    print("Type 'quit' or 'exit' to end. Type 'clear' to reset conversation.\n")

    coordinator = Coordinator()
    conversation = None

    while True:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye.")
            return 0
        if user_input.lower() == "clear":
            conversation = None
            print("Conversation cleared.\n")
            continue

        try:
            print(f"\n{agent_name} > ", end="", flush=True)
            full_response = []
            for chunk in coordinator.chat_stream(
                agent_name,
                user_input,
                ticket_id=ticket_id,
                conversation=conversation,
            ):
                print(chunk, end="", flush=True)
                full_response.append(chunk)
            print("\n")

            # Update conversation reference for next turn
            if conversation is None:
                # Retrieve the conversation that was created
                convs = coordinator._conversations.list_conversations(agent_name)
                if convs:
                    conversation = coordinator._conversations.load(agent_name, convs[-1])
        except ValueError as e:
            print(f"\nError: {e}")
            return 1
        except Exception as e:
            print(f"\nAPI Error: {e}")
            return 1

    return 0


def cmd_agent_dispatch(args: argparse.Namespace) -> int:
    """Dispatch a ticket to its assigned agent."""
    from scripts.claude_orchestrator.orchestration.coordinator import Coordinator

    coordinator = Coordinator()
    print(f"\nDispatching {args.ticket_id}...")

    try:
        response = coordinator.dispatch(args.ticket_id)
        print(f"\n{response}\n")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


def cmd_pipeline_run(args: argparse.Namespace) -> int:
    """Run the Task Integrity Loop pipeline."""
    from pathlib import Path
    from scripts.claude_orchestrator.orchestration.pipeline import PipelineExecutor

    prd_path = Path(args.prd)
    if not prd_path.exists():
        print(f"Error: PRD file not found: {args.prd}")
        return 1

    prd_content = prd_path.read_text(encoding="utf-8")

    try:
        executor = PipelineExecutor(args.ticket_id)
        result = executor.run(prd_content, args.agent)
        print(f"\n{result.summary()}\n")
        return 0 if result.final_status == "PASSED" else 1
    except Exception as e:
        print(f"Pipeline error: {e}")
        return 1


def cmd_token_report(args: argparse.Namespace) -> int:
    """Show token usage report."""
    from scripts.claude_orchestrator.core.token_tracker import TokenTracker

    tracker = TokenTracker()
    group_by = getattr(args, "by", "agent")

    if group_by == "total":
        total = tracker.total_usage()
        print("\nTotal Token Usage")
        print(f"{'─' * 40}")
        print(f"  Input tokens:  {total['input_tokens']:>12,}")
        print(f"  Output tokens: {total['output_tokens']:>12,}")
        print(f"  Total tokens:  {total['total_tokens']:>12,}")
        print(f"  API calls:     {total['calls']:>12,}")
        print(f"{'─' * 40}\n")
        return 0

    if group_by == "agent":
        report = tracker.report_by_agent()
    elif group_by == "ticket":
        report = tracker.report_by_ticket()
    elif group_by == "sprint":
        report = tracker.report_by_sprint()
    else:
        report = tracker.report_by_agent()

    if not report:
        print("\nNo token usage data found.\n")
        return 0

    print(f"\nToken Usage by {group_by.title()}")
    print(f"{'─' * 75}")
    print(f"{'Key':<25} {'Input':>12} {'Output':>12} {'Total':>12} {'Calls':>8}")
    print(f"{'─' * 75}")

    for key in sorted(report.keys()):
        data = report[key]
        print(
            f"{key:<25} {data['input_tokens']:>12,} "
            f"{data['output_tokens']:>12,} {data['total_tokens']:>12,} "
            f"{data['calls']:>8,}"
        )

    print(f"{'─' * 75}\n")
    return 0


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "agent":
        cmd = getattr(args, "agent_command", None)
        if cmd == "list":
            return cmd_agent_list(args)
        elif cmd == "chat":
            return cmd_agent_chat(args)
        elif cmd == "dispatch":
            return cmd_agent_dispatch(args)
        else:
            parser.parse_args(["agent", "--help"])
            return 0
    elif args.command == "pipeline":
        cmd = getattr(args, "pipeline_command", None)
        if cmd == "run":
            return cmd_pipeline_run(args)
        else:
            parser.parse_args(["pipeline", "--help"])
            return 0
    elif args.command == "token":
        cmd = getattr(args, "token_command", None)
        if cmd == "report":
            return cmd_token_report(args)
        else:
            parser.parse_args(["token", "--help"])
            return 0
    elif args.command is None:
        parser.print_help()
        return 0
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

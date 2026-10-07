"""Command-line interface for Daily Workout.

Usage:
    python -m daily_workout.cli profile
    python -m daily_workout.cli today
    python -m daily_workout.cli log
    python -m daily_workout.cli history
    python -m daily_workout.cli reset
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date

from . import agent, store

# Windows consoles default to cp1252 and can crash on unicode output.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer or default


def _csv(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def cmd_profile() -> int:
    p = store.get_profile()
    print("Set your profile (Enter keeps the current value).\n")
    goal = _ask("Goal (e.g. build strength / lose fat / general fitness)", p.get("goal", "general fitness"))
    level = _ask("Level (beginner / intermediate / advanced)", p.get("level", "beginner"))
    days = _ask("Days per week", str(p.get("days_per_week", 3)))
    equipment = _ask("Equipment (comma-separated)", ", ".join(p.get("equipment", ["dumbbells"])))
    injuries = _ask("Injuries (comma-separated, or leave blank)", ", ".join(p.get("injuries", [])))
    dislikes = _ask("Dislikes (comma-separated, or leave blank)", ", ".join(p.get("dislikes", [])))

    try:
        days_int = int(days)
    except ValueError:
        days_int = 3

    store.set_profile(
        {
            "goal": goal,
            "level": level,
            "days_per_week": days_int,
            "equipment": _csv(equipment),
            "injuries": _csv(injuries),
            "dislikes": _csv(dislikes),
        }
    )
    print("\nProfile saved to runtime/data/profile.json.")
    return 0


def _print_plan(plan: dict) -> None:
    if not plan:
        print("No plan saved yet. Run `today`.")
        return
    print(f"\nToday's session — {plan.get('objective', '')} ({plan.get('date', '')})")
    for block in plan.get("blocks", []):
        print(f"\n  {block.get('name', '')}")
        for item in block.get("items", []):
            print(f"    - {item}")
    if plan.get("notes"):
        print(f"\n  Note: {plan['notes']}")


def cmd_today() -> int:
    result = asyncio.run(agent.today())
    output = result.get("output") if isinstance(result, dict) else str(result)
    print("\n[coach] " + (output or "").strip())
    _print_plan(store.get_plan())
    return 0


def cmd_log() -> int:
    print("Log a completed session.\n")
    focus = _ask("Focus (e.g. push / legs / full body)", "full body")
    difficulty = _ask("Difficulty 1-5 (1 = easy, 5 = maximal)", "3")
    note = _ask("Note (how it felt, any pain)", "")
    try:
        diff_int = max(1, min(5, int(difficulty)))
    except ValueError:
        diff_int = 3
    entry = {
        "date": date.today().isoformat(),
        "focus": focus,
        "difficulty": diff_int,
        "note": note,
    }
    store.add_log(entry)
    print(f"\nLogged: {entry['date']} · {focus} · difficulty {diff_int}")
    if diff_int >= 4 or "pain" in note.lower():
        print("Noted. Tomorrow's session will ease off the affected movement.")
    return 0


def cmd_history() -> int:
    logs = store.get_logs()
    if not logs:
        print("No sessions logged yet.")
    else:
        print(f"Recent sessions ({len(logs)} total):\n")
        for entry in logs[-10:]:
            print(
                f"  {entry.get('date', '?')} · {entry.get('focus', '')} · "
                f"difficulty {entry.get('difficulty', '?')}"
                + (f" · {entry['note']}" if entry.get("note") else "")
            )
    _print_plan(store.get_plan())
    return 0


def cmd_reset() -> int:
    store.reset()
    print("Cleared logs and today's plan (runtime/data/profile.json kept).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="daily-workout", description="Daily Workout CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("profile", "set your profile"),
        ("today", "get today's session"),
        ("log", "log a completed session"),
        ("history", "show recent sessions and today's plan"),
        ("reset", "clear logs and today's plan"),
    ):
        sub.add_parser(name, help=help_text)

    args = parser.parse_args(argv)

    if args.command == "profile":
        return cmd_profile()
    if args.command == "today":
        return cmd_today()
    if args.command == "log":
        return cmd_log()
    if args.command == "history":
        return cmd_history()
    if args.command == "reset":
        return cmd_reset()
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())

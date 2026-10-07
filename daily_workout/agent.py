"""Build and run the Daily Workout agent on openjiuwen."""

from __future__ import annotations

from datetime import date
from typing import Any

from . import config, runtime, tools

SYSTEM_PROMPT = """You are Daily Workout, a safe and practical daily fitness coach.

You have these tools:
- get_profile(): the athlete's goal, level, days/week, equipment, injuries, dislikes.
- save_profile(profile_json).
- recent_sessions(n): the last logged sessions.
- save_plan(plan_json): save today's session.
- log_session(entry_json): record a completed session.

When asked for today's session:
1. Call get_profile and recent_sessions first.
2. Respect every injury and only use available equipment.
3. Keep the session 30-50 minutes, in three blocks:
   warm-up, main work, cool-down.
4. Progress the load only if recent sessions felt easy (difficulty <= 2).
   If a session felt hard (difficulty >= 4) or mentions pain, reduce or swap the movement.
5. Never prescribe an exercise that conflicts with a listed injury or dislike.
6. Save the plan with save_plan, using JSON:
   {"date": "...", "objective": "...", "blocks": [{"name": "...", "items": ["..."]}], "notes": "..."}
7. Reply with a short plain-text summary (do not paste the JSON back).

This is general fitness guidance, not medical advice. If pain is mentioned, advise stopping.
"""

_runner_started = False


async def _ensure_runner() -> None:
    global _runner_started
    if not _runner_started:
        from openjiuwen.core.runner import Runner

        try:
            await Runner.start()
        except Exception:
            pass
        _runner_started = True


def build_agent():
    """Create the Daily Workout ``DeepAgent``."""
    from openjiuwen.harness import create_deep_agent

    runtime.setup()

    rails: list[Any] = []
    if config.has_embedding():
        try:
            from openjiuwen.harness.rails import MemoryRail

            rails.append(MemoryRail(embedding_config=config.embedding_config()))
        except Exception:
            rails = []

    return create_deep_agent(
        model=config.make_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=tools.ALL_TOOLS,
        rails=rails,
        enable_task_loop=False,
        max_iterations=20,
        workspace=runtime.workspace(),
    )


async def _run(query: str) -> dict[str, Any]:
    from openjiuwen.core.runner import Runner

    config.validate()
    await _ensure_runner()
    agent = build_agent()
    result = await Runner.run_agent(agent, {"query": query})
    return result if isinstance(result, dict) else {"output": str(result)}


async def today() -> dict[str, Any]:
    """Generate and save today's session."""
    return await _run(
        f"Today is {date.today().isoformat()}. Give me today's session. "
        "Check my profile and recent sessions first, then save the plan with today's date."
    )


async def coach(question: str) -> dict[str, Any]:
    """Ask the coach anything (e.g. adapt tomorrow, explain a swap)."""
    return await _run(question)

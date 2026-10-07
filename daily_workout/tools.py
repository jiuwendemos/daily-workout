"""The agent's tools — thin wrappers over :mod:`daily_workout.store`."""

from __future__ import annotations

import json
from typing import Any

from openjiuwen.core.foundation.tool import tool

from . import store


def _parse(raw: Any) -> Any:
    if isinstance(raw, (list, dict)):
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        return json.loads(text)
    raise ValueError(f"unsupported payload type: {type(raw)!r}")


@tool(
    name="get_profile",
    description="Return the athlete profile as JSON (goal, level, days_per_week, equipment, injuries, dislikes).",
    input_params={"type": "object", "properties": {}, "required": []},
)
def get_profile() -> str:
    return json.dumps(store.get_profile(), ensure_ascii=False)


@tool(
    name="save_profile",
    description=(
        "Save the athlete profile. profile_json has keys: goal (string), level (string), "
        "days_per_week (int), equipment (array of strings), injuries (array of strings), "
        "dislikes (array of strings)."
    ),
    input_params={
        "type": "object",
        "properties": {"profile_json": {"type": "string", "description": "JSON object string."}},
        "required": ["profile_json"],
    },
)
def save_profile(profile_json: str) -> str:
    store.set_profile(_parse(profile_json))
    return "profile saved"


@tool(
    name="recent_sessions",
    description="Return the most recent logged sessions as a JSON array, newest last.",
    input_params={
        "type": "object",
        "properties": {"n": {"type": "integer", "description": "How many recent sessions (default 10)."}},
        "required": [],
    },
)
def recent_sessions(n: int = 10) -> str:
    return json.dumps(store.recent_logs(int(n or 10)), ensure_ascii=False)


@tool(
    name="save_plan",
    description=(
        "Save today's session. plan_json: an object with keys date (string), objective (string), "
        "blocks (array of {name, items: [strings]}), notes (string)."
    ),
    input_params={
        "type": "object",
        "properties": {"plan_json": {"type": "string", "description": "JSON object string."}},
        "required": ["plan_json"],
    },
)
def save_plan(plan_json: str) -> str:
    store.set_plan(_parse(plan_json))
    return "plan saved"


@tool(
    name="log_session",
    description=(
        "Log a completed session. entry_json: an object with keys date (string), focus (string), "
        "difficulty (integer 1-5), note (string)."
    ),
    input_params={
        "type": "object",
        "properties": {"entry_json": {"type": "string", "description": "JSON object string."}},
        "required": ["entry_json"],
    },
)
def log_session(entry_json: str) -> str:
    store.add_log(_parse(entry_json))
    return "session logged"


ALL_TOOLS = [get_profile, save_profile, recent_sessions, save_plan, log_session]

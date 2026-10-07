"""Local JSON state: profile, session logs, and today's plan."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import json_store, runtime

DATA_DIR = runtime.DATA_DIR
PROFILE_PATH = DATA_DIR / "profile.json"
LOGS_PATH = DATA_DIR / "logs.json"
PLAN_PATH = DATA_DIR / "plan.json"


def _read(path: Path, default: Any) -> Any:
    return json_store.read_json(path, default)


def _write(path: Path, data: Any) -> None:
    json_store.write_json(path, data)


# --- profile ---------------------------------------------------------------

def get_profile() -> dict[str, Any]:
    return _read(PROFILE_PATH, {})


def set_profile(profile: dict[str, Any]) -> dict[str, Any]:
    _write(PROFILE_PATH, profile)
    return profile


# --- logs ------------------------------------------------------------------

def get_logs() -> list[dict[str, Any]]:
    logs = _read(LOGS_PATH, [])
    return logs if isinstance(logs, list) else []


def add_log(entry: dict[str, Any]) -> dict[str, Any]:
    logs = get_logs()
    logs.append(entry)
    _write(LOGS_PATH, logs)
    return entry


def recent_logs(n: int = 10) -> list[dict[str, Any]]:
    return get_logs()[-n:]


# --- plan ------------------------------------------------------------------

def get_plan() -> dict[str, Any]:
    return _read(PLAN_PATH, {})


def set_plan(plan: dict[str, Any]) -> dict[str, Any]:
    _write(PLAN_PATH, plan)
    return plan


# --- reset -----------------------------------------------------------------

def reset() -> None:
    for path in (LOGS_PATH, PLAN_PATH):
        if path.exists():
            path.unlink()

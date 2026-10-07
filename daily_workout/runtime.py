"""Runtime directory layout and logging setup (self-contained)."""

from __future__ import annotations

from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent  # daily_workout/
PROJECT_ROOT = _PACKAGE_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
WORKSPACE_DIR = RUNTIME_DIR / "workspace"
LOG_DIR = RUNTIME_DIR / "logs"
DATA_DIR = RUNTIME_DIR / "data"

_configured = False


def setup() -> None:
    global _configured
    if _configured:
        return
    for directory in (WORKSPACE_DIR, LOG_DIR, DATA_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    try:
        from openjiuwen.core.common.logging.log_config import configure_log_config

        configure_log_config(
            {
                "backend": "default",
                "level": "INFO",
                "log_path": str(LOG_DIR),
                "output": ["file"],
                "interface_output": ["file"],
                "performance_output": ["file"],
            }
        )
    except Exception:
        pass
    _configured = True


def workspace() -> str:
    return str(WORKSPACE_DIR)

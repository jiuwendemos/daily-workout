# Daily Workout

A daily fitness coach you open every day. It gives you **today's session** — warm-up, main work, cool-down — tailored to your goal, level, equipment, and injuries. You log what you did and how hard it felt; tomorrow's session adapts.

Built on [openjiuwen](https://github.com/openJiuwen-ai/agent-core). **No third-party integrations** — your profile and logs are local files; only the model is called.

## Daily use

1. `profile` once — goal, level, days/week, equipment, injuries.
2. `today` — get today's session.
3. `log` — record what you did and how it felt (1–5).
4. Next `today` — it progresses when it was easy and swaps moves when something hurts.

## Setup

This machine already has a working openjiuwen environment. Point at one of the repo venvs — `pip`/`python` are not on PATH here.

```powershell
$PY = "C:\Workspace\openjiuwen\jiuwenswarm\.venv\Scripts\python.exe"
# $PY = "C:\Workspace\openjiuwen\agent-core\.venv\Scripts\python.exe"

# Streamlit is only needed for the web UI (the CLI needs nothing extra)
& $PY -m pip install streamlit
```

`.env` is already filled in. If you reuse this elsewhere, copy `.env.example` and set `MODEL_PROVIDER`, `API_BASE`, `API_KEY`, `MODEL_NAME`.

## Use

Run from the `daily-workout` folder.

```powershell
# set your profile (interactive)
& $PY -m daily_workout.cli profile

# today's session
& $PY -m daily_workout.cli today

# log a completed session
& $PY -m daily_workout.cli log

# see recent sessions
& $PY -m daily_workout.cli history
```

Or the web UI:

```powershell
& $PY -m streamlit run daily_workout/ui.py
```

Or the one-line launcher:

```powershell
.\run.ps1
```

## Project layout

```
daily-workout/
├── runtime/                  # generated state, gitignored (created on first run)
│   ├── workspace/            # DeepAgent workspace scaffold
│   ├── logs/                 # openjiuwen logs
│   └── data/
│       ├── profile.json      # your goal, level, equipment, injuries
│       ├── logs.json         # completed sessions
│       └── plan.json         # today's session
├── daily_workout/
│   ├── config.py             # model config from env
│   ├── runtime.py            # runtime dir + logging setup
│   ├── store.py              # local JSON state
│   ├── tools.py              # the agent's tools (@tool)
│   ├── agent.py              # builds the DeepAgent + runs it
│   ├── cli.py                # profile / today / log / history / reset
│   └── ui.py                 # Streamlit UI
├── .env
└── requirements.txt
```

## How it uses openjiuwen

- `openjiuwen.harness.create_deep_agent` — assembles the agent with our tools and prompt.
- `openjiuwen.core.foundation.tool.tool` — each action is a `@tool`.
- `openjiuwen.core.runner.Runner.run_agent` — runs the agent.
- `openjiuwen.harness.rails.MemoryRail` — optional memory (enabled when `EMBED_*` is set); otherwise constraints live in `runtime/data/profile.json`.

## Notes

- Not medical advice. Review the plan and stop if something hurts. Lower `LLM_TEMPERATURE` for more stable output.

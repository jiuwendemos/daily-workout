"""Streamlit UI for Daily Workout.

Run:
    streamlit run daily_workout/ui.py
"""

from __future__ import annotations

import asyncio
from datetime import date

import streamlit as st

from daily_workout import agent, store

st.set_page_config(page_title="Daily Workout", page_icon="🏋️", layout="wide")

st.title("🏋️ Daily Workout")
st.caption("Your daily session, adapted from how the last one felt.")

with st.sidebar:
    st.header("Profile")
    profile = store.get_profile()
    goal = st.text_input("Goal", value=profile.get("goal", "general fitness"))
    level = st.text_input("Level", value=profile.get("level", "beginner"))
    days = st.number_input("Days / week", min_value=1, max_value=7, value=int(profile.get("days_per_week", 3)))
    equipment = st.text_input("Equipment (comma-separated)", value=", ".join(profile.get("equipment", [])))
    injuries = st.text_input("Injuries (comma-separated)", value=", ".join(profile.get("injuries", [])))
    if st.button("Save profile"):
        store.set_profile(
            {
                "goal": goal,
                "level": level,
                "days_per_week": int(days),
                "equipment": [x.strip() for x in equipment.split(",") if x.strip()],
                "injuries": [x.strip() for x in injuries.split(",") if x.strip()],
                "dislikes": profile.get("dislikes", []),
            }
        )
        st.success("Profile saved.")

    st.divider()
    if st.button("Generate today's session", type="primary"):
        with st.spinner("Coaching…"):
            try:
                result = asyncio.run(agent.today())
                msg = result.get("output") if isinstance(result, dict) else str(result)
                if msg:
                    st.write(msg)
            except SystemExit as exc:
                st.error(str(exc))
            except Exception as exc:  # noqa: BLE001
                st.exception(exc)

    if st.button("Reset (keep profile)"):
        store.reset()
        st.rerun()

plan = store.get_plan()
tab_today, tab_log, tab_history = st.tabs(["Today", "Log", "History"])

with tab_today:
    if not plan:
        st.info("No plan yet. Click “Generate today's session” in the sidebar.")
    else:
        st.subheader(f"{plan.get('objective', '')}")
        st.caption(plan.get("date", ""))
        for block in plan.get("blocks", []):
            st.markdown(f"**{block.get('name', '')}**")
            for item in block.get("items", []):
                st.markdown(f"- {item}")
        if plan.get("notes"):
            st.info(plan["notes"])

with tab_log:
    with st.form("log_form"):
        focus = st.text_input("Focus", value="full body")
        difficulty = st.slider("Difficulty", 1, 5, 3)
        note = st.text_input("Note (how it felt, any pain)")
        submitted = st.form_submit_button("Log session")
    if submitted:
        store.add_log(
            {
                "date": date.today().isoformat(),
                "focus": focus,
                "difficulty": difficulty,
                "note": note,
            }
        )
        st.success("Logged. Tomorrow's session will adapt.")

with tab_history:
    logs = store.get_logs()
    if not logs:
        st.info("No sessions logged yet.")
    for entry in reversed(logs[-20:]):
        st.markdown(
            f"- **{entry.get('date', '?')}** · {entry.get('focus', '')} · "
            f"difficulty {entry.get('difficulty', '?')}"
            + (f" — {entry['note']}" if entry.get("note") else "")
        )

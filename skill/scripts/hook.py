#!/usr/bin/env python3
"""Claude Code hook for Remodel: practice the active cards inside every session.

  hook.py session   register under SessionStart: tells Claude which cards are active
  hook.py prompt    register under UserPromptSubmit: when a card's trigger matches the
                    prompt, asks Claude to put the card's question to the user (once per
                    session per card) and cautions the user when a pattern repeats in a day

Reads only this profile's ledger (<$CLAUDE_CONFIG_DIR or ~/.claude>/remodel/state.json), so each
Claude Code profile practises its own cards. Any problem exits 0 silently; a session is never blocked.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

PROFILE = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude").expanduser()
DATA = Path(os.environ.get("REMODEL_HOME") or PROFILE / "remodel")
STATE = DATA / "state.json"
NUDGES = DATA / "nudges.jsonl"


def read_state():
    try:
        state = json.loads(STATE.read_text())
    except (OSError, ValueError):
        return None
    return state if state.get("active") else None


def in_scope(state, cwd):
    scope = state.get("scope") or []
    return not scope or any(s.lower() in cwd.lower() for s in scope)


def recent_nudges():
    try:
        with NUDGES.open("rb") as fh:
            fh.seek(0, 2)
            start = max(fh.tell() - 65536, 0)
            fh.seek(start)
            lines = fh.read().decode(errors="ignore").splitlines()
            if start:
                lines = lines[1:]  # first line is cut in half when reading from the middle
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def log_nudge(entry):
    DATA.mkdir(parents=True, exist_ok=True)
    with NUDGES.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")


def on_session(state):
    cards = state["active"]
    lines = ["Remodel is active. The user is practising these thinking cards:"]
    for c in cards:
        lines.append(f'- {c["title"]}: when {c["when"]}, the question is "{c["question"]}"')
    lines.append("When a card's moment comes up, ask its question once, in one short line, then carry on with the request.")
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(lines)},
            "systemMessage": "Remodel · practising: " + " · ".join(c["title"] for c in cards)}


def on_prompt(state, payload):
    text = payload.get("prompt") or ""
    session = payload.get("session_id") or ""
    today = time.strftime("%Y-%m-%d")
    history = recent_nudges()
    context, warnings = [], []
    for card in state["active"]:
        try:
            if not re.search(card.get("trigger") or r"(?!)", text):
                continue
        except re.error:
            continue
        first_in_session = not any(n.get("card") == card["id"] and n.get("session") == session and n.get("fired")
                                   for n in history)
        count_today = 1 + sum(1 for n in history if n.get("card") == card["id"] and n.get("day") == today)
        log_nudge({"ts": time.time(), "day": today, "session": session, "card": card["id"], "fired": first_in_session})
        if first_in_session:
            context.append(f'Remodel card "{card["title"]}" matched this prompt. Practise it now: '
                           f'{card.get("agent_line") or "ask the card question"} The card question is "{card["question"]}". '
                           "Keep it to one short line and do it once in this session.")
        limit = int(card.get("caution_after") or 0)
        if limit and count_today == limit:
            warnings.append(f'Remodel: "{card["old"]}" has come up {count_today} times today. {card["question"]}')
    out = {}
    if context:
        out["hookSpecificOutput"] = {"hookEventName": "UserPromptSubmit", "additionalContext": "\n".join(context)}
    if warnings:
        out["systemMessage"] = " ".join(warnings)
    return out


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    state = read_state()
    if not state or not in_scope(state, payload.get("cwd") or os.getcwd()):
        return
    out = on_session(state) if event == "session" else on_prompt(state, payload) if event == "prompt" else {}
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never block a session because of the coach
        pass

#!/usr/bin/env python3
"""Render a /remodel report.json into the Claude artifact page, then update the card ledger.

Usage: render.py <report.json> [--pdf] [--out-dir DIR]   write the page (and optionally a PDF)
       render.py --set-url <artifact url>                remember where the page is published
Exits 2 with a list of problems when the report does not match the format, so it can be fixed.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DAY_START, PROFILE, STATE, day_start, load_json, merge_patterns,  # noqa: E402
                    read_cards, read_personas, runs_today, save_json)
import page  # noqa: E402

CHROMES = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium",
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
           "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
CARD_STATUSES = {"new", "installing", "installed", "queued"}
PROBLEM_STATUSES = {"new", "repeating", "still"}


def plain(text):
    """Lower case, straight quotes and apostrophes, single spaces: for matching quotes to their source."""
    text = str(text or "").lower().translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))
    return " ".join(text.split())


def validate(report, cards, personas):
    problems = []
    if report.get("mode") not in ("normal", "goal"):
        problems.append('mode must be "normal" or "goal"')
    if report.get("mode") == "goal" and not report.get("goal"):
        problems.append("goal mode needs a goal")
    if not isinstance(report.get("verdict"), str) or not report["verdict"].strip():
        problems.append("verdict must be one headline sentence")
    window = report.get("window")
    if not (isinstance(window, dict) and window.get("from") and window.get("to")):
        problems.append("window must be collect.py's window object (from, to, days, typed_prompts)")
    if len(report.get("facts", [])) > 3:
        problems.append("keep at most 3 facts")

    persona = report.get("persona")
    pfile, steps = None, []
    if persona is not None:
        pfile = personas.get(persona.get("id"))
        if not pfile:
            problems.append(f"persona {persona.get('id')!r} has no persona file")
        else:
            steps = [plain(x) for x in pfile.get("voice", {}).get("steps", [])]
            source = plain(Path(pfile["path"]).read_text())

    items = report.get("problems")
    if not isinstance(items, list) or not 1 <= len(items) <= 3:
        problems.append("problems must list 1-3 problems")
        items = []
    ids = [p.get("id") for p in items]
    if len(set(ids)) != len(ids):
        problems.append("problem ids must be unique")
    questions = 0
    active = 0
    persona_card = False
    for i, p in enumerate(items):
        where = f"problems[{i}]"
        for key in ("id", "tab", "title", "call", "old", "new"):
            if not str(p.get(key) or "").strip():
                problems.append(f"{where} is missing {key}")
        if p.get("status") not in PROBLEM_STATUSES:
            problems.append(f"{where}.status must be one of {sorted(PROBLEM_STATUSES)}")
        ev = p.get("evidence") or {}
        if not ev.get("summary") or not [x for x in ev.get("prompts", []) if x.get("quote")]:
            problems.append(f"{where}.evidence needs a summary and at least one dated prompt")
        st = p.get("steps") or []
        if not 3 <= len(st) <= 7 or any(not s.get("name") or not s.get("text") for s in st):
            problems.append(f"{where}.steps needs 3-7 steps, each with name and text")
        elif steps and [plain(s.get("name")).rstrip(".") for s in st] != steps:
            problems.append(f"{where}.steps must follow the persona's steps in order: {' | '.join(pfile['voice']['steps'])}")
        dl = p.get("deadline") or {}
        if not dl.get("when") or not dl.get("done"):
            problems.append(f"{where}.deadline needs when and done")
        q = p.get("quote") or {}
        if q:
            if not q.get("text") or not q.get("source"):
                problems.append(f"{where}.quote needs text and source")
            elif pfile:
                for segment in page.QUOTED.findall(q["text"]):
                    if plain(segment) not in source:
                        problems.append(f"{where}.quote puts words in quotation marks that are not in the persona file: "
                                        f"{segment[:60]!r}. Quote the file exactly or drop the quotation marks")
        for j, qq in enumerate(p.get("questions") or []):
            questions += 1
            if not qq.get("id") or not qq.get("text"):
                problems.append(f"{where}.questions[{j}] needs an id and text")
            if len(qq.get("options", [])) > 5:
                problems.append(f"{where}.questions[{j}] has more than 5 options")
        c = p.get("card")
        if c:
            if c.get("id") not in cards:
                problems.append(f"card {c.get('id')!r} has no card file (write it to <profile>/remodel/cards first)")
            elif persona and cards[c["id"]].get("persona") == persona.get("id"):
                persona_card = True
            if c.get("status") not in CARD_STATUSES:
                problems.append(f"card {c.get('id')!r}: status must be one of {sorted(CARD_STATUSES)}")
            elif c["status"] in ("new", "installing"):
                active += 1
    if questions > 3:
        problems.append("keep at most 3 questions across all problems")
    if active > 2:
        problems.append(f"{active} cards are active; keep at most 2 so practice stays focused")
    if pfile and pfile.get("cards") and not persona_card:
        problems.append(f"with a persona, one problem's card should be a {persona.get('id')} card (active or queued)")

    ins = report.get("insights") or {}
    process = ins.get("process") or []
    if not 1 <= len(process) <= 3:
        problems.append("insights.process needs 1-3 rules")
    for j, x in enumerate(process):
        if not x.get("when") or not x.get("rule") or x.get("problem") not in ids:
            problems.append(f"insights.process[{j}] needs when, rule and a problem id from problems")
    do_first = ins.get("do_first") or []
    if not 1 <= len(do_first) <= 5 or any(not x.get("when") or not x.get("text") for x in do_first):
        problems.append("insights.do_first needs 1-5 items, each with when and text")
    for j, m in enumerate(ins.get("models") or []):
        if not m.get("old") or not m.get("new") or m.get("problem") not in ids:
            problems.append(f"insights.models[{j}] needs old, new and a problem id from problems")
    if len(ins.get("calls", [])) > 3:
        problems.append("keep at most 3 goal calls")
    setup = report.get("setup", [])
    if len(setup) > 3:
        problems.append("keep at most 3 setup items")
    for j, f in enumerate(setup):
        for key in ("title", "where", "prompt"):
            if not f.get(key):
                problems.append(f"setup[{j}] is missing {key}")
    return problems


def find_chrome():
    if os.environ.get("REMODEL_CHROME"):
        return os.environ["REMODEL_CHROME"]
    for path in CHROMES:
        if Path(path).exists():
            return path
    for name in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(name):
            return shutil.which(name)
    return None


def to_pdf(html_path, pdf_path):
    chrome = find_chrome()
    if not chrome:
        return "no Chrome or Chromium found; set REMODEL_CHROME to a Chromium binary"
    if pdf_path.exists():
        pdf_path.unlink()
    with tempfile.TemporaryDirectory() as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--disable-extensions", "--no-first-run",
               "--no-default-browser-check", f"--user-data-dir={profile}", "--no-pdf-header-footer",
               "--print-to-pdf-no-header", f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Headless Chrome sometimes keeps running after the PDF is written, so watch the file
        # and stop Chrome once its size has settled instead of waiting for it to exit.
        last_size, deadline = -1, time.time() + 90
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            size = pdf_path.stat().st_size if pdf_path.exists() else -1
            if size > 1000 and size == last_size:
                break
            last_size = size
            time.sleep(0.5)
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
        return "Chrome produced no PDF"
    return None


def update_state(report, cards, pdf, today, run_dir):
    current = load_json(STATE, {}) or {}
    if not runs_today(current, today):
        save_json(DAY_START, {"date": today, "state": current})
    # A rerun on the same day starts from the ledger as it stood before the day's first run, so the
    # day keeps one entry and earlier same-day runs leave no streaks, cards or history behind.
    state = day_start(current, today) or {}
    state["patterns"] = merge_patterns(state.get("patterns"), report, today)
    previous = {c["id"]: c for c in state.get("active", [])}
    installed = {i["id"]: i for i in state.get("installed", [])}
    active, queued = [], []
    for p in report.get("problems", []):
        c = p.get("card")
        if not c:
            continue
        d = cards[c["id"]]
        if c["status"] == "installed":
            installed.setdefault(c["id"], {"id": c["id"], "installed_on": today})
        elif c["status"] == "queued":
            queued.append(c["id"])
        else:
            active.append({
                "id": c["id"], "type": d.get("type"), "title": c.get("title") or d.get("title"),
                "old": c.get("old") or d.get("old"), "when": c.get("when") or d.get("when"),
                "question": c.get("question") or d.get("question"),
                "trigger": d.get("trigger"), "agent_line": d.get("agent_line"),
                "caution_after": int(d.get("caution_after") or 0),
                "since": previous.get(c["id"], {}).get("since", today), "uses": int(c.get("uses") or 0),
                "problem": p.get("id"),
            })
    queue = list(dict.fromkeys(queued + report.get("queue", [])))
    state.update({
        "version": 2, "profile": str(PROFILE), "mode": report["mode"], "updated": dt.datetime.now().isoformat(timespec="seconds"),
        "goal": report.get("goal") if report["mode"] == "goal" else state.get("goal"),
        "scope": report.get("scope", state.get("scope", [])),
        "persona": (report.get("persona") or {}).get("id"),
        "active": active, "installed": list(installed.values()), "queue": queue,
    })
    entry = {"date": today, "at": dt.datetime.now().isoformat(timespec="seconds"), "mode": report["mode"],
             "run": str(run_dir), "report": str(pdf), "persona": (report.get("persona") or {}).get("id"),
             "window": report.get("window"), "problems": [p.get("id") for p in report.get("problems", [])],
             "active": [a["id"] for a in active], "uses": {a["id"]: a["uses"] for a in active}}
    state.setdefault("history", []).append(entry)
    save_json(STATE, state)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report", nargs="?")
    ap.add_argument("--pdf", action="store_true", help="also write a printable PDF")
    ap.add_argument("--no-pdf", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--set-url", help="record the published artifact URL in the ledger")
    ap.add_argument("--out-dir", help="where to write the page and PDF (default: next to report.json)")
    args = ap.parse_args(argv)

    if args.set_url:
        state = load_json(STATE, {}) or {}
        state["artifact_url"] = args.set_url
        save_json(STATE, state)
        print(json.dumps({"artifact_url": args.set_url}))
        return
    if not args.report:
        ap.error("give a report.json path, or --set-url")

    report = load_json(args.report)
    if not isinstance(report, dict):
        print(f"cannot read {args.report} as JSON", file=sys.stderr)
        sys.exit(2)
    cards = read_cards()
    personas = read_personas()
    problems = validate(report, cards, personas)
    if problems:
        print("report.json needs fixes:\n- " + "\n- ".join(problems), file=sys.stderr)
        sys.exit(2)

    today = dt.date.today().isoformat()
    out = Path(args.out_dir) if args.out_dir else Path(args.report).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    page_path = out / "page.html"
    patterns = merge_patterns((load_json(STATE, {}) or {}).get("patterns"), report, today)
    html = page.build(report, cards, today, patterns, personas)
    page_path.write_text(html)
    pdf_path, error = None, None
    if args.pdf:
        stem = f"remodel-{today}-{report['mode']}"
        print_path = out / f"{stem}.html"
        # The printed copy is the same page with every fold opened.
        print_path.write_text('<!doctype html><html><head><meta charset="utf-8"></head><body>'
                              + html.replace("<details>", "<details open>") + "</body></html>")
        pdf_path = out / f"{stem}.pdf"
        error = to_pdf(print_path, pdf_path)
        if error:
            pdf_path = None
    update_state(report, cards, page_path, today, Path(args.report).resolve().parent)
    state = load_json(STATE, {}) or {}
    print(json.dumps({"page": str(page_path), "pdf": str(pdf_path) if pdf_path else None, "pdf_error": error,
                      "artifact_url": state.get("artifact_url"), "state": str(STATE)}))

if __name__ == "__main__":
    main()

"""End-to-end tests for the Remodel scripts. Run: python3 -m unittest discover -s tests"""
import json
import re
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skill" / "scripts"


def run(script, *args, home, stdin=None, profile=None):
    env = dict(os.environ, REMODEL_HOME=str(home))
    if profile:
        env["CLAUDE_CONFIG_DIR"] = str(profile)
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], input=stdin,
                          capture_output=True, text=True, env=env, timeout=60)


def history_row(text, minutes_ago, project="/Users/x/Documents/personal/Acme/projects", session="s1"):
    return json.dumps({"display": text, "timestamp": int((time.time() - minutes_ago * 60) * 1000),
                       "project": project, "sessionId": session})


CARD = {"id": "think-at-scale", "type": "model", "title": "Think at scale", "old": "Fix it for this one",
        "when": "a one-off fix", "question": "Does this work for 100,000 customers without me?",
        "trigger": r"(?i)\b(query i can execute|sql)\b", "agent_line": "Offer the general version.",
        "caution_after": 3, "since": "2026-10-01", "uses": 0}


PERSONA = """---
id: zed
name: Zed Example
essence: Ship the smallest true thing
best_for: deciding what to cut
watch_out: Burning out the team
---
# Zed Example: Ship the smallest true thing

## Mental models
### Ship the smallest true thing
- **Belief:** "a shipped draft beats a perfect plan" [1].

## Bottleneck checks
| Bottleneck | You see it when | Fix |
|---|---|---|
| Polishing | you ask to polish | What ships today? |

## Voice
- **Tone:** Short and direct.
- **Steps:** Cut | Ship | Learn
- **Deadlines:** Tonight.
- **Lands like:** Ship it tonight.

## Practice cards
```yaml
id: zed-ship-it
type: process            # changes the order of steps
title: Ship the smallest piece
old: Polish before shipping
when: you keep polishing
question: What is the smallest piece a customer can use today?
trigger: '(?i)\\b(polish|perfect)\\b'
proof: '(?i)\\b(ship it|smallest)\\b'
agent_line: Name the smallest shippable piece.
```

## Sources
[1] Example source
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "remodel-home"

    def tearDown(self):
        self.tmp.cleanup()

    def write_persona(self, text=PERSONA, name="zed.md"):
        folder = self.home / "personas"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text)

    def write_state(self, **extra):
        self.home.mkdir(parents=True, exist_ok=True)
        state = {"version": 1, "mode": "goal", "active": [dict(CARD)], "scope": [], **extra}
        (self.home / "state.json").write_text(json.dumps(state))


class CollectTests(Base):
    def test_reads_only_its_own_profile(self):
        mine, other = self.root / "profile-a", self.root / "profile-b"
        for folder, text in ((mine, "prompt from profile a"), (other, "prompt from profile b")):
            folder.mkdir()
            (folder / "history.jsonl").write_text(history_row(text, 5) + "\n")
        env = dict(os.environ, CLAUDE_CONFIG_DIR=str(mine))
        env.pop("REMODEL_HOME", None)
        result = subprocess.run([sys.executable, str(SCRIPTS / "collect.py")], capture_output=True,
                                text=True, env=env, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        self.assertEqual(info["data"], str((mine / "remodel").resolve()))
        self.assertTrue(info["run"].startswith(str((mine / "remodel" / "runs").resolve())))
        digest = Path(info["digest"]).read_text()
        self.assertIn("prompt from profile a", digest)
        self.assertNotIn("prompt from profile b", digest)

    def test_digest_has_buckets_signals_and_masks_keys(self):
        profile = self.root / "profile"
        profile.mkdir()
        src = profile / "history.jsonl"
        src.write_text("\n".join([
            history_row("give me the query i can execute", 60 * 24 * 20),
            history_row("fix the printer alignment", 50),
            history_row("still not working, try again", 40),
            history_row("a", 30),
            history_row("use this key sk-abcdefghijklmnopqrstuvwxyz123456", 20),
            history_row("make price import self-serve for all customers", 10),
            history_row("/model", 5),
        ]) + "\n")
        out = self.root / "run"
        result = run("collect.py", "--out", str(out), home=self.home, profile=profile)
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        self.assertEqual(info["typed_prompts"], 6)
        digest = (out / "digest.md").read_text()
        self.assertIn("### Last 7 days", digest)
        self.assertIn("### 15-30 days ago", digest)
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz123456", digest)
        self.assertIn("| think-at-scale | model |", digest)
        signals = json.loads((out / "signals.json").read_text())
        self.assertEqual(signals["window"]["retries"], 1)
        self.assertEqual(signals["window"]["picks"], 1)
        self.assertGreaterEqual(signals["cards"]["think-at-scale"]["proof_unprompted"], 1)


    def test_taps_from_the_page_reach_the_digest(self):
        profile = self.root / "profile"
        profile.mkdir()
        (profile / "history.jsonl").write_text(history_row("hello there", 5) + "\n")
        out = self.root / "run"
        taps = out / "taps" / "answers"
        taps.mkdir(parents=True)
        (taps / "w__spot-0.json").write_text(json.dumps({"id": "w__spot-0", "version": 3, "data": {
            "week": "2026-10-31", "kind": "spot", "item": "w__spot-0", "label": "Fix it for this one",
            "value": "partly", "note": "only for one store"}}))
        result = run("collect.py", "--out", str(out), home=self.home, profile=profile)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["taps"], 1)
        digest = (out / "digest.md").read_text()
        self.assertIn("spot · Fix it for this one → partly · note: only for one store", digest)


    def test_since_last_run_shows_what_did_not_change(self):
        profile = self.root / "profile"
        profile.mkdir()
        (profile / "history.jsonl").write_text("\n".join([
            history_row("old prompt before the run", 120),
            history_row("give me the query i can execute again", 10)]) + "\n")
        prev = self.root / "prev-run"
        prev.mkdir()
        (prev / "report.json").write_text(json.dumps({
            "mode": "goal", "verdict": "Hand fixes again.",
            "spotted": [{"id": "hand-fix", "old": "Fix it for this one", "new": "Fix the rule", "card": "think-at-scale"}],
            "moves": ["Write the rule"],
            "apply": [{"title": "Install the Remodel hooks", "where": str(profile / "settings.json"), "prompt": "x"}]}))
        yesterday = time.time() - 86400
        day = time.strftime("%Y-%m-%d", time.localtime(yesterday))
        first = time.strftime("%Y-%m-%d", time.localtime(time.time() - 8 * 86400))
        self.home.mkdir(parents=True)
        (self.home / "state.json").write_text(json.dumps({
            "history": [{"date": day, "at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(yesterday)),
                         "run": str(prev), "mode": "goal"}],
            "patterns": {"hand-fix": {"id": "hand-fix", "first_seen": first, "dates": [first, day]}}}))
        out = self.root / "run"
        result = run("collect.py", "--out", str(out), home=self.home, profile=profile)
        self.assertEqual(result.returncode, 0, result.stderr)
        digest = (out / "digest.md").read_text()
        self.assertIn("## Since the last run", digest)
        self.assertIn(f"[hand-fix] Fix it for this one → Fix the rule · first flagged {first} · runs 2", digest)
        self.assertIn("trigger hits since: 1", digest)
        self.assertIn("give me the query i can execute again", digest)
        self.assertIn("move-0: Write the rule · tap: no tap", digest)
        self.assertIn("Install the Remodel hooks · on disk: hooks not installed", digest)

    def test_since_last_run_reads_problems(self):
        profile = self.root / "profile"
        profile.mkdir()
        (profile / "history.jsonl").write_text(history_row("give me the query i can execute again", 10) + "\n")
        prev = self.root / "prev-run"
        prev.mkdir()
        (prev / "report.json").write_text(json.dumps({
            "mode": "normal", "verdict": "Hand fixes again.",
            "problems": [{"id": "hand-fix", "title": "You fix rows by hand", "status": "repeating", "old": "Fix this one",
                          "new": "Fix the import", "deadline": {"when": "Mon 2 Nov", "done": "one real order"},
                          "card": {"id": "think-at-scale", "status": "installing"},
                          "questions": [{"id": "cost", "text": "What does one customer cost?"}]}],
            "insights": {"do_first": [{"when": "Today", "text": "Paste the hooks prompt"}]},
            "setup": [{"title": "Install the Remodel hooks", "where": str(profile / "settings.json"), "prompt": "x"}]}))
        yesterday = time.localtime(time.time() - 86400)
        self.home.mkdir(parents=True)
        day = time.strftime("%Y-%m-%d", yesterday)
        (self.home / "state.json").write_text(json.dumps({"history": [
            {"date": day, "at": time.strftime("%Y-%m-%dT%H:%M:%S", yesterday), "run": str(prev), "mode": "normal"}]}))
        (self.home / "taps").mkdir()
        out = self.root / "run"
        (out / "taps" / "answers").mkdir(parents=True)
        (out / "taps" / "answers" / "a.json").write_text(json.dumps(
            {"item": f"{day}__problem-hand-fix", "value": "true", "kind": "problem", "label": "x", "week": day}))
        result = run("collect.py", "--out", str(out), home=self.home, profile=profile)
        self.assertEqual(result.returncode, 0, result.stderr)
        digest = (out / "digest.md").read_text()
        self.assertIn("[hand-fix] You fix rows by hand · Fix this one → Fix the import · was repeating", digest)
        self.assertIn("tap: true · deadline Mon 2 Nov: one real order · card think-at-scale trigger hits since: 1", digest)
        self.assertIn("question: What does one customer cost? · answer: no tap", digest)
        self.assertIn("- Today: Paste the hooks prompt", digest)
        self.assertIn("Install the Remodel hooks · on disk: hooks not installed", digest)

    def test_same_day_reruns_are_ignored(self):
        profile = self.root / "profile"
        profile.mkdir()
        (profile / "history.jsonl").write_text(history_row("a prompt", 5) + "\n")
        runs = {}
        for name, verdict in (("earlier-day", "Verdict from an earlier day."), ("today", "Verdict from this morning.")):
            runs[name] = self.root / name
            runs[name].mkdir()
            (runs[name] / "report.json").write_text(json.dumps({"mode": "goal", "verdict": verdict}))
        yesterday = time.localtime(time.time() - 86400)
        self.home.mkdir(parents=True)
        (self.home / "state.json").write_text(json.dumps({"history": [
            {"date": time.strftime("%Y-%m-%d", yesterday), "at": time.strftime("%Y-%m-%dT%H:%M:%S", yesterday),
             "run": str(runs["earlier-day"]), "mode": "goal"},
            {"date": time.strftime("%Y-%m-%d"), "at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 600)),
             "run": str(runs["today"]), "mode": "goal"}]}))
        out = self.root / "run"
        result = run("collect.py", "--out", str(out), home=self.home, profile=profile)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["same_day_reruns_ignored"], 1)
        digest = (out / "digest.md").read_text()
        self.assertIn("Same-day reruns ignored: 1 earlier run(s) today", digest)
        self.assertIn("last verdict: Verdict from an earlier day.", digest)
        self.assertNotIn("Verdict from this morning.", digest)

    def test_thin_window_widens_until_the_sample_is_big_enough(self):
        profile = self.root / "profile"
        profile.mkdir()
        rows = [history_row("recent prompt", 60)] + [history_row(f"older prompt {i}", 60 * 24 * 45 + i) for i in range(70)]
        (profile / "history.jsonl").write_text("\n".join(rows) + "\n")
        out = self.root / "run"
        result = run("collect.py", "--out", str(out), home=self.home, profile=profile)
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        self.assertEqual((info["window_days"], info["widened_from"]), (60, 30))
        digest = (out / "digest.md").read_text()
        self.assertIn("Window widened from 30 to 60 days: only 1 typed prompts in the last 30 days", digest)
        self.assertIn("older prompt 3", digest)

    def test_chosen_time_frame_limits_the_sessions(self):
        profile = self.root / "profile"
        profile.mkdir()
        day = 60 * 24
        (profile / "history.jsonl").write_text("\n".join([
            history_row("too old for the frame", 20 * day), history_row("inside the frame", 10 * day),
            history_row("after the frame", 2 * day)]) + "\n")
        start = time.strftime("%Y-%m-%d", time.localtime(time.time() - 15 * 86400))
        end = time.strftime("%Y-%m-%d", time.localtime(time.time() - 5 * 86400))
        out = self.root / "run"
        result = run("collect.py", "--out", str(out), "--from", start, "--to", end, home=self.home, profile=profile)
        self.assertEqual(result.returncode, 0, result.stderr)
        window = json.loads(result.stdout)["window"]
        self.assertEqual((window["from"], window["to"], window["chosen"], window["typed_prompts"]), (start, end, True, 1))
        digest = (out / "digest.md").read_text()
        self.assertIn(f"Window: {start} to {end} (11 days, chosen by the user)", digest)
        self.assertIn("inside the frame", digest)
        self.assertNotIn("after the frame", digest)
        self.assertNotIn("too old for the frame", digest.split("## Prompts")[1])
        bad = run("collect.py", "--out", str(out), "--from", end, "--to", start, home=self.home, profile=profile)
        self.assertNotEqual(bad.returncode, 0)

    def test_full_window_is_not_widened(self):
        profile = self.root / "profile"
        profile.mkdir()
        (profile / "history.jsonl").write_text("\n".join(history_row(f"p{i}", 60 + i) for i in range(5)) + "\n")
        result = run("collect.py", "--out", str(self.root / "run"), "--min-prompts", "5", home=self.home, profile=profile)
        info = json.loads(result.stdout)
        self.assertEqual((info["window_days"], info["widened_from"]), (30, None))

    def test_persona_lens_by_name_or_typo(self):
        profile = self.root / "profile"
        profile.mkdir()
        (profile / "history.jsonl").write_text(history_row("polish the settings screen again", 30) + "\n")
        self.write_persona()
        self.write_persona(PERSONA.replace("id: zed", "id: yan").replace("Zed Example", "Yan Other")
                           .replace("zed-ship-it", "yan-card"), "yan.md")
        for query in ("zed example", "Zedd"):
            out = self.root / f"run-{query}"
            result = run("collect.py", "--out", str(out), "--persona", query, home=self.home, profile=profile)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["persona"]["id"], "zed")
            digest = (out / "digest.md").read_text()
            self.assertIn("## Persona lens: Zed Example (zed)", digest)
            self.assertIn("| zed-ship-it | process | Ship the smallest piece | 1 / 1 |", digest)
            self.assertNotIn("yan-card", digest)

    def test_unknown_persona_lists_the_choices(self):
        profile = self.root / "profile"
        profile.mkdir()
        self.write_persona()
        result = run("collect.py", "--out", str(self.root / "run"), "--persona", "nobody", home=self.home, profile=profile)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown persona", result.stderr)
        self.assertIn("zed (Zed Example)", result.stderr)


class HookTests(Base):
    def prompt(self, text, session="s1", cwd="/Users/x/Documents/personal/Acme/projects"):
        payload = json.dumps({"prompt": text, "session_id": session, "cwd": cwd, "hook_event_name": "UserPromptSubmit"})
        result = run("hook.py", "prompt", home=self.home, stdin=payload)
        self.assertEqual(result.returncode, 0)
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def test_no_state_means_silence(self):
        self.assertEqual(self.prompt("give me the query i can execute"), {})

    def test_fires_once_per_session_then_cautions(self):
        self.write_state()
        first = self.prompt("give me the query i can execute")
        self.assertIn("Think at scale", first["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(first["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        second = self.prompt("another sql please")
        self.assertNotIn("hookSpecificOutput", second)
        third = self.prompt("sql again", session="s2")
        self.assertIn("hookSpecificOutput", third)
        self.assertIn("3 times today", third["systemMessage"])

    def test_unrelated_prompt_is_ignored(self):
        self.write_state()
        self.assertEqual(self.prompt("rename this variable"), {})

    def test_scope_limits_folders(self):
        self.write_state(scope=["Acme"])
        self.assertEqual(self.prompt("give me the query i can execute", cwd="/Users/x/work/other"), {})
        self.assertIn("hookSpecificOutput", self.prompt("give me the query i can execute"))

    def test_session_start_lists_cards(self):
        self.write_state()
        payload = json.dumps({"cwd": "/tmp", "session_id": "s9", "source": "startup"})
        out = json.loads(run("hook.py", "session", home=self.home, stdin=payload).stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("Think at scale", out["systemMessage"])

    def test_each_profile_practises_only_its_own_cards(self):
        mine, other = self.root / "profile-a", self.root / "profile-b"
        (mine / "remodel").mkdir(parents=True)
        other.mkdir()
        (mine / "remodel" / "state.json").write_text(json.dumps({"active": [dict(CARD)], "scope": []}))
        payload = json.dumps({"prompt": "give me the query i can execute", "session_id": "s1", "cwd": "/tmp"})
        for profile, expect in ((mine, True), (other, False)):
            env = dict(os.environ, CLAUDE_CONFIG_DIR=str(profile))
            env.pop("REMODEL_HOME", None)
            out = subprocess.run([sys.executable, str(SCRIPTS / "hook.py"), "prompt"], input=payload,
                                 capture_output=True, text=True, env=env, timeout=30).stdout
            self.assertEqual("hookSpecificOutput" in out, expect, profile)

    def test_bad_input_never_blocks(self):
        self.write_state()
        result = run("hook.py", "prompt", home=self.home, stdin="not json")
        self.assertEqual(result.returncode, 0)


class RenderTests(Base):
    def problem(self, pid="hand-fix", **extra):
        p = {"id": pid, "tab": "Hand fixes", "title": "You fix each customer by hand", "status": "repeating",
             "status_note": "4 times in 30 days", "type": "model", "call": "Four hand fixes this month.",
             "evidence": {"summary": "4 SQL fixes", "prompts": [{"ts": "10-30 09:40", "quote": "give me the query"}]},
             "old": "Fix it for this one", "new": "Fix the rule for everyone",
             "steps": [{"name": "What is wrong?", "text": "Write the check."}, {"name": "Why", "text": "Find the rule."},
                       {"name": "Proof", "text": "Run the check."}],
             "deadline": {"when": "Mon 2 Nov", "done": "One real order is right."},
             "questions": [{"id": "price", "text": "What would you charge?", "options": ["$99", "$199"]}],
             "card": {"id": "think-at-scale", "status": "new", "uses": 0, "title": "Think at $50B scale"}}
        p.update(extra)
        return p

    def report(self, **extra):
        report = {"mode": "goal", "goal": "Build a big company", "scope": ["Acme"],
                  "window": {"from": "2026-10-02", "to": "2026-10-31", "days": 30, "chosen": False, "typed_prompts": 29},
                  "verdict": "You fixed things by hand all week.",
                  "facts": [{"value": "4", "label": "hand fixes"}],
                  "insights": {"process": [{"when": "Before you fix", "rule": "find the rule", "problem": "hand-fix"}],
                               "do_first": [{"when": "Today", "text": "Install the hooks"}],
                               "calls": ["Own the back office"],
                               "models": [{"problem": "hand-fix", "old": "Patch rows.", "new": "Fix the rule once."}]},
                  "problems": [self.problem()],
                  "setup": [{"title": "Install hooks", "status": "Not done", "where": "/x/settings.json", "prompt": "Apply this."}],
                  "queue": ["seller-first"]}
        report.update(extra)
        path = self.root / "report.json"
        path.write_text(json.dumps(report))
        return path

    def render(self, path, *args):
        out = self.root / "reports"
        result = run("render.py", str(path), "--out-dir", str(out), *args, home=self.home)
        html = (out / "page.html").read_text() if result.returncode == 0 else ""
        return result, html

    def test_renders_the_page_and_updates_ledger(self):
        result, html = self.render(self.report())
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("You fixed things by hand all week.", "Sessions analysed: 2 Oct – 31 Oct 2026 · 29 prompts",
                     "Goal: Build a big company", "Actionable insights", "Change what you believe",
                     "Change the order you work in", "Do first", "What the goal demands", "Own the back office",
                     "You fix each customer by hand", "Repeating · 4 times in 30 days", "Fix the rule for everyone",
                     "Next time, do this", "Deadline: Mon 2 Nov.", "Setup, one minute each",
                     'data-target="setup-0"', "30 Oct 09:40", "<s>Patch rows.</s> <b>Fix the rule once.</b>",
                     "Card: think at $50B scale"):
            self.assertIn(text, html)
        self.assertNotIn("<!doctype", html.lower())
        nav = html[html.index('<nav class="tabs"'):html.index("</nav>")]
        self.assertEqual(re.findall(r'data-target="([^"]+)"', nav), ["insights", "p-hand-fix", "setup"])
        self.assertIn(">1. Hand fixes<", nav)
        self.assertLess(html.index("<h1>"), html.index('<nav class="tabs"'))
        today = time.strftime("%Y-%m-%d")
        for item in (f"{today}__problem-hand-fix", f"{today}__q-price"):
            self.assertIn(f'data-id="{item}"', html)
        state = json.loads((self.home / "state.json").read_text())
        self.assertEqual(state["active"][0]["id"], "think-at-scale")
        self.assertEqual(state["active"][0]["problem"], "hand-fix")
        self.assertEqual(state["scope"], ["Acme"])
        self.assertEqual(state["history"][-1]["window"]["to"], "2026-10-31")
        self.assertEqual(state["patterns"]["hand-fix"]["new"], "Fix the rule for everyone")

    def test_still_problem_offers_still_true(self):
        result, html = self.render(self.report(problems=[self.problem(status="still", status_note="asked last run")]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Still · asked last run", html)
        self.assertIn(">Still true<", html)

    def test_rejects_an_incomplete_problem(self):
        broken = self.problem()
        for key in ("new", "deadline", "steps"):
            broken.pop(key)
        result = run("render.py", str(self.report(problems=[broken])), home=self.home)
        self.assertEqual(result.returncode, 2)
        for text in ("missing new", "steps needs 3-7 steps", "deadline needs when and done"):
            self.assertIn(text, result.stderr)

    def test_rejects_without_the_window(self):
        result = run("render.py", str(self.report(window="last 30 days")), home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("window must be collect.py's window object", result.stderr)

    def test_rejects_too_many_active_cards(self):
        cards = ["think-at-scale", "seller-first", "outcome-first"]
        items = [self.problem(f"p{i}", card={"id": c, "status": "new"}, questions=[]) for i, c in enumerate(cards)]
        result = run("render.py", str(self.report(problems=items,
                                                  insights={"process": [{"when": "a", "rule": "b", "problem": "p0"}],
                                                            "do_first": [{"when": "a", "text": "b"}]})), home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("at most 2", result.stderr)

    def test_rejects_too_many_questions(self):
        qs = [{"id": f"q{i}", "text": "?"} for i in range(4)]
        result = run("render.py", str(self.report(problems=[self.problem(questions=qs)])), home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("at most 3 questions", result.stderr)

    def test_rejects_unknown_card(self):
        result = run("render.py", str(self.report(problems=[self.problem(card={"id": "nope", "status": "new"})])),
                     home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("no card file", result.stderr)

    def test_set_url_is_remembered(self):
        result = run("render.py", "--set-url", "https://claude.ai/artifact/abc", home=self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.home / "state.json").read_text())["artifact_url"], "https://claude.ai/artifact/abc")

    def persona_problem(self, **extra):
        p = self.problem(steps=[{"name": "Cut", "text": "Drop the polish."}, {"name": "Ship", "text": "Ship tonight."},
                                {"name": "Learn", "text": "Ask one customer."}],
                         quote={"text": 'His rule: "a shipped draft beats a perfect plan".', "source": "Zed, 2020"},
                         card={"id": "zed-ship-it", "status": "queued"})
        p.update(extra)
        return p

    def test_persona_report_in_the_persona_voice(self):
        self.write_persona()
        result, html = self.render(self.report(persona={"id": "zed"}, problems=[self.persona_problem()]))
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("Lens: Zed Example", "Example&#x27;s three steps, applied", "His rule: &quot;a shipped draft",
                     "<cite>Zed, 2020</cite>", "next in line", "Only text in quotation marks is Example's own"):
            self.assertIn(text, html)
        self.assertNotIn("Every section below is read through", html)
        state = json.loads((self.home / "state.json").read_text())
        self.assertEqual(state["persona"], "zed")
        self.assertEqual(state["queue"][0], "zed-ship-it")

    def test_persona_steps_must_follow_the_voice(self):
        self.write_persona()
        result = run("render.py", str(self.report(persona={"id": "zed"}, problems=[
            self.persona_problem(steps=[{"name": "Plan", "text": "a"}, {"name": "Build", "text": "b"},
                                        {"name": "Test", "text": "c"}])])), home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("must follow the persona's steps in order: Cut | Ship | Learn", result.stderr)

    def test_rejects_an_invented_quote(self):
        self.write_persona()
        fake = self.persona_problem(quote={"text": '"move fast and polish nothing"', "source": "Zed"})
        result = run("render.py", str(self.report(persona={"id": "zed"}, problems=[fake])), home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not in the persona file", result.stderr)
        paraphrase = self.persona_problem(quote={"text": "Ship before it feels ready.", "source": "Zed"})
        result, html = self.render(self.report(persona={"id": "zed"}, problems=[paraphrase]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Zed (in Remodel's words)", html)

    def test_persona_needs_its_card(self):
        self.write_persona()
        result = run("render.py", str(self.report(persona={"id": "zed"}, problems=[
            self.persona_problem(card={"id": "think-at-scale", "status": "new"})])), home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("should be a zed card", result.stderr)

    def test_same_day_rerun_rebuilds_from_the_day_start_ledger(self):
        first = self.report(problems=[self.problem("first-try")],
                            insights={"process": [{"when": "a", "rule": "b", "problem": "first-try"}],
                                      "do_first": [{"when": "a", "text": "b"}]})
        self.assertEqual(run("render.py", str(first), home=self.home).returncode, 0)
        run("render.py", "--set-url", "https://claude.ai/artifact/abc", home=self.home)
        second = self.report(mode="normal", problems=[self.problem("second-try")],
                             insights={"process": [{"when": "a", "rule": "b", "problem": "second-try"}],
                                       "do_first": [{"when": "a", "text": "b"}]})
        result = run("render.py", str(second), home=self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads((self.home / "state.json").read_text())
        self.assertEqual([h["mode"] for h in state["history"]], ["normal"])
        self.assertEqual(list(state["patterns"]), ["second-try"])
        self.assertEqual(state["artifact_url"], "https://claude.ai/artifact/abc")
        self.assertTrue((self.home / "day-start.json").exists())


class PersonaLibraryTests(unittest.TestCase):
    SECTIONS = ("## In one minute", "## Mental models", "## Thinking process", "## More done at the same quality",
                "## Wins that came from the thinking", "## Failures and what they show", "## Don't copy",
                "## Applied to a founder", "## Bottleneck checks", "## Voice", "## Practice cards", "## Sources")

    def test_built_in_personas_are_complete(self):
        sys.path.insert(0, str(SCRIPTS))
        import common
        import re
        folder = SCRIPTS.parent / "references" / "personas"
        for pid in ("musk", "gates", "bezos", "buffett", "munger", "ambani"):
            with self.subTest(persona=pid):
                p = common.parse_persona(folder / f"{pid}.md")
                self.assertEqual(p["id"], pid)
                for key in ("name", "essence", "best_for", "watch_out"):
                    self.assertTrue(p.get(key), key)
                for section in self.SECTIONS:
                    self.assertIn(section, p["body"])
                self.assertTrue(2 <= len(p["cards"]) <= 3)
                self.assertTrue(4 <= len(p["voice"]["steps"]) <= 6, p["voice"])
                for key in ("tone", "deadlines"):
                    self.assertTrue(p["voice"].get(key), key)
                for card in p["cards"]:
                    self.assertTrue(card["id"].startswith(pid + "-"), card["id"])
                    self.assertIn(card.get("type"), ("model", "process"))
                    for key in ("title", "old", "when", "question", "agent_line"):
                        self.assertTrue(card.get(key), f"{card['id']}.{key}")
                    re.compile(card["trigger"])
                    re.compile(card["proof"])
                sources = p["body"][p["body"].index("## Sources"):]
                self.assertGreaterEqual(len(re.findall(r"(?m)^\s*(?:\d+\.\s*)?\[\d+\]", sources)), 12)

    def test_names_and_typos_find_the_persona(self):
        sys.path.insert(0, str(SCRIPTS))
        import common
        personas = common.read_personas()
        for query, pid in (("elon musk", "musk"), ("Bill Gates", "gates"), ("jeff", "bezos"), ("buffet", "buffett"),
                           ("charlie munger", "munger"), ("Mukesh Ambani", "ambani")):
            self.assertEqual(common.find_persona(query, personas), pid, query)
        self.assertIsNone(common.find_persona("someone else", personas))


if __name__ == "__main__":
    unittest.main()

# report.json

`render.py` validates this file, writes the page and updates the ledger. It exits 2 with a list of
what to fix. The page reads top to bottom in this order: the headline, up to three numbers, a sticky
tab row, **Actionable insights**, one block per **problem**, then **Setup**.

```json
{
  "mode": "normal",
  "goal": "Only in goal mode",
  "scope": ["Documents/personal"],
  "window": {"from": "2026-10-02", "to": "2026-10-31", "days": 30, "chosen": false, "typed_prompts": 287},
  "persona": {"id": "musk", "why": "Only with persona auto: why this persona"},
  "verdict": "You are hand-typing SQL to fix one menu price. Your product itself has no price. Stop.",
  "facts": [
    {"value": "5", "label": "catalogues loaded by SQL in 30 days"},
    {"value": "0", "label": "prompts about price or unit cost"}
  ],
  "insights": {
    "process": [
      {"when": "Before you build", "rule": "question the requirement, delete, simplify, then speed up. Automate last.", "problem": "hand-loading"}
    ],
    "do_first": [
      {"when": "Today", "text": "Paste the hooks prompt (Setup). One minute."},
      {"when": "Mon 2 Nov", "text": "Catalogue import live, proven on one real order."}
    ],
    "calls": ["Goal mode only: up to 3 strategic calls"]
  },
  "problems": [
    {
      "id": "hand-loading",
      "tab": "Hand-loading",
      "title": "The SQL step should not exist",
      "status": "repeating",
      "status_note": "5 times in 30 days",
      "type": "process",
      "call": "Five catalogue loads by hand for two customers. Each one costs you an evening...",
      "quote": {"text": "\"possibly the most common error of a smart engineer is to optimize the thing that should not exist\"",
                "source": "Elon Musk, Starbase tour, 2021"},
      "evidence": {"summary": "Store A on 4 and 8 Oct. Store B on 27 Oct and twice on 30 Oct.",
                   "prompts": [{"ts": "10-30 16:24", "quote": "give me the sql query which reflects so"}]},
      "old": "Fix this customer's rows, then ask the AI if it's right.",
      "new": "Delete the manual step. Build the import once. Prove it on a real order.",
      "steps": [
        {"name": "Question the requirement", "text": "Who said prices get loaded by hand? Nobody. It's a habit."},
        {"name": "Delete", "text": "No more hand SQL for catalogues, starting with the next batch."},
        {"name": "Simplify", "text": "One sheet format and one tax rule, decided once."},
        {"name": "Accelerate", "text": "The import is live before Store A's next batch."},
        {"name": "Automate", "text": "Only then does the import check tax on every upload by itself."}
      ],
      "deadline": {"when": "Monday 2 Nov", "done": "Done means one real order shows the right total."},
      "questions": [{"id": "unit-cost", "text": "What does one customer cost you per month?", "options": ["Under $5", "$5–20", "No idea"]}],
      "card": {"id": "proof-not-promise", "status": "installing", "uses": 0}
    }
  ],
  "setup": [
    {"title": "Install the Remodel hooks", "status": "Not done · offered in every report today",
     "where": "/Users/me/.claude/settings.json", "prompt": "Apply this Remodel correction. ..."}
  ],
  "queue": ["think-at-scale", "musk-cost-from-inputs"]
}
```

## Fields

| Field | Meaning |
|---|---|
| `mode`, `goal`, `scope` | As passed to the run. `scope` limits where the hooks fire. |
| `window` | collect.py's `window` object, copied as it is. The page shows "Sessions analysed: 2 Oct – 31 Oct 2026 · 287 prompts". |
| `persona` | Only with a persona lens. `why` only when it was picked with `auto`. |
| `verdict` | The headline: one to three short, blunt sentences naming the problems in order. In a persona lens, written in the persona's voice. |
| `facts` | Up to 3 numbers from the digest, ideally one per problem. |
| `insights.models` | Optional. Shorter old → new lines for the "Change what you believe" list (`problem`, `old`, `new`); without it the list uses each problem's own `old` → `new`. |
| `insights.process` | 1–3 rules for the order of work, each tied to the moment it applies (`when`: "Before you build") and to a `problem` id. |
| `insights.do_first` | 1–5 actions with a concrete `when` ("Today", "Mon 2 Nov"), in the order to do them. |
| `insights.calls` | Goal mode only: up to 3 strategic calls. |
| `problems` | 1–3 problems, the costliest first. Each one tells its whole story, so nothing about it appears anywhere else. |
| `problems[].id`, `tab` | Stable lowercase id (reuse it when the same problem returns, so its streak carries over) and a 1–3 word tab label. |
| `problems[].status` | `new`, `repeating` (seen several times this period) or `still` (flagged last run, not changed). `status_note` adds the count or what was asked. |
| `problems[].type` | `model` (a belief) or `process` (an order of steps). |
| `problems[].call` | The verdict on this problem: what it costs, in plain numbers, with no softening. |
| `problems[].quote` | Persona lens only. Words inside quotation marks must appear in the persona file exactly, or render.py rejects the report; anything else is shown as "(in Remodel's words)". `source` names who and where. |
| `problems[].evidence` | A one-line `summary` and dated `prompts` copied from the digest. |
| `problems[].old`, `new` | The thinking to replace, and its replacement. The insights' "Change what you believe" list is built from these. |
| `problems[].steps` | 3–7 steps for next time. With a persona, the step names must be the persona's Voice steps, in order. |
| `problems[].deadline` | `when` is a date; `done` says what proves it. |
| `problems[].questions` | Optional, at most 3 across the report. Tap options, never free text. |
| `problems[].card` | Optional: the card that practises this problem. `status`: `new`, `installing`, `installed` or `queued` (shown as next in line). At most 2 active; with a persona, one card should be the persona's. |
| `setup` | Up to 3 one-time changes to Claude's setup, each with a copy-ready `prompt`. `status` says whether it is done and how often it was offered. |
| `queue` | The next cards to activate. |

## How the page uses these fields

| Page part | From | Taps saved to `answers` |
|---|---|---|
| Top line | `mode`, `goal`, `persona`, `window` | none |
| Headline and numbers | `verdict`, `facts` | none |
| Actionable insights | each problem's `old` → `new`, `insights.process`, `insights.do_first`, `insights.calls` | none |
| Problem blocks | `problems` | "Is this you?": That's me · Partly · Not really (Still true · Fixed now · Not a problem for `still`), and each question's options |
| Setup | `setup` | Copy prompt button |

Tap ids: `<date>__problem-<id>` and `<date>__q-<question id>`.

## Ready-made setup

Use the absolute path of the skill folder (`${CLAUDE_SKILL_DIR}`) and this run's profile folder
(the `profile` value collect.py prints). The hook finds the profile's ledger by itself through
`$CLAUDE_CONFIG_DIR`, so the same command works in every profile.

**Install the Remodel hooks**, where: `<config dir>/settings.json`, merged into any existing `hooks`:

```json
{
  "hooks": {
    "SessionStart": [
      {"matcher": "startup|resume|clear|compact",
       "hooks": [{"type": "command", "command": "python3 <skill dir>/scripts/hook.py session", "timeout": 10}]}
    ],
    "UserPromptSubmit": [
      {"hooks": [{"type": "command", "command": "python3 <skill dir>/scripts/hook.py prompt", "timeout": 10}]}
    ]
  }
}
```

Done when: a new session in a scoped folder shows "Remodel · practising: …", and a prompt with a
trigger word makes Claude ask the card's question.

**Run Remodel every Sunday**, where: `~/Library/LaunchAgents/com.remodel.weekly.<profile name without the dot>.plist`
(for a profile at `~/.claude-work` that is `com.remodel.weekly.claude-work.plist`; the label matches the file name).
It runs `claude -p` at 20:00 on Sundays, then `launchctl load` registers it:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.remodel.weekly.<profile name></string>
  <key>ProgramArguments</key><array>
    <string>/bin/zsh</string><string>-lc</string>
    <string>cd ~ &amp;&amp; CLAUDE_CONFIG_DIR="<profile>" <claude binary> -p "/remodel goal" --allowedTools "Bash(python3 <skill dir>/scripts/*),Bash(open *),Read,Write" --permission-mode acceptEdits --max-turns 40 &gt;&gt; <profile>/remodel/weekly.log 2&gt;&amp;1</string>
  </array>
  <key>StartCalendarInterval</key><dict>
    <key>Weekday</key><integer>0</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer>
  </dict>
</dict></plist>
```

Use `/remodel` instead of `/remodel goal` when the ledger's mode is `normal`. Use the absolute path
of `claude` (`command -v claude` in a normal terminal), because launchd does not load the shell
PATH. Done when `launchctl list | grep com.remodel.weekly` shows the job.

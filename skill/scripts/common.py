"""Shared paths, card parsing and state I/O for the Remodel scripts (stdlib only)."""
import copy
import difflib
import json
import os
import re
from pathlib import Path

HOME = Path.home()


def _profile():
    """The Claude Code profile this run belongs to: $CLAUDE_CONFIG_DIR, else ~/.claude."""
    env = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(env).expanduser().resolve() if env else (HOME / ".claude").resolve()


# Remodel is isolated per profile: it reads only this profile's history and keeps its ledger,
# runs, cards and page link inside this profile, so separate profiles never see each other.
PROFILE = _profile()
HISTORY = PROFILE / "history.jsonl"
DATA = Path(os.environ.get("REMODEL_HOME") or PROFILE / "remodel")
SKILL_DIR = Path(__file__).resolve().parent.parent
BUILTIN_CARDS = SKILL_DIR / "references" / "cards"
CUSTOM_CARDS = DATA / "cards"
BUILTIN_PERSONAS = SKILL_DIR / "references" / "personas"
CUSTOM_PERSONAS = DATA / "personas"
STATE = DATA / "state.json"
DAY_START = DATA / "day-start.json"
NUDGES = DATA / "nudges.jsonl"
CONFIG_DIRS = [PROFILE]


def parse_meta(block):
    """Flat `key: value` lines. Quoted values are kept verbatim; unquoted ones drop a trailing # comment."""
    meta = {}
    for line in block.strip().splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        else:
            value = re.sub(r"\s+#.*$", "", value)
        meta[key.strip()] = value
    return meta


def parse_card(path):
    """Read a card file: flat `key: value` frontmatter plus a markdown body."""
    text = Path(path).read_text()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    meta = parse_meta(text[3:end])
    if not meta.get("id"):
        return None
    meta["body"] = text[end + 4:].strip()
    meta["path"] = str(path)
    return meta


def parse_persona(path):
    """Read a persona file: frontmatter, plus the yaml card blocks under "## Practice cards"."""
    meta = parse_card(path)
    if not meta:
        return None
    body = meta["body"]
    start = body.find("## Practice cards")
    section = body[start:body.find("\n## ", start + 1) if body.find("\n## ", start + 1) != -1 else None] if start != -1 else ""
    voice = body[body.find("## Voice"):] if "## Voice" in body else ""
    voice = voice[:voice.find("\n## ", 1)] if voice.find("\n## ", 1) != -1 else voice
    meta["voice"] = {k.strip().lower(): v.strip() for k, v in re.findall(r"^- \*\*(.+?):\*\*\s*(.+)$", voice, re.M)}
    meta["voice"]["steps"] = [x.strip() for x in meta["voice"].get("steps", "").split("|") if x.strip()]
    meta["cards"] = []
    for block in re.findall(r"```ya?ml\n(.*?)```", section, re.S):
        card = parse_meta(block)
        if card.get("id") and card.get("question"):
            card.update({"persona": meta["id"], "path": str(path)})
            meta["cards"].append(card)
    return meta


def read_personas():
    """Built-in personas, overridden by the user's own persona files with the same id."""
    personas = {}
    for folder in (BUILTIN_PERSONAS, CUSTOM_PERSONAS):
        if folder.is_dir():
            for path in sorted(folder.glob("*.md")):
                persona = parse_persona(path)
                if persona:
                    personas[persona["id"]] = persona
    return personas


def find_persona(query, personas=None):
    """Match "musk", "Elon Musk" or a typo like "buffet" to a persona id; None when nothing is close."""
    personas = read_personas() if personas is None else personas
    words = re.findall(r"[a-z]+", str(query).lower())
    names = {}
    for pid, p in personas.items():
        for word in [pid] + re.findall(r"[a-z]+", p.get("name", "").lower()):
            names.setdefault(word, set()).add(pid)
    hits = set()
    for word in words:
        close = difflib.get_close_matches(word, names, n=1, cutoff=0.8)
        if close:
            hits |= names[close[0]]
    return hits.pop() if len(hits) == 1 else None


def read_cards():
    """Built-in cards and persona cards, overridden by the user's custom cards with the same id."""
    cards = {}
    for persona in read_personas().values():
        for card in persona["cards"]:
            cards[card["id"]] = card
    for folder in (BUILTIN_CARDS, CUSTOM_CARDS):
        if folder.is_dir():
            for path in sorted(folder.glob("*.md")):
                card = parse_card(path)
                if card:
                    cards[card["id"]] = card
    return cards


def load_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


SCHEDULE_PLIST = HOME / "Library" / "LaunchAgents" / f"com.remodel.weekly.{PROFILE.name.lstrip('.')}.plist"


def applied_lines():
    """User-level CLAUDE.md lines a past correction added (they carry a `Remodel:` marker)."""
    found = []
    for folder in CONFIG_DIRS:
        path = folder / "CLAUDE.md"
        try:
            lines = path.read_text().splitlines()
        except OSError:
            continue
        found += [f"{path}: {line.strip()}" for line in lines if "Remodel:" in line]
    return found


def hooks_installed():
    """Settings files that already register the Remodel hook."""
    found = []
    for folder in CONFIG_DIRS:
        settings = folder / "settings.json"
        try:
            text = settings.read_text()
        except OSError:
            continue
        if "remodel" in text and "hook.py" in text:
            found.append(str(settings))
    return found


def runs_today(state, today):
    return [h for h in (state or {}).get("history", []) if h.get("date") == today]


def day_start(state, today):
    """The ledger as it stood before today's first run, so a rerun on the same day is analysed as
    if the earlier runs that day never happened. Without a snapshot (runs from before this existed),
    drop today's history entries and pattern dates instead."""
    if not state:
        return state
    snap = load_json(DAY_START)
    if isinstance(snap, dict) and snap.get("date") == today and isinstance(snap.get("state"), dict):
        base = copy.deepcopy(snap["state"])
    else:
        base = copy.deepcopy(state)
        base["history"] = [h for h in base.get("history", []) if h.get("date", "") < today]
        patterns = {}
        for pid, p in (base.get("patterns") or {}).items():
            dates = [d for d in p.get("dates", []) if d < today]
            if dates:
                patterns[pid] = dict(p, dates=dates, last_seen=dates[-1])
        base["patterns"] = patterns
    if state.get("artifact_url"):  # where the page lives is not part of the analysis
        base["artifact_url"] = state["artifact_url"]
    return base


def text_of(item):
    """Moves and calls are plain strings, or {"text", "lens"} when a persona shaped them."""
    return str(item.get("text") or "") if isinstance(item, dict) else str(item or "")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:40] or "item"


def merge_patterns(patterns, report, today):
    """Pattern ledger: each spotted habit keeps a stable id, when it was first flagged and on which dates."""
    merged = {k: dict(v, dates=list(v.get("dates", []))) for k, v in (patterns or {}).items()}
    persona = report.get("persona") or {}
    found = [(i.get("id") or slug(i.get("old")), i.get("old"), i.get("new"), i.get("type"))
             for i in report.get("spotted", [])]
    found += [(g.get("id") or f"{persona.get('id')}-{slug(g.get('bottleneck'))}", g.get("bottleneck"), g.get("they"),
               f"persona:{persona.get('id')}") for g in persona.get("gaps", [])]
    found += [(p.get("id") or slug(p.get("old")), p.get("old"), p.get("new"), p.get("type") or "problem")
              for p in report.get("problems", [])]
    for pid, old, new, kind in found:
        entry = merged.setdefault(pid, {"id": pid, "first_seen": today, "dates": []})
        entry.update({"old": old, "new": new, "type": kind, "last_seen": today})
        if today not in entry["dates"]:
            entry["dates"].append(today)
    for item in report.get("still", []):
        if item.get("kind") == "pattern" and item.get("id") in merged:
            entry = merged[item["id"]]
            entry["last_seen"] = today
            if today not in entry["dates"]:
                entry["dates"].append(today)
    return merged

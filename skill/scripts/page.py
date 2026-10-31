"""Build the Remodel report as a Claude artifact page (no doctype: the Artifact tool wraps it).

The page reads top to bottom: the headline, up to three numbers, a sticky tab row, the actionable
insights, one block per problem, then setup. Every tap ("is this you?", questions) is saved to the
artifact's `answers` collection through the `db` capability, so the next /remodel run can read it
back with ArtifactData. Copy buttons put setup prompts on the clipboard.
"""
import datetime as dt
import html
import re

from common import slug

STATUS = {"new": "New", "repeating": "Repeating", "still": "Still"}
NUMBERS = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
# Quoted segments in a persona quote: straight or curly double quotes.
QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")


def e(text):
    return html.escape(str(text or ""), quote=True)


def stamp(ts):
    """'10-08 23:28' → '8 Oct 23:28'; anything else is shown as given."""
    try:
        return dt.datetime.strptime(f"2000-{ts}", "%Y-%m-%d %H:%M").strftime("%-d %b %H:%M")
    except (TypeError, ValueError):
        return str(ts or "")


def tap(item_id, kind, label, options):
    chips = "".join(f'<button type="button" class="chip" data-v="{e(v)}" aria-pressed="false" disabled>{e(t)}</button>'
                    for v, t in options)
    return (f'<div class="tapbar" data-id="{e(item_id)}" data-kind="{e(kind)}" data-label="{e(label)}">'
            f'<div class="chips">{chips}<span class="saved" aria-live="polite"></span></div></div>')


def lower_first(text):
    text = str(text or "")
    return text[:1].lower() + text[1:] if text[1:2].islower() else text


def window_text(win):
    if isinstance(win, dict) and win.get("from") and win.get("to"):
        a, b = dt.date.fromisoformat(win["from"]), dt.date.fromisoformat(win["to"])
        span = f"{a:%-d %b}" + ("" if a.year == b.year else f" {a.year}") + f" – {b:%-d %b %Y}"
        count = f" · {win['typed_prompts']} prompts" if win.get("typed_prompts") else ""
        return f"Sessions analysed: {span}{count}"
    return str(win or "")


def problem_html(n, p, week, cards, pr, steps_label):
    status = p.get("status", "new")
    pill = STATUS.get(status, status.title()) + (f" · {p['status_note']}" if p.get("status_note") else "")
    quote = ""
    q = p.get("quote") or {}
    if pr and q.get("text"):
        own = "" if QUOTED.search(q["text"]) else " (in Remodel's words)"
        quote = f'<p class="quote">{e(q["text"])}<cite>{e(q.get("source"))}{own}</cite></p>'
    ev = p.get("evidence") or {}
    prompts = "".join(f'<div><span class="ts">{e(stamp(x.get("ts")))}</span>{e(x.get("quote"))}</div>'
                      for x in ev.get("prompts", [])[:5])
    steps = "".join(
        f'<li><span><b>{e(s.get("name"))}{"" if str(s.get("name", "")).rstrip()[-1:] in ".?!" else "."}</b>'
        f'{e(s.get("text"))}</span></li>' for s in p.get("steps", []))
    dl = p.get("deadline") or {}
    questions = ""
    if p.get("questions"):
        rows = "".join(f'<p class="q">{e(qq.get("text"))}</p>'
                       + tap(f"{week}__q-{slug(qq.get('id'))}", "question", qq.get("text"),
                             [(slug(o), o) for o in qq.get("options", [])])
                       for qq in p["questions"])
        questions = f'<div class="block"><span class="label">Answer now</span>{rows}</div>'
    card = ""
    c = p.get("card") or {}
    if c.get("id") in cards:
        d = cards[c["id"]]
        use = ("next in line" if c.get("status") == "queued" else "learned" if c.get("status") == "installed"
               else f"used {int(c.get('uses') or 0)} of 3 times")
        card = (f'<div class="block"><span class="label">Claude will ask you</span>'
                f'<p class="ask">{e(c.get("question") or d.get("question"))}</p>'
                f'<p class="meta">Card: {e(lower_first(c.get("title") or d.get("title")))} · {use}</p></div>')
    options = ([("true", "Still true"), ("fixed", "Fixed now"), ("drop", "Not a problem")] if status == "still"
               else [("yes", "That's me"), ("partly", "Partly"), ("no", "Not really")])
    return (f'<section class="thread" id="p-{e(slug(p.get("id")))}">'
            f'<div><div class="eyebrow"><span>Problem {n}</span><span class="status {e(status)}">{e(pill)}</span></div>'
            f'<h2>{e(p.get("title"))}</h2></div>'
            f'<p class="call">{e(p.get("call"))}</p>{quote}'
            f'<div class="block"><span class="label">Evidence</span><p>{e(ev.get("summary"))}</p>'
            + (f'<details><summary>Show your prompts</summary><div class="log">{prompts}</div></details>' if prompts else "")
            + '</div>'
            f'<div class="block"><span class="label">Change the thinking</span><div class="swap">'
            f'<p><span>Old</span><s>{e(p.get("old"))}</s></p><p><span>New</span><b class="new">{e(p.get("new"))}</b></p></div></div>'
            f'<div class="block"><span class="label">{e(steps_label)}</span><ol class="steps">{steps}</ol></div>'
            f'<p class="deadline"><b>Deadline: {e(dl.get("when"))}.</b> {e(dl.get("done"))}</p>'
            f'{questions}{card}'
            f'<div class="block"><span class="label">Is this you?</span>'
            + tap(f"{week}__problem-{slug(p.get('id'))}", "problem", p.get("title"), options)
            + '</div></section>\n<hr>\n')


def build(report, cards, today, patterns=None, personas=None):
    week = today
    pr = report.get("persona")
    pinfo = (personas or {}).get((pr or {}).get("id"), {})
    pname = pinfo.get("name") or (pr or {}).get("id") or ""
    short = pname.split()[-1] if pname else ""
    problems = report.get("problems", [])
    nsteps = max((len(p.get("steps", [])) for p in problems), default=0)
    steps_label = f"{short}'s {NUMBERS.get(nsteps, nsteps)} steps, applied" if pr and short else "Next time, do this"

    left = ["<b>Remodel</b>"]
    if report.get("mode") == "goal":
        left.append(f"Goal: {e(report['goal'])}" if report.get("goal") else "Goal mode")
    if pr:
        left.append(f"Lens: {e(pname)}")
    facts = "".join(f'<div class="fact"><b>{e(f.get("value"))}</b><span>{e(f.get("label"))}</span></div>'
                    for f in report.get("facts", [])[:3])

    ins = report.get("insights") or {}
    # Beliefs to change: each problem's old → new, or the shorter lines in insights.models when given.
    beliefs = ins.get("models") or [{"problem": p.get("id"), "old": p.get("old"), "new": p.get("new")} for p in problems]
    models = "".join(f'<li><a href="#p-{e(slug(m.get("problem")))}" data-jump="p-{e(slug(m.get("problem")))}">'
                     f'<s>{e(m.get("old"))}</s> <b>{e(m.get("new"))}</b></a></li>' for m in beliefs)
    process = "".join(f'<li><a href="#p-{e(slug(x.get("problem")))}" data-jump="p-{e(slug(x.get("problem")))}">'
                      f'<b>{e(x.get("when"))}:</b> {e(x.get("rule"))}</a></li>' for x in ins.get("process", []))
    calls = ""
    if ins.get("calls"):
        calls = ('<div class="ins"><h3>What the goal demands</h3><ol class="ins-list">'
                 + "".join(f"<li>{e(x)}</li>" for x in ins["calls"][:3]) + "</ol></div>")
    do_first = "".join(f'<li><span class="when">{e(x.get("when"))}</span>{e(x.get("text"))}</li>'
                       for x in ins.get("do_first", []))
    insights = ('<section class="insights" id="insights"><h2>Actionable insights</h2><div class="ins-grid">'
                f'<div class="ins"><h3>Change what you believe</h3><p class="ins-sub">Mental models</p><ol class="ins-list">{models}</ol></div>'
                f'<div class="ins"><h3>Change the order you work in</h3><p class="ins-sub">Thinking process</p><ol class="ins-list">{process}</ol></div>'
                f'</div>{calls}'
                + (f'<div class="ins do-first"><h3>Do first</h3><ol class="ins-list">{do_first}</ol></div>' if do_first else "")
                + '</section>\n<hr>\n')

    blocks = "".join(problem_html(i, p, week, cards, pr, steps_label) for i, p in enumerate(problems, 1))

    fixes = "".join(
        f'<div class="fix"><div><h3>{e(f.get("title"))}</h3><p>{e(f.get("status") or "Not done")}</p></div>'
        f'<button type="button" class="btn copy" data-target="setup-{i}">Copy prompt</button>'
        f'<details><summary>See the prompt</summary><pre id="setup-{i}">{e(f.get("prompt"))}</pre></details></div>'
        for i, f in enumerate(report.get("setup", [])))
    setup = f'<section class="setup" id="setup"><h2>Setup, one minute each</h2>{fixes}</section>' if fixes else ""

    tabs = [("insights", "Actionable insights")]
    tabs += [(f"p-{slug(p.get('id'))}", f"{i}. {p.get('tab') or p.get('title')}") for i, p in enumerate(problems, 1)]
    if fixes:
        tabs.append(("setup", "Setup"))
    nav = "".join(f'<a class="tab" href="#{e(t)}" data-target="{e(t)}">{e(label)}</a>' for t, label in tabs)
    sourced = (f"<p>Only text in quotation marks is {e(short)}'s own, with its source. "
               f"The rest is Remodel applying {e(short)}'s habits to your prompts.</p>") if pr else ""

    return f"""<title>Remodel</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400&display=swap">
<style>{CSS}</style>
<main class="wrap" data-week="{e(week)}">
<div class="top"><span>{" · ".join(left)}</span><span>{e(window_text(report.get("window")))}</span></div>
<h1>{e(report.get("verdict"))}</h1>
{f'<div class="facts">{facts}</div>' if facts else ""}
<nav class="tabs" aria-label="Sections">{nav}</nav>
{insights}{blocks}{setup}
<footer>{sourced}<p id="status">Connecting so your answers can be saved…</p></footer>
</main>
<script>{JS}</script>
"""


CSS = """
/* Layout: a calm reading column (about 68 characters), sentence case throughout, one quiet accent, labels above content. Follows the viewer's light or dark theme. */
:root{
  --bg:#F5F6F8;--surface:#FFFFFF;--ink:#1F2328;--soft:#3D444D;--muted:#5F6873;--line:#E2E5E9;
  --accent:#2F5BB7;--accent-soft:#EAF0FB;--warn:#A4531A;--warn-soft:#FBF0E7;--ok:#1C7A55;--log:#F1F3F5;
  --f-body:"Atkinson Hyperlegible","Segoe UI",system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#16191D;--surface:#1D2126;--ink:#E7E9EC;--soft:#C9CED4;--muted:#A0A8B2;--line:#2D3238;
  --accent:#8EB1F3;--accent-soft:#1E2A3D;--warn:#E9A46F;--warn-soft:#2D2219;--ok:#6CCB9E;--log:#22272D;color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#16191D;--surface:#1D2126;--ink:#E7E9EC;--soft:#C9CED4;--muted:#A0A8B2;--line:#2D3238;
  --accent:#8EB1F3;--accent-soft:#1E2A3D;--warn:#E9A46F;--warn-soft:#2D2219;--ok:#6CCB9E;--log:#22272D;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:17px;line-height:1.65}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
.wrap{max-width:720px;margin:0 auto;padding-block:28px 64px;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:flex;flex-direction:column;gap:40px}
h1,h2,h3{margin:0;line-height:1.3;text-wrap:balance;font-weight:700}
p{margin:0}
.top{display:flex;justify-content:space-between;gap:8px 16px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
.top b{color:var(--ink)}
h1{font-size:clamp(24px,3.6vw,30px)}
.top+h1{margin-top:-24px}
.facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:-16px}
.fact{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;min-width:0}
.fact b{font-size:26px;line-height:1.2;font-variant-numeric:tabular-nums}
.fact span{font-size:14px;color:var(--muted);line-height:1.4}
.tabs{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;border-bottom:1px solid var(--line);margin-top:-16px}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;font-size:15px;font-weight:700;color:var(--muted);text-decoration:none;padding:12px 10px 10px;border-bottom:3px solid transparent;white-space:nowrap}
.tab:hover{color:var(--ink)}
.tab[aria-current="true"]{color:var(--ink);border-bottom-color:var(--accent)}
section{scroll-margin-top:calc(env(safe-area-inset-top,0px) + 64px)}
/* actionable insights */
.insights{display:flex;flex-direction:column;gap:16px}
.insights h2,.setup h2{font-size:24px}
.ins-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.ins{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:6px;min-width:0}
.ins h3{font-size:18px}
.ins-sub{font-size:14px;color:var(--muted);margin-top:-4px}
.ins-list{margin:4px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:10px}
.ins-list a{color:inherit;text-decoration:none}
.ins-list a:hover b{text-decoration:underline}
.ins-list s{display:block;font-size:15px}
.ins-list b{color:var(--ok)}
.ins-grid .ins:last-child .ins-list b{color:var(--ink)}
.do-first{background:var(--accent-soft);border-color:transparent}
.do-first .ins-list{padding-left:0;list-style:none}
.do-first li{display:grid;grid-template-columns:96px minmax(0,1fr);gap:10px}
.when{font-weight:700;color:var(--accent)}
/* a problem, read top to bottom */
.thread{display:flex;flex-direction:column;gap:22px}
.eyebrow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:14px;color:var(--muted)}
.status{font-size:13px;font-weight:700;color:var(--warn);background:var(--warn-soft);border-radius:999px;padding:2px 10px}
.status.new{color:var(--accent);background:var(--accent-soft)}
.thread h2{font-size:24px;margin-top:6px}
.call{font-size:18px;color:var(--soft)}
.quote{border-left:3px solid var(--line);padding-left:14px;color:var(--soft)}
.quote cite{display:block;font-style:normal;font-size:14px;color:var(--muted);margin-top:4px}
.block{display:flex;flex-direction:column;gap:8px}
.label{font-size:14px;font-weight:700;color:var(--muted)}
.swap{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:6px}
.swap p span{display:inline-block;min-width:44px;font-size:14px;font-weight:700;color:var(--muted)}
s{text-decoration-color:var(--warn);color:var(--muted)}
.new{font-weight:700;color:var(--ok)}
.steps{margin:0;padding:0;list-style:none;counter-reset:st;display:flex;flex-direction:column;gap:12px}
.steps li{counter-increment:st;display:grid;grid-template-columns:28px minmax(0,1fr);gap:10px}
.steps li::before{content:counter(st);width:26px;height:26px;border-radius:50%;background:var(--accent-soft);color:var(--accent);font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center;margin-top:2px}
.steps b{margin-right:6px}
.deadline{background:var(--accent-soft);border-radius:12px;padding:12px 16px}
.deadline b{color:var(--accent)}
.ask{font-size:19px;font-weight:700}
.meta{font-size:14px;color:var(--muted)}
details summary{cursor:pointer;font-size:15px;color:var(--accent);width:fit-content}
details[open] summary{margin-bottom:8px}
.log{background:var(--log);border-radius:10px;padding:10px 12px;font:13.5px/1.6 var(--f-mono);white-space:pre-wrap;word-break:break-word;display:flex;flex-direction:column;gap:6px;color:var(--soft)}
.ts{color:var(--muted);margin-right:8px}
.chips{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.chip{font:700 15px var(--f-body);border-radius:999px;padding:7px 14px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.chip:not(:disabled):hover{border-color:var(--muted)}
.chip:disabled{cursor:default;opacity:.55}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--bg);opacity:1}
.saved{font-size:13px;color:var(--ok)}
.q{font-weight:700}
.tapbar+.q{margin-top:6px}
hr{border:0;border-top:1px solid var(--line);margin:0}
/* setup */
.setup{display:flex;flex-direction:column;gap:14px}
.fix{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 12px;align-items:center}
.fix h3{font-size:17px}
.fix p{font-size:14px;color:var(--muted)}
.fix details{grid-column:1/-1}
pre{margin:0;background:var(--log);border-radius:10px;padding:10px 12px;font:12.5px/1.6 var(--f-mono);white-space:pre-wrap;word-break:break-word;max-height:260px;overflow:auto;color:var(--soft)}
.btn{font:700 15px var(--f-body);border-radius:10px;padding:8px 14px;border:0;background:var(--ink);color:var(--bg);cursor:pointer;white-space:nowrap}
footer{font-size:14px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px;display:flex;flex-direction:column;gap:4px}
.tab:focus-visible,.chip:focus-visible,.btn:focus-visible,summary:focus-visible,.ins-list a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:600px){.facts,.ins-grid{grid-template-columns:minmax(0,1fr)}.fix{grid-template-columns:minmax(0,1fr)}.do-first li{grid-template-columns:minmax(0,1fr);gap:0}}
@media print{.tabs,.chips,.btn,#status{display:none}body{font-size:12pt}pre{max-height:none}}
"""

JS = """
(function () {
  var nav = document.querySelector(".tabs");
  if (!nav) return;
  var tabs = Array.prototype.slice.call(nav.querySelectorAll(".tab"));
  var targets = tabs.map(function (t) { return document.getElementById(t.dataset.target); });
  function jump(id, ev) {
    var el = document.getElementById(id);
    if (!el) return;
    ev.preventDefault();
    el.scrollIntoView({ block: "start" });
  }
  tabs.forEach(function (t) { t.addEventListener("click", function (ev) { jump(t.dataset.target, ev); }); });
  document.querySelectorAll("[data-jump]").forEach(function (a) {
    a.addEventListener("click", function (ev) { jump(a.dataset.jump, ev); });
  });
  var current = -2, queued = false;
  function mark() {
    queued = false;
    var line = nav.getBoundingClientRect().bottom + 24, active = -1;
    targets.forEach(function (el, i) { if (el && el.getBoundingClientRect().top <= line) active = i; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) active = targets.length - 1;
    if (active === current) return;
    current = active;
    tabs.forEach(function (t, i) { t.setAttribute("aria-current", i === active ? "true" : "false"); });
    var tab = tabs[Math.max(active, 0)];
    if (tab.offsetLeft < nav.scrollLeft || tab.offsetLeft + tab.offsetWidth > nav.scrollLeft + nav.clientWidth) {
      nav.scrollLeft = tab.offsetLeft - 12;
    }
  }
  window.addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(mark); } }, { passive: true });
  window.addEventListener("resize", mark);
  mark();
})();
(function () {
  var root = document.querySelector("main[data-week]");
  var WEEK = root.getAttribute("data-week");
  var bars = Array.prototype.slice.call(document.querySelectorAll(".tapbar"));
  var statusEl = document.getElementById("status");
  var db = null, answers = {}, busy = {};

  function setStatus(text) { statusEl.textContent = text; }
  function summary() {
    var n = bars.filter(function (b) { return !answers[b.dataset.id]; }).length;
    setStatus(n ? n + " quick answers left. Remodel reads them on the next run." : "All answered. Remodel reads them on the next run.");
  }
  function paint() {
    bars.forEach(function (bar) {
      var a = answers[bar.dataset.id];
      bar.querySelectorAll(".chip").forEach(function (c) {
        c.setAttribute("aria-pressed", a && a.value === c.dataset.v ? "true" : "false");
      });
    });
    if (db) summary();
  }
  function flash(bar, text) {
    var s = bar.querySelector(".saved");
    s.textContent = text;
    setTimeout(function () { if (s.textContent === text) s.textContent = ""; }, 2000);
  }
  function save(bar, value) {
    if (!db) return;
    var id = bar.dataset.id;
    var doc = { week: WEEK, kind: bar.dataset.kind, item: id, label: bar.dataset.label, value: value, note: "",
      at: new Date().toISOString() };
    if (value) answers[id] = doc; else delete answers[id];
    paint();
    var ref = db.collection("answers").doc(id);
    busy[id] = (busy[id] || Promise.resolve()).then(function () {
      return value ? ref.set(doc) : ref.delete();
    }).then(function () { flash(bar, "Saved"); }, function (err) {
      flash(bar, err && err.code === "invalid_argument" ? "This view is read-only" : "Not saved. Try again.");
    });
  }
  bars.forEach(function (bar) {
    bar.querySelectorAll(".chip").forEach(function (c) {
      c.addEventListener("click", function () {
        var a = answers[bar.dataset.id];
        save(bar, a && a.value === c.dataset.v ? "" : c.dataset.v);
      });
    });
  });
  document.querySelectorAll(".copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var pre = document.getElementById(btn.dataset.target), label = btn.textContent;
      function done() { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = label; }, 1800); }
      function fallback() {
        var d = pre.closest("details"); if (d) d.open = true;
        var range = document.createRange(); range.selectNodeContents(pre);
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
        btn.textContent = "Selected. Press Cmd+C";
        setTimeout(function () { btn.textContent = label; }, 3000);
      }
      try { navigator.clipboard.writeText(pre.textContent).then(done, fallback); } catch (err) { fallback(); }
    });
  });
  function offline(text) { setStatus(text); }
  if (!window.claude || !window.claude.use) { offline("Open this page on claude.ai to save your answers."); return; }
  var timer = setTimeout(function () { offline("Saved answers can't be reached yet. Taps will save once the page connects."); }, 10000);
  window.claude.use("db").then(function (d) {
    if (!d) { clearTimeout(timer); offline("Answers can't be saved in this view. Open the page on claude.ai."); return; }
    db = d;
    document.querySelectorAll(".chip").forEach(function (el) { el.disabled = false; });
    summary();
    db.collection("answers").where("week", "==", WEEK).onSnapshot(function (snap) {
      if (!snap.metadata.fromCache) clearTimeout(timer);
      var next = {};
      snap.docs.forEach(function (doc) { if (doc.exists) next[doc.id] = doc.data(); });
      answers = next;
      paint();
    }, function () { clearTimeout(timer); offline("Saved answers stopped updating. Reload the page to reconnect."); });
  });
})();
"""

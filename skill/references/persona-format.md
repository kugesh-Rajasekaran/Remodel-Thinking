# Writing a persona

A persona lets Remodel compare the user's thinking with one thinker and say, concretely, where the
user's bottleneck is and what to change to get more done at the same quality. Built-in personas
live in `references/personas/`. Custom personas go in `<profile>/remodel/personas/<id>.md`; a
custom persona with a built-in persona's `id` replaces it.

A good persona is researched, not remembered: their own letters, books, talks and long interviews
first, then reputable biographies and journalism. Failures get as much space as wins, because the
failures are where the thinking shows. Every decision, number or date carries a source number;
quotes are verbatim or left out.

```markdown
---
id: bezos
name: Jeff Bezos
essence: Start from the customer and work backwards, for the long term
best_for: deciding what to build and which bets to make
watch_out: the one trait not to copy, in one line
---

# Jeff Bezos: Start from the customer and work backwards

## In one minute
3-4 bullets: what they built, and the one or two thinking habits that made it.

## Mental models (what they believe)
5-7 models, most distinctive first. Each:
### <Model, written as an instruction>
- **Belief:** one sentence.
- **Real decision:** what they did, year, outcome [n].
- **Ask yourself:** one question.
- **In a founder's prompts:** what a prompt sounds like with this model / without it.

## Thinking process (the order of their steps)
A numbered loop of 4-7 steps for a big decision, each with a real example [n].

## More done at the same quality
3-5 concrete practices with evidence [n].

## Wins that came from the thinking
| Decision | Year | Thinking used | Outcome |

## Failures and what they show
| Failure | Year | What went wrong in the thinking | What changed after |

## Public image vs how they actually decide
2-4 bullets.

## Don't copy
2-3 traits that hurt, or that don't transfer to a small team.

## Applied to a founder
4-6 one-line calls: "<Name> would ..." in the user's world.

## Bottleneck checks
| Bottleneck in your thinking | You see it when your prompts... | <Name>'s fix (one question) |
6-8 rows. Remodel compares the user's digest with this table, so the middle column must be
observable in prompts to a coding agent: what the user asks for, how they frame a task, what they
never ask.

## Voice
- **Tone:** how this persona delivers bad news, in one line. Blunt about the habit, never the person.
- **Steps:** 4-6 short step names, separated by `|`, in the order the persona runs a decision.
- **Deadlines:** the persona's deadline style.
- **Lands like:** one example verdict in that tone (not a quote).

## Practice cards
2-3 cards, each a fenced yaml block in card format (see card-format.md); ids start with `<id>-`.

## Sources
`[n] Title, author/outlet, year, URL`. At least 12.
```

How Remodel uses each part:

| Part | Used for |
|---|---|
| Frontmatter | `essence` and `best_for` help `persona auto` choose; `watch_out` is what a report must never recommend. |
| Mental models, Thinking process, More done at the same quality | What the persona would do about each problem. |
| Bottleneck checks | The comparison itself: each row with evidence in the digest can become a problem. |
| Voice | The report's tone, the step names every problem must follow (render.py checks), and the deadline style. |
| Everything quoted in the file | The only words a report may put in quotation marks; render.py rejects any other quote. |
| Practice cards | Activated like any card (hooks ask its question); their signals appear in the digest when the persona is the lens. |

Check a new persona with `python3 scripts/collect.py --persona <id>`: the digest's persona section
should list its cards, and the card table should show their trigger and proof hits.

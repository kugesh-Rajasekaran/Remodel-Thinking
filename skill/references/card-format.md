# Writing a card

A card is one better habit of thought, written so a hook can spot its moment and Claude can
practise it with the user. Built-in cards live in `references/cards/`. Custom cards go in
`<profile>/remodel/cards/<id>.md` (each Claude Code profile keeps its own); a custom card with a built-in card's `id` replaces it.

```markdown
---
id: think-at-scale
type: model
title: Think at scale
old: Fix it for this one customer
when: you ask for a one-off fix, data patch or manual step for a single customer
question: Does this work for 100,000 customers without me in the loop?
trigger: '(?i)\b(sql|query i can (run|execute)|for this customer|by hand)\b'
proof: '(?i)\b(all customers|every customer|self-?serve|bulk import|without me)\b'
agent_line: Do the requested fix, then name in one line the version that works for every customer without the user, and offer it.
caution_after: 3
tags: goal, business, scale
---
## Spot it
What the old thinking looks like in the history, concretely.

## Proof it is installed
What the user says when they use the new thinking on their own.

## Why it matters
One or two sentences.
```

| Field | Meaning |
|---|---|
| `id` | Lowercase, hyphenated, unique. |
| `type` | `model` changes what the user believes; `process` changes the order of steps they take. |
| `title` | The new habit, as an instruction. |
| `old` | The belief or habit it replaces, in the user's world. |
| `when` | The trigger in plain words, finishing "When…". |
| `question` | The one question that runs the new habit. The user should be able to ask it themselves. |
| `trigger` | Python regex the prompt hook matches against each prompt. Aim for the moment the old thinking starts. |
| `proof` | Python regex for prompts that look like the new thinking. It only finds candidates; Claude confirms them. |
| `agent_line` | What Claude does when the trigger matches. Keep it to one move. |
| `caution_after` | Optional. Shows the user a caution when the trigger fires this many times in one day. |

Regex tips:
- Start with `(?i)` for case-insensitive matching, and use `\b` word boundaries.
- Wrap the value in single quotes and keep apostrophes out of it; write `didn.?t` instead of `didn't`.
- Prefer phrases the user really types (from the digest) over generic words; a trigger that fires
  on everything turns the coach into noise.

After writing a card, rerun `collect.py`. The card's row in the digest's card-signals table shows
whether the trigger and proof patterns catch the right prompts.

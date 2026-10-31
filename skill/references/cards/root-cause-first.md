---
id: root-cause-first
type: process
title: Root cause before retry
old: Try it, look, tweak, try again
when: you ask for another attempt at the same problem
question: Stop. What is the root cause, and what one check would prove it?
trigger: '(?i)\b(still (not|isn.?t|doesn.?t|failing|broken)|not working|didn.?t work|same (issue|error|problem)|try again)\b'
proof: '(?i)\b(root cause|the cause is|because the|my hypothesis|i think it.?s caused|check whether|prove (it|that))\b'
agent_line: Name the most likely root cause and the one check that confirms it before changing anything else.
caution_after: 3
tags: general
---
## Spot it
Three or more rapid retries on one issue inside a session ("still not working", "again",
small visual nudges like "move it 2cm"), each followed by another blind change.

## Proof it is installed
The user opens with a hypothesis or a check ("I think it's X because Y, verify that first")
before asking for a change, without a nudge.

## Why it matters
Retry loops feel like progress but each attempt costs a full cycle. One root-cause check
usually replaces three to six attempts.

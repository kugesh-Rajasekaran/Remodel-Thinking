---
id: think-at-scale
type: model
title: Think at scale
old: Fix it for this one
when: you ask for a one-off fix, data patch or manual step for a single customer
question: Does this work for 100,000 customers without me in the loop?
trigger: '(?i)\b(sql|query i can (run|execute)|insert (into|the)|update the (price|record|row)s?|for this (merchant|customer|store|client)|(fix|update|add|do) (it|this|them) manually|by hand|one-?off)\b'
proof: '(?i)\b(all (merchants|customers|stores|users)|every (merchant|customer|store|user)|self-?serve|automat(e|ic|ion)|bulk import|without me|at scale|scalable)\b'
agent_line: Do the requested fix, then name in one line the version that works for every customer without the user, and offer it.
caution_after: 3
tags: goal, business, scale
---
## Spot it
The same manual fix, data load or support step repeated for single customers three or
more times in a month.

## Proof it is installed
The user asks for the general version (self-serve, import, automation, "for all
customers") without a nudge.

## Why it matters
Anything that needs the founder in the loop caps the company at the founder's hours.
The third repeat of a manual fix is a product.

# Rule phrasing

How to write rules in `plugins/*/rules.md` and in skills. The agent reads them
literally and on every session, so wording decides behaviour.

## Positive scope first

State what to do and where it applies before any exception. "Scratch work goes under
`<home>/tmp`" gives the agent a place to go; "don't use `/tmp`" leaves it guessing.

## Attach the why

Give the reason in the same rule, briefly. The agent applies a rule with a reason to
cases the wording didn't foresee, and a reviewer can tell when the reason no longer
holds.

## Glue negatives to their replacement

A prohibition comes with the thing to do instead, in the same sentence: "never reveal
token values -- mask them in command output". A bare negative names the forbidden
action and leaves the agent to improvise the alternative.

## Bare NEVER only for one-safe-path invariants

Use an unqualified NEVER only where every alternative is safe and the forbidden path
is not, such as deleting the arena's default branch. Elsewhere a hard NEVER blocks
legitimate edge cases and teaches the agent to treat all rules as negotiable.

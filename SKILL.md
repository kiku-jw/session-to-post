---
name: session-to-post
description: Turn a completed coding session, git diff, notes, or transcript into a development diary draft or end-of-session writeup without rewriting the story by hand. Use near the end of meaningful work when the user wants a durable wrap-up.
---

# Session to Post

## Metadata
- Trigger when: the session is winding down and there is real evidence such as a repo diff, saved patch, notes, or transcript.
- Do not use when: the work is still changing rapidly, the user only wants a mid-session checkpoint, or there is no real session evidence.

## Skill Purpose

Convert real session artifacts into a grounded wrap-up or post draft so the work, lessons, and pivots survive the session in a reusable form.

## Instructions
1. Decide whether the user wants a full post draft or only a short wrap-up note. Do not overuse the full draft path when a compact internal summary would do.
2. Choose the best source inputs and run the `session-to-post` CLI with explicit paths. Read `/Users/nick/.codex/skills/session-to-post/README.md` for the current flag set and source-selection rules if needed, especially when deciding between repo diff, saved patch, notes, and transcript inputs.
3. Review the generated result for groundedness, privacy, and signal. Keep the story anchored to decisions, failures, and pivots from the real session; if it is not public-safe, keep the output private-safe by default.

## Non-Negotiable Acceptance Criteria
- The draft stays anchored to real session evidence.
- Public-safe framing is the default unless the user explicitly asks for private internal notes.
- The output does not become a file-by-file tour when the real story is about decisions or lessons.
- The skill does not auto-run just because a session ended; the user still has to want a write-up.

## Output
- The draft text or saved draft path.
- The source artifacts used to build it.
- A note on whether the result is a public draft, a private note, or a short internal wrap-up.
- `Next skill options` (only if needed): `$public-artifact-lane` — turn the session draft into a public-facing artifact; `$ai-writing-detox` — remove synthetic tone before sharing; `$visual-explainer` — add a supporting HTML explainer if the story needs diagrams or structure.

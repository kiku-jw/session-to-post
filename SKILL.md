---
name: session-to-post
description: Turn a completed coding session, git diff, notes, or transcript into a development diary draft or end-of-session writeup without rewriting the story by hand.
---

# Session to Post

Use this skill near the end of meaningful coding work when the user wants a dev diary draft, build log, publishable post seed, or another durable writeup from real session artifacts.

Typical prompts:

- `turn this session into a post draft`
- `write a build diary from this diff`
- `make an end-of-session writeup from today's work`
- `use the transcript and notes to draft a post`
- `capture this coding session as a public-safe article`

## What to do

1. Decide if the user wants a full draft or only a short status note.
   - If a short wrap-up is enough, do not overuse this skill.
2. Choose the best source input.
   - Prefer `--repo` when the repo diff still matches the session.
   - Prefer `--diff` when the patch was already saved or curated.
   - Add `--session-notes` and `--transcript` only when they improve fidelity.
3. Run the CLI to generate the draft:

```bash
session-to-post \
  --repo /absolute/path/to/repo \
  --session-notes /absolute/path/to/notes.md \
  --transcript /absolute/path/to/session.jsonl \
  --out-dir /absolute/path/to/out
```

4. Review the result quickly for title, frontmatter, and whether the draft stays anchored to decisions, failures, and pivots.
5. If the user wants handoff into another system, use `--post-save-cmd`.

## When to read the README

Read `README.md` if you need:

- exact CLI flags
- source-selection guidance for `--repo` vs `--diff`
- publish-hook behavior

## Rules

- This skill improves invocation accuracy, but it does not auto-run just because a session ended.
- Prefer public-safe framing unless the user explicitly asks for private internal notes.
- Keep the story grounded in real work, not file-by-file tours.

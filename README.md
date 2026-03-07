# session-to-post

Turn a real coding session into a development diary draft without writing the whole post by hand.

This repo takes a git diff, session notes, or transcript, runs a writer + critic + editor pass, and saves one Markdown article you can drop into a blog or docs repo.

## Why this exists

Most developer blogs die in the same boring place: the work happened, the lessons were real, but nobody wants to spend another hour turning them into a post.

`session-to-post` is the small tool for that gap.

- input: real work
- output: one readable dev diary draft
- optional: run your own publish hook after save

The core product is the draft itself. Pushing to git or copying into a site should stay an adapter, not the whole point.

## What it does

- reads a git diff with optional session notes and transcript context
- normalizes raw transcripts or JSONL logs into a usable timeline
- writes a first draft in a candid dev-diary tone
- runs a critic pass before the final editor pass
- keeps the article anchored to decisions, failures, and pivots instead of file tours
- saves Markdown with frontmatter
- can trigger an optional post-save command

## Quick start

```bash
python3 -m pip install -e .
export OPENAI_API_KEY="your-key"
session-to-post \
  --diff examples/sample.diff \
  --session-notes examples/session-summary.md \
  --transcript examples/session-transcript.jsonl \
  --out-dir ./out
```

That command works from this repo as-is. It writes one Markdown draft to `./out` and prints a small JSON summary.

## Which input should I use?

Start with one code input, then add context only if it helps:

- `--repo` is the best first choice when the work still lives in a local git repo and `git diff HEAD~1` roughly matches the session you want to write about.
- `--diff` is better when you already saved a patch, want to trim the input, or the changes came from somewhere other than your current repo.
- `--session-notes` helps when the story is mostly about intent, tradeoffs, or why the plan changed.
- `--transcript` helps when the back-and-forth matters and you want the draft to keep the real timeline of pivots, questions, and dead ends.

Simple rule: choose `--repo` or `--diff` first. Add `--session-notes` and `--transcript` only when they make the draft more faithful.

## Real session example

```bash
session-to-post \
  --repo /path/to/project \
  --session-notes /path/to/session-summary.md \
  --transcript /path/to/session.jsonl \
  --out-dir ./out
```

## Inputs

The CLI accepts:

- one code input: `--repo`, `--diff`, or `--diff -` to read from stdin
- optional context: `--session-notes` and `--transcript`
- compatibility alias: `--chat-log` works like `--transcript`

## Output

The CLI writes one Markdown file and prints a small JSON result with:

- `articlePath`
- `title`
- `slug`
- `timelineUsed`

## Optional publish hook

If you want to hand the result to another system, pass `--post-save-cmd`.

Example:

```bash
session-to-post \
  --repo /path/to/project \
  --out-dir /path/to/content/blog \
  --post-save-cmd 'git -C /path/to/site add "$ARTICLE_PATH"'
```

Available environment variables inside the hook:

- `ARTICLE_PATH`
- `ARTICLE_TITLE`
- `ARTICLE_SLUG`

## What this repo is not

- not a full CMS
- not a scheduler
- not a GitHub Actions template
- not a Telegram bot

It is the content-generation step between real work and a first solid draft.

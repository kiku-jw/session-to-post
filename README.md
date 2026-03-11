# session-to-post

Codex skill and CLI for turning a real coding session into a development diary draft without writing the whole post by hand.

This repo takes a git diff, session notes, or transcript, runs a writer + critic + editor pass, and saves one Markdown article you can drop into a blog or docs repo.

As a skill, it improves natural-language invocation near the end of a session. It does not auto-run unless your Codex setup or automation tells it to.

## Explicit trigger pattern

This skill should fire when the user is clearly wrapping up and there is already real work to capture.

Good trigger phrases:

- `before we stop, summarize today's work`
- `wrap up this session`
- `save what we learned today`
- `turn this diff into a build diary`
- `make a post seed from this session`

Good evidence:

- current repo diff
- saved patch
- session notes
- transcript or JSONL log

It should not be the default for mid-session status checks or vague brainstorming.

## Why this exists

Most developer blogs die in the same boring place: the work happened, the lessons were real, but nobody wants to spend another hour turning them into a post.

`session-to-post` is the small tool for that gap.

- input: real work
- output: one readable dev diary draft
- optional: run your own publish hook after save

The core product is the draft itself. Pushing to git or copying into a site should stay an adapter, not the whole point.

## What it does

- reads a git diff or a saved session summary
- normalizes raw transcripts or JSONL logs into a usable timeline
- writes a first draft in a candid field-note tone: sharp, concrete, and a little suspicious of hype
- runs a critic pass before the final editor pass
- keeps the article anchored to decisions, failures, and pivots instead of file tours
- saves Markdown with frontmatter
- can trigger an optional post-save command

## Repository layout

- `SKILL.md` - Codex skill instructions for when and how to use the repo as a skill
- `agents/openai.yaml` - skill metadata for UI surfaces
- `src/dev_diary_pipeline/` - CLI and generation pipeline
- `examples/` - sample inputs

## Quick start

```bash
python3 -m pip install -e .
cp .env.example .env
export OPENAI_API_KEY="your-key"
python3 -m dev_diary_pipeline.cli \
  --repo /path/to/project \
  --session-notes examples/session-summary.md \
  --transcript examples/session-transcript.jsonl \
  --out-dir /path/to/content/blog
```

Or feed it a diff file:

```bash
python3 -m dev_diary_pipeline.cli \
  --diff examples/sample.diff \
  --out-dir ./out
```

## Inputs

You can use any mix of:

- `--repo` to read `git diff HEAD~1`
- `--diff` to read a saved diff file
- `--session-notes` for a short human summary
- `--chat-log` for useful context from the coding session
- `--transcript` for raw transcript text or JSONL session logs

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
python3 -m dev_diary_pipeline.cli \
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

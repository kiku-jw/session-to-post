# session-to-post

Turn a real coding session into a development diary draft without writing the whole post by hand.

This repo takes a git diff, session notes, or chat log, runs a writer + editor pass, and saves one Markdown article you can drop into a blog or docs repo.

## Why this exists

Most developer blogs die in the same boring place: the work happened, the lessons were real, but nobody wants to spend another hour turning them into a post.

`session-to-post` is the small tool for that gap.

- input: real work
- output: one readable dev diary draft
- optional: run your own publish hook after save

The core product is the draft itself. Pushing to git or copying into a site should stay an adapter, not the whole point.

## What it does

- reads a git diff or a saved session summary
- writes a first draft in a candid dev-diary tone
- runs an editor pass to cut filler and keep the text tied to the source
- saves Markdown with frontmatter
- can trigger an optional post-save command

## Quick start

```bash
python3 -m pip install -e .
cp .env.example .env
export OPENAI_API_KEY="your-key"
python3 -m dev_diary_pipeline.cli \
  --repo /path/to/project \
  --session-notes examples/session-summary.md \
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

## Output

The CLI writes one Markdown file and prints a small JSON result with:

- `articlePath`
- `title`
- `slug`

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

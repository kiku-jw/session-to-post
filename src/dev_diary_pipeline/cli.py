from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .core import (
    PipelineConfig,
    draft_article,
    extract_title,
    read_diff_from_repo,
    read_optional_text,
    run_post_save_cmd,
    save_article,
    slugify,
)


def load_source_text(args: argparse.Namespace) -> str:
    if args.diff == "-":
        return sys.stdin.read().strip()
    if args.diff:
        return Path(args.diff).read_text(encoding="utf-8").strip()
    if args.repo:
        return read_diff_from_repo(Path(args.repo))
    raise RuntimeError("Provide --diff, --diff -, or --repo.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a dev diary draft from a coding session.")
    parser.add_argument("--repo", help="Path to a git repo. Reads `git diff HEAD~1`.")
    parser.add_argument("--diff", help="Path to a diff file. Use `-` to read from stdin.")
    parser.add_argument("--session-notes", help="Optional Markdown notes from the session.")
    parser.add_argument("--chat-log", help="Optional chat log or transcript.")
    parser.add_argument("--out-dir", required=True, help="Directory where the draft Markdown file will be written.")
    parser.add_argument("--title", help="Override the generated article title.")
    parser.add_argument("--date", help="Override the article date (YYYY-MM-DD).")
    parser.add_argument("--tags", nargs="*", help="Optional frontmatter tags.")
    parser.add_argument("--post-save-cmd", help="Optional shell command to run after save.")
    args = parser.parse_args()

    source_text = load_source_text(args)
    if not source_text:
        raise SystemExit("Source material is empty.")

    config = PipelineConfig(
        api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
        api_base=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        model=os.environ.get("DEV_DIARY_MODEL", "gpt-5-mini").strip(),
    )
    if not config.api_key:
        raise SystemExit("OPENAI_API_KEY is required.")

    session_notes = read_optional_text(Path(args.session_notes)) if args.session_notes else ""
    chat_log = read_optional_text(Path(args.chat_log)) if args.chat_log else ""
    article_body = draft_article(config, source_text, session_notes, chat_log)
    target = save_article(
        article_body,
        Path(args.out_dir),
        title=args.title,
        article_date=args.date,
        tags=args.tags,
    )
    title = args.title or extract_title(article_body)
    slug = slugify(title)

    if args.post_save_cmd:
        run_post_save_cmd(args.post_save_cmd, target, title, slug)

    print(
        json.dumps(
            {
                "ok": True,
                "articlePath": str(target),
                "title": title,
                "slug": slug,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

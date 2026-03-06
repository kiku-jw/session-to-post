from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


@dataclass
class PipelineConfig:
    api_key: str
    api_base: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2200


def read_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def read_diff_from_repo(repo_path: Path) -> str:
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "--stat", "-p"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"git diff failed: {detail}")
    return result.stdout.strip()


def read_optional_text(path: Path | None) -> str:
    if path is None:
        return ""
    return path.read_text(encoding="utf-8").strip()


def extract_title(article_body: str) -> str:
    for line in article_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ").strip()
        if stripped:
            return stripped[:80]
    return "Untitled Dev Diary"


def slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = slug.strip("-")
    return slug[:60] or "untitled-dev-diary"


def llm_call(config: PipelineConfig, system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    request = urllib.request.Request(
        f"{config.api_base.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"chat completion failed: {detail}") from exc
    return data["choices"][0]["message"]["content"].strip()


def build_writer_prompt(source_text: str, session_notes: str, chat_log: str) -> str:
    parts = ["## Source Material", "", "```diff", source_text[:12000], "```"]
    if session_notes:
        parts.extend(["", "## Session Notes", "", session_notes[:4000]])
    if chat_log:
        parts.extend(["", "## Chat Log", "", chat_log[:4000]])
    return "\n".join(parts)


def build_editor_prompt(draft: str, source_text: str) -> str:
    return "\n".join(
        [
            "## Draft",
            "",
            draft,
            "",
            "## Source Material",
            "",
            "```diff",
            source_text[:10000],
            "```",
        ]
    )


def draft_article(config: PipelineConfig, source_text: str, session_notes: str, chat_log: str) -> str:
    writer_system = read_prompt("writer.md")
    editor_system = read_prompt("editor.md")
    writer_prompt = build_writer_prompt(source_text, session_notes, chat_log)
    first_pass = llm_call(config, writer_system, writer_prompt)
    editor_prompt = build_editor_prompt(first_pass, source_text)
    return llm_call(config, editor_system, editor_prompt)


def render_frontmatter(title: str, article_date: str, tags: list[str]) -> str:
    return "\n".join(
        [
            "---",
            f'title: "{title}"',
            f"date: {article_date}",
            'description: "Development diary draft generated from a real coding session."',
            f"tags: {json.dumps(tags, ensure_ascii=False)}",
            "---",
            "",
        ]
    )


def save_article(article_body: str, out_dir: Path, *, title: str | None = None, article_date: str | None = None, tags: list[str] | None = None) -> Path:
    resolved_title = title or extract_title(article_body)
    resolved_date = article_date or date.today().isoformat()
    resolved_tags = tags or ["dev-diary"]
    filename = f"{resolved_date}-{slugify(resolved_title)}.md"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / filename
    frontmatter = render_frontmatter(resolved_title, resolved_date, resolved_tags)
    target.write_text(frontmatter + article_body.strip() + "\n", encoding="utf-8")
    return target


def run_post_save_cmd(command: str, article_path: Path, title: str, slug: str) -> None:
    env = dict(os.environ)
    env["ARTICLE_PATH"] = str(article_path)
    env["ARTICLE_TITLE"] = title
    env["ARTICLE_SLUG"] = slug
    subprocess.run(command, shell=True, check=True, env=env)

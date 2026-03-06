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


def compact_text(text: str, *, limit: int = 240) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


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


def flatten_content(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts = [flatten_content(item) for item in value]
        return "\n".join(part for part in parts if part.strip())
    if isinstance(value, dict):
        if "text" in value:
            return flatten_content(value["text"])
        if "content" in value:
            return flatten_content(value["content"])
        if value.get("type") == "text":
            return flatten_content(value.get("text"))
        for key in ("message", "body", "prompt", "input", "output", "summary", "error"):
            if key in value:
                text = flatten_content(value[key])
                if text.strip():
                    return text
        parts = [flatten_content(item) for item in value.values()]
        return "\n".join(part for part in parts if part.strip())
    return str(value)


def transcript_label(record: dict[str, object]) -> str:
    if record.get("error") or record.get("is_error") is True:
        return "Failure"

    raw_role = str(
        record.get("role")
        or record.get("speaker")
        or record.get("author")
        or record.get("type")
        or record.get("event")
        or ""
    ).lower()
    if any(token in raw_role for token in ("user", "human")):
        return "User"
    if any(token in raw_role for token in ("assistant", "model", "ai")):
        return "Assistant"
    if any(token in raw_role for token in ("tool", "function", "call")):
        return "Tool"
    if any(token in raw_role for token in ("system", "context")):
        return "System"
    return "Event"


def extract_transcript_entry(record: dict[str, object]) -> str:
    text = flatten_content(
        record.get("content")
        or record.get("text")
        or record.get("message")
        or record.get("body")
        or record.get("prompt")
        or record.get("input")
        or record.get("output")
        or record.get("delta")
        or record.get("error")
    )
    if not text.strip():
        return ""
    return f"- {transcript_label(record)}: {compact_text(text)}"


def normalize_plain_chat_log(chat_log: str, *, max_entries: int = 18) -> str:
    entries: list[str] = []
    for line in chat_log.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        entries.append(f"- Event: {compact_text(stripped)}")
        if len(entries) >= max_entries:
            break
    return "\n".join(entries)


def normalize_chat_log(chat_log: str, *, max_entries: int = 18) -> str:
    raw = chat_log.strip()
    if not raw:
        return ""

    records: list[dict[str, object]] = []
    lines = [line for line in raw.splitlines() if line.strip()]
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            records = [item for item in parsed if isinstance(item, dict)]
    elif raw.startswith("{") and len(lines) == 1:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            records = [parsed]
    else:
        jsonl_records: list[dict[str, object]] = []
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                jsonl_records = []
                break
            if isinstance(record, dict):
                jsonl_records.append(record)
        records = jsonl_records

    if not records:
        return normalize_plain_chat_log(raw, max_entries=max_entries)

    entries: list[str] = []
    for record in records:
        entry = extract_transcript_entry(record)
        if not entry:
            continue
        entries.append(entry)
        if len(entries) >= max_entries:
            break
    if not entries:
        return normalize_plain_chat_log(raw, max_entries=max_entries)
    return "\n".join(entries)


def build_writer_prompt(source_text: str, session_notes: str, chat_log: str) -> str:
    parts = ["## Source Material", "", "```diff", source_text[:12000], "```"]
    if session_notes:
        parts.extend(["", "## Session Notes", "", session_notes[:4000]])
    if chat_log:
        parts.extend(["", "## Conversation Timeline", "", normalize_chat_log(chat_log)])
    return "\n".join(parts)


def build_critic_prompt(draft: str, source_text: str, chat_log: str) -> str:
    parts = [
        "## Draft",
        "",
        draft,
        "",
        "## Source Material",
        "",
        "```diff",
        source_text[:8000],
        "```",
    ]
    if chat_log:
        parts.extend(["", "## Conversation Timeline", "", normalize_chat_log(chat_log)])
    return "\n".join(parts)


def build_editor_prompt(draft: str, source_text: str, critic_notes: str, chat_log: str) -> str:
    return "\n".join(
        [
            "## Draft",
            "",
            draft,
            "",
            "## Critic Notes",
            "",
            critic_notes,
            "",
            "## Source Material",
            "",
            "```diff",
            source_text[:10000],
            "```",
            "",
            "## Conversation Timeline",
            "",
            normalize_chat_log(chat_log) if chat_log else "- Event: No transcript provided.",
        ]
    )


def draft_article(config: PipelineConfig, source_text: str, session_notes: str, chat_log: str) -> str:
    writer_system = read_prompt("writer.md")
    critic_system = read_prompt("critic.md")
    editor_system = read_prompt("editor.md")
    writer_prompt = build_writer_prompt(source_text, session_notes, chat_log)
    first_pass = llm_call(config, writer_system, writer_prompt)
    critic_prompt = build_critic_prompt(first_pass, source_text, chat_log)
    critic_notes = llm_call(config, critic_system, critic_prompt)
    editor_prompt = build_editor_prompt(first_pass, source_text, critic_notes, chat_log)
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

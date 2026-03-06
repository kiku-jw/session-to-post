from dev_diary_pipeline.core import build_editor_prompt, extract_title, normalize_chat_log, slugify


def test_slugify_keeps_it_short_and_clean() -> None:
    assert slugify("Why We Split the Publish Step From the Draft Generator") == "why-we-split-the-publish-step-from-the-draft-generator"


def test_extract_title_prefers_heading() -> None:
    body = "## What changed\n\nWe split the pipeline."
    assert extract_title(body) == "What changed"


def test_normalize_chat_log_from_jsonl() -> None:
    raw = "\n".join(
        [
            '{"role":"user","content":"Move blog publishing into GitHub."}',
            '{"role":"assistant","content":"I will switch the publish step and keep the site build."}',
            '{"role":"tool","content":"git push failed: auth missing"}',
            '{"type":"error","error":"remote rejected credentials"}',
        ]
    )
    timeline = normalize_chat_log(raw)
    assert "- User: Move blog publishing into GitHub." in timeline
    assert "- Assistant: I will switch the publish step and keep the site build." in timeline
    assert "- Tool: git push failed: auth missing" in timeline
    assert "- Failure: remote rejected credentials" in timeline


def test_build_editor_prompt_includes_critic_notes() -> None:
    prompt = build_editor_prompt(
        "# Draft\n\nToo vague.",
        "diff --git a/app.py b/app.py",
        "- Make the opening less generic.",
        '{"role":"user","content":"Make it clearer."}',
    )
    assert "## Critic Notes" in prompt
    assert "- Make the opening less generic." in prompt
    assert "## Conversation Timeline" in prompt

from dev_diary_pipeline.core import extract_title, slugify


def test_slugify_keeps_it_short_and_clean() -> None:
    assert slugify("Why We Split the Publish Step From the Draft Generator") == "why-we-split-the-publish-step-from-the-draft-generator"


def test_extract_title_prefers_heading() -> None:
    body = "## What changed\n\nWe split the pipeline."
    assert extract_title(body) == "What changed"

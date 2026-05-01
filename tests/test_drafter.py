"""Tests for customer-outreach drafter."""
from __future__ import annotations
import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from customer_outreach_agent.drafter import draft_email
from customer_outreach_agent.models import Lead, Project


def _lead(*, signal: str = "tweeted: tired of launch boards that disappear") -> Lead:
    return Lead(
        email="alice@example.com",
        signal_source="x.com/alice/status/123",
        signal_text=signal,
        name="Alice",
        handle="@alice",
    )


def _proj() -> Project:
    return Project(
        name="VibeXForge",
        one_liner="Forge AI projects into 16-bit pixel heroes that evolve.",
        differentiator="Real traction drives stage advancement (Seed→Myth)",
        free_offer="Free to forge first project — 30 seconds, no signup gate.",
        paid_tier="Hero Card skins from $3 (cosmetic only)",
        founder_name="Alex",
        founder_email="alex@vibexforge.com",
    )


def _fake_client(*, configured: bool = True,
                  subject: str = "Saw your launch-board tweet",
                  body: str = "Hey Alice — that exact frustration is what I built X for.",
                  err: str | None = None):
    c = MagicMock()
    c.configured = configured
    if err:
        c.messages_create_json.return_value = (None, err)
    else:
        c.messages_create_json.return_value = ({
            "subject": subject, "body": body,
        }, None)
    return c


def test_draft_unconfigured_uses_template():
    fake = _fake_client(configured=False)
    d = draft_email(_lead(), _proj(), client=fake)
    # Template open is "Saw this — \"<signal>\""
    assert "tired of launch boards" in d.body
    assert "Alice" in d.body
    assert d.lead_email == "alice@example.com"
    assert fake.messages_create_json.call_count == 0


def test_draft_uses_claude_subject_body():
    fake = _fake_client()
    d = draft_email(_lead(), _proj(), client=fake)
    assert d.subject == "Saw your launch-board tweet"
    assert "Alice" in d.body
    assert "X for" in d.body  # from fake body


def test_draft_anthropic_error_falls_back():
    fake = _fake_client(err="rate limit")
    d = draft_email(_lead(), _proj(), client=fake)
    # Template fallback contains the verbatim signal
    assert "tired of launch boards" in d.body
    assert "fell back" in d.raw_response


def test_draft_empty_subject_falls_back():
    fake = _fake_client(subject="", body="real body")
    d = draft_email(_lead(), _proj(), client=fake)
    # Should fall back since subject was empty
    assert "tired of launch boards" in d.body  # template signal


def test_draft_carries_lead_metadata():
    fake = _fake_client()
    d = draft_email(_lead(), _proj(), client=fake)
    assert d.lead_email == "alice@example.com"
    assert d.lead_name == "Alice"
    assert d.project_name == "VibeXForge"


def test_draft_template_no_name():
    """Lead without name → template uses 'Hey there' instead of 'Hey Alice'."""
    fake = _fake_client(configured=False)
    lead = Lead(email="x@y.com", signal_source="src",
                 signal_text="said something", name="")
    d = draft_email(lead, _proj(), client=fake)
    assert "there" in d.body

"""Drafter — produces one personalized email per (Lead, Project).

Different from vc-outreach by design:
  - The OPEN is the signal that triggered outreach (verbatim quote /
    observable fact). NOT a thesis hint.
  - The ASK is "try the product on us" — reversible, free / cheap.
  - Tone: indie-maker-to-indie-maker. NOT founder-to-investor.
  - 90 words max; subject ≤6 words.

Always returns a Draft (never None). Falls back to template if Claude
unavailable. Falls back to template if Claude returns empty subject/body.
"""
from __future__ import annotations
import pathlib
from datetime import datetime, timezone
from typing import Optional

from solo_founder_os.anthropic_client import (
    AnthropicClient,
    DEFAULT_HAIKU_MODEL,
)

from .models import Draft, Lead, Project


USAGE_LOG_PATH = (pathlib.Path.home()
                  / ".customer-outreach-agent" / "usage.jsonl")

DEFAULT_MODEL = DEFAULT_HAIKU_MODEL


SYSTEM_PROMPT = """You are an indie founder writing one personalized cold email \
to a potential customer (not an investor).

Rules — break any of these and the draft is rejected:

1. Open with ONE specific line that quotes or paraphrases the signal that \
made you reach out (their tweet, their post, their comment, etc). Use the \
`signal_text` field verbatim if it's short enough.

2. The product comes second, not first. Don't open with "I'm building X". \
Open with what THEY said.

3. The ASK is "try it free / cheap". Specific offer. NOT "would you take a \
meeting", NOT "happy to chat", NOT "would love to learn more".

4. 90 words max. Subject ≤6 words. No emoji. No exclamation marks. No \
"hope this email finds you well".

5. End with the link to try it. Then sign with first name only.

6. NEVER use these phrases: "circling back", "touching base", "quick \
question", "synergy", "leverage", "ecosystem", "game-changer", "AI-powered" \
(it's already AI; don't oversell), "transform", "revolutionize".

7. If the signal_text mentions a competitor, address it specifically — don't \
hide that you noticed.

Tone reference: someone you'd actually want to hear from, not a sales rep."""


DRAFT_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {
            "type": "string",
            "description": ("Email subject. ≤6 words, no emoji, no marketing "
                              "speak. Plain text."),
        },
        "body": {
            "type": "string",
            "description": ("Email body. ≤90 words. Use \\n for line breaks."),
        },
    },
    "required": ["subject", "body"],
    "additionalProperties": False,
}


def _build_user_prompt(lead: Lead, proj: Project) -> str:
    return f"""Lead:
  Name: {lead.name or '(unknown — start with "Hey")'}
  Email: {lead.email}
  Handle: {lead.handle or '(none)'}
  Signal source: {lead.signal_source}
  Signal text: {lead.signal_text}
  Notes: {lead.notes or '(none)'}

Project:
  Name: {proj.name}
  One-liner: {proj.one_liner}
  Differentiator: {proj.differentiator or '(skip — focus on signal alignment)'}
  Free offer: {proj.free_offer or '(say "free to try, takes 30 seconds")'}
  Paid tier (after free): {proj.paid_tier or '(skip)'}
  Proof URL: {proj.proof_url or '(skip)'}

Founder: {proj.founder_name} <{proj.founder_email}>

Write the email now."""


def _template_fallback(lead: Lead, proj: Project) -> Draft:
    """No-API-key path. Less personalized, but doesn't ship 'Dear Sir/Madam'.
    Picks the first 60 chars of signal_text as the open."""
    first_name = lead.name.split()[0] if lead.name else "there"
    signal_excerpt = lead.signal_text.strip().split("\n")[0][:120]
    free_line = (proj.free_offer or "Free to try, no signup wall — takes "
                 "30 seconds.")
    subject = proj.name[:30]
    body = (
        f"Hey {first_name},\n\n"
        f"Saw this — \"{signal_excerpt}\".\n\n"
        f"{proj.name}: {proj.one_liner}\n\n"
        f"{free_line} If it's not for you, no email follow-up.\n\n"
        f"— {proj.founder_name.split()[0] if proj.founder_name else 'me'}"
    )
    return Draft(
        lead_email=lead.email,
        lead_name=lead.name,
        project_name=proj.name,
        subject=subject,
        body=body,
        drafted_at=datetime.now(timezone.utc),
        raw_prompt="(template mode — no API key)",
        raw_response="",
    )


def draft_email(
    lead: Lead,
    proj: Project,
    *,
    model: str = DEFAULT_MODEL,
    client: Optional[AnthropicClient] = None,
) -> Draft:
    """Draft one email. Always returns a Draft."""
    if client is None:
        client = AnthropicClient(usage_log_path=USAGE_LOG_PATH)

    if not client.configured:
        return _template_fallback(lead, proj)

    user_prompt = _build_user_prompt(lead, proj)
    obj, err = client.messages_create_json(
        schema=DRAFT_SCHEMA,
        model=model,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    if err is not None:
        d = _template_fallback(lead, proj)
        d.raw_response = f"(LLM error, fell back to template: {err})"
        return d

    subject = (obj.get("subject") or "").strip()
    body = (obj.get("body") or "").strip()
    if not subject or not body:
        d = _template_fallback(lead, proj)
        d.raw_response = "(LLM returned empty subject/body, fell back)"
        return d

    # L3 skill library: record successful Claude drafts so distill_skill
    # can derive a learned 'draft-customer-outreach' template later.
    try:
        from solo_founder_os import record_example
        record_example(
            "draft-customer-outreach",
            inputs={
                "lead_name": lead.name,
                "signal_source": lead.signal_source,
                "signal_text": lead.signal_text[:300],
                "project_name": proj.name,
                "one_liner": proj.one_liner,
                "free_offer": proj.free_offer,
            },
            output=f"Subject: {subject}\n\n{body}",
            note="LLM-drafted, pre-HITL",
        )
    except Exception:
        pass

    return Draft(
        lead_email=lead.email,
        lead_name=lead.name,
        project_name=proj.name,
        subject=subject,
        body=body,
        drafted_at=datetime.now(timezone.utc),
        raw_prompt=user_prompt,
        raw_response=f"(structured-output JSON: {obj})",
    )

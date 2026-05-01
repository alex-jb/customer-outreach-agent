"""HITL queue — markdown files in ~/.customer-outreach-agent/queue/.

Wraps solo-founder-os's HitlQueue. Renders the agent-specific markdown
body. Same shape as vc-outreach's queue, different content.
"""
from __future__ import annotations
import pathlib
from datetime import datetime, timezone

from solo_founder_os.hitl_queue import (
    APPROVED,
    HitlQueue,
    PENDING,
    REJECTED,
    SENT,
    make_basename,
    sanitize_filename_part,
)

from .models import Draft


DEFAULT_QUEUE_ROOT = (pathlib.Path.home()
                     / ".customer-outreach-agent" / "queue")


def _queue() -> HitlQueue:
    return HitlQueue.from_env("CUSTOMER_OUTREACH_QUEUE",
                                default=DEFAULT_QUEUE_ROOT)


def _render_markdown(draft: Draft, status: str) -> str:
    parts = [
        "---",
        f"to: {draft.lead_email}",
        f"name: {draft.lead_name}",
        f"project: {draft.project_name}",
        f"status: {status}",
        f"drafted_at: {(draft.drafted_at or datetime.now(timezone.utc)).isoformat()}",
        "---",
        "",
        f"# {draft.subject}",
        "",
        f"**To:** {draft.lead_email}",
        "",
        "## Body",
        "",
        draft.body,
        "",
        "---",
        "",
        "## Audit",
        "",
        "### Prompt",
        "```",
        draft.raw_prompt[:2000] if draft.raw_prompt else "(template fallback)",
        "```",
        "",
        "### Response",
        f"`{(draft.raw_response or '')[:200]}`",
        "",
    ]
    return "\n".join(parts)


def queue_draft(draft: Draft, *, status: str = PENDING) -> pathlib.Path:
    q = _queue()
    body = _render_markdown(draft, status)
    base = make_basename(
        slug=sanitize_filename_part(draft.lead_email.split("@")[0]),
        ext="md",
    )
    return q.write(status=status, basename=base, body=body)


def list_queue(*, status: str = PENDING) -> list[pathlib.Path]:
    return _queue().list(status=status)


__all__ = [
    "queue_draft", "list_queue",
    "PENDING", "APPROVED", "REJECTED", "SENT",
]

"""MCP server — Claude Desktop / Cursor / Zed customer-outreach drafting."""
from __future__ import annotations
import os
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    print("customer-outreach-mcp requires the `mcp` package. "
          "Install with: pip install 'customer-outreach-agent[mcp]'",
          file=sys.stderr)
    raise SystemExit(1) from e

from .drafter import draft_email
from .models import Lead, Project
from .queue import APPROVED, PENDING, list_queue, queue_draft


mcp = FastMCP("customer-outreach")


@mcp.tool()
def draft_outreach_email(
    lead_email: str,
    signal_text: str,
    project_name: str,
    one_liner: str,
    lead_name: str = "",
    handle: str = "",
    signal_source: str = "",
    differentiator: str = "",
    free_offer: str = "",
    paid_tier: str = "",
    founder_name: str = "",
    save_to_queue: bool = False,
) -> str:
    """Draft one customer-outreach email. The signal_text is the verbatim
    observation that triggered outreach (their tweet, their PH comment).
    Required so we don't ship generic cold spam."""
    if not signal_text.strip():
        return "Refusing to draft — signal_text is empty."
    lead = Lead(email=lead_email, signal_text=signal_text,
                  signal_source=signal_source, name=lead_name, handle=handle)
    proj = Project(name=project_name, one_liner=one_liner,
                    differentiator=differentiator, free_offer=free_offer,
                    paid_tier=paid_tier, founder_name=founder_name)
    draft = draft_email(lead, proj)
    parts = [
        f"### To: {draft.lead_email}",
        f"### Subject: {draft.subject}",
        "",
        draft.body,
    ]
    if save_to_queue:
        path = queue_draft(draft, status=PENDING)
        parts.append("")
        parts.append(f"📥 saved to HITL queue: `{path}`")
    return "\n".join(parts)


@mcp.tool()
def list_pending() -> str:
    """Drafts in pending/ awaiting review."""
    paths = list_queue(status=PENDING)
    if not paths:
        return "No drafts pending review."
    return "Pending drafts:\n" + "\n".join(f"- {p}" for p in paths)


@mcp.tool()
def list_approved() -> str:
    """Drafts in approved/ ready to send."""
    paths = list_queue(status=APPROVED)
    if not paths:
        return "No approved drafts ready to send."
    return "Approved drafts:\n" + "\n".join(f"- {p}" for p in paths)


def main() -> None:
    if os.getenv("CUSTOMER_OUTREACH_SKIP") == "1":
        return
    mcp.run()


if __name__ == "__main__":
    main()

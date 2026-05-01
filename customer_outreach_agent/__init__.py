"""customer-outreach-agent — cold-email drafter for potential paying customers.

Solo Founder OS agent #10 (the 6th of the 7 canonical one-person-company
stack layers: sales / customer acquisition).

vc-outreach-agent is for INVESTORS (the ask: meeting). This agent is for
CUSTOMERS (the ask: try product, give feedback, maybe pay).

Different shape:
  - Open with the signal that triggered outreach (saw your tweet / your
    project hit Active stage / you starred the repo) — not a thesis hint
  - Lead with the product, not the company
  - 90 words, ≤6-word subject
  - Offer is concrete and reversible (free trial / 14-day money-back),
    not "would you take a meeting"

NEVER auto-sends. All drafts go through HITL.
"""
__version__ = "0.1.0"

from .models import Lead, Project, Draft
from .drafter import draft_email
from .queue import queue_draft, list_queue, PENDING, APPROVED, REJECTED, SENT

__all__ = [
    "Lead", "Project", "Draft",
    "draft_email",
    "queue_draft", "list_queue",
    "PENDING", "APPROVED", "REJECTED", "SENT",
]

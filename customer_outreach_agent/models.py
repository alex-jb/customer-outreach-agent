"""Data classes — Lead (the customer target), Project (what we're selling),
Draft (the output)."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Lead:
    """One potential customer.

    The minimum viable record is email + signal — concrete observable
    behavior that tells you THIS person might want THIS product.

      Lead(
          email="alice@x.com",
          name="Alice",
          signal_source="x.com/alice/status/...",
          signal_text="tweeted: 'tired of launch boards that don't track \
            evolution over time'",
          handle="@alice",
      )

    `signal_text` is the open of every outreach email — verbatim. If you
    don't have a specific signal, don't email this person. Generic outbound
    to cold lists is the wrong audience for this agent.
    """
    email: str
    signal_source: str  # URL or "PH comment on vibex" etc
    signal_text: str    # the verbatim observation
    name: str = ""
    handle: str = ""    # @handle on X, IH username, etc
    notes: str = ""
    last_contacted: Optional[datetime] = None


@dataclass
class Project:
    """The project being pitched. Customer-facing wording (NOT investor-deck)."""
    name: str
    one_liner: str
    differentiator: str = ""  # what makes THIS product not generic
    free_offer: str = ""       # "free for 14 days", "free for first 100 users"
    paid_tier: str = ""        # "$5/month after", "$3 one-time"
    proof_url: str = ""         # social proof link (a real success story)
    founder_name: str = ""
    founder_email: str = ""


@dataclass
class Draft:
    """Output of the drafter — one email for (lead, project)."""
    lead_email: str
    subject: str
    body: str
    lead_name: str = ""
    project_name: str = ""
    drafted_at: Optional[datetime] = None
    raw_prompt: str = ""
    raw_response: str = ""

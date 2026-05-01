"""CLI: customer-outreach-agent <subcommand>.

Subcommands:
    draft  --project P.json --leads L.csv  → fan into HITL queue
    queue  [--status pending|approved|rejected|sent] → list

Bypass: CUSTOMER_OUTREACH_SKIP=1
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import sys
from pathlib import Path

from .drafter import draft_email
from .models import Lead, Project
from .queue import APPROVED, PENDING, REJECTED, SENT, list_queue, queue_draft


def _load_project(path: str) -> Project:
    raw = Path(path).read_text()
    if path.endswith(".json"):
        data = json.loads(raw)
    else:
        # tiny YAML-ish: key: value, no nesting
        data = {}
        for line in raw.splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                k, _, v = line.partition(":")
                data[k.strip()] = v.strip()
    return Project(
        name=data.get("name", ""),
        one_liner=data.get("one_liner", ""),
        differentiator=data.get("differentiator", ""),
        free_offer=data.get("free_offer", ""),
        paid_tier=data.get("paid_tier", ""),
        proof_url=data.get("proof_url", ""),
        founder_name=data.get("founder_name", ""),
        founder_email=data.get("founder_email", ""),
    )


def _load_leads(path: str) -> list[Lead]:
    """CSV columns: email,name,handle,signal_source,signal_text,notes."""
    out: list[Lead] = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if not row.get("email"):
                continue
            if not row.get("signal_text"):
                # Skip cold rows without a signal — agent's whole point is
                # personalization on a real observation
                print(f"⚠️  skipping {row.get('email')}: no signal_text",
                      file=sys.stderr)
                continue
            out.append(Lead(
                email=row["email"].strip(),
                name=(row.get("name") or "").strip(),
                handle=(row.get("handle") or "").strip(),
                signal_source=(row.get("signal_source") or "").strip(),
                signal_text=row["signal_text"].strip(),
                notes=(row.get("notes") or "").strip(),
            ))
    return out


def cmd_draft(args) -> int:
    proj = _load_project(args.project)
    leads = _load_leads(args.leads)
    if not leads:
        print("no leads with signal_text — nothing to draft", file=sys.stderr)
        return 0
    print(f"drafting {len(leads)} email(s) for {proj.name}", file=sys.stderr)
    for lead in leads:
        d = draft_email(lead, proj)
        path = queue_draft(d)
        print(f"  ✓ {lead.email} → {path.name}", file=sys.stderr)
    return 0


def cmd_queue(args) -> int:
    status = args.status or PENDING
    paths = list_queue(status=status)
    if not paths:
        print(f"(queue empty: {status})", file=sys.stderr)
        return 0
    print(f"# {status} ({len(paths)})")
    for p in paths:
        print(f"  - {p.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if os.getenv("CUSTOMER_OUTREACH_SKIP") == "1":
        return 0

    p = argparse.ArgumentParser(
        prog="customer-outreach-agent",
        description="Cold-email drafter for paying customers (not investors).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("draft", help="Draft emails for a CSV of leads.")
    d.add_argument("--project", required=True,
                    help="JSON or tiny-YAML file describing the project.")
    d.add_argument("--leads", required=True,
                    help="CSV with columns: email,name,handle,"
                         "signal_source,signal_text,notes")
    d.set_defaults(func=cmd_draft)

    q = sub.add_parser("queue", help="List queue.")
    q.add_argument("--status",
                    choices=[PENDING, APPROVED, REJECTED, SENT],
                    default=PENDING)
    q.set_defaults(func=cmd_queue)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

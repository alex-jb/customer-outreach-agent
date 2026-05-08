# customer-outreach-agent

> Solo Founder OS agent #10 — cold-email drafter for **paying customers** (not investors). Personalized on a verbatim signal; HITL queue.

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](#)

Built by [Alex Ji](https://github.com/alex-jb) — closes the 6th of 7 canonical one-person-company stack layers (sales / customer acquisition).

## Why this isn't vc-outreach-agent

`vc-outreach-agent` writes to investors. The ASK is "take a meeting." The OPEN is a thesis hint.

`customer-outreach-agent` writes to potential paying users. The ASK is "try the product, free, no meeting." The OPEN is a verbatim signal — what they actually said about a problem your product solves.

Different audience, different shape. Different system prompt, different schema, different banned phrases.

## What it refuses to do

If a lead row has no `signal_text`, this agent skips it. Generic outbound email blasts to cold lists is the wrong tool for this agent. Bring observable signals (their tweets, their PH comments, their repo stars) or this agent does nothing.

## Install

```bash
pip install customer-outreach-agent
# or
git clone https://github.com/alex-jb/customer-outreach-agent
cd customer-outreach-agent && pip install -e .
```

## Usage

### 1. Project file

```yaml
# orallexa.yml (or .json)
name: VibeXForge
one_liner: Forge AI projects into 16-bit pixel heroes that evolve from Seed to Myth.
differentiator: Real traction drives stage advancement, not algorithm magic
free_offer: Free to forge first project — 30 seconds, no signup gate
paid_tier: Hero Card skins from $3 (cosmetic only)
proof_url: https://www.vibexforge.com/project/breakout-example
founder_name: Alex Ji
founder_email: alex@vibexforge.com
```

### 2. Leads CSV

```csv
email,name,handle,signal_source,signal_text,notes
alice@example.com,Alice,@alice_dev,x.com/alice_dev/status/123,"tweeted: 'tired of launch boards that disappear after day-1'",
bob@example.com,Bob,@bob,producthunt.com/posts/x/comments,"commented: 'wish there was a launch board where projects keep evolving'",
```

### 3. Draft

```bash
customer-outreach-agent draft \
  --project orallexa.yml \
  --leads leads.csv

# drafting 12 email(s) for VibeXForge
#   ✓ alice@example.com → 2026-05-02-alice.md
#   ✓ bob@example.com → 2026-05-02-bob.md
#   ⚠️  skipping cold@example.com: no signal_text
```

Each draft lands in `~/.customer-outreach-agent/queue/pending/`. Review in Obsidian, move to `approved/` to send manually (or wire SMTP per vc-outreach pattern in v0.2).

## MCP server

```bash
pip install 'customer-outreach-agent[mcp]'
```

```json
{
  "mcpServers": {
    "customer-outreach": {
      "command": "customer-outreach-mcp",
      "env": { "ANTHROPIC_API_KEY": "..." }
    }
  }
}
```

Tools: `draft_outreach_email(...)` · `list_pending()` · `list_approved()`

The MCP `draft_outreach_email` tool *enforces* the signal_text requirement — it refuses to draft without one, even from Claude Desktop.

## Roadmap

- [x] **v0.1** — Claude drafter + heuristic template fallback · HITL queue · MCP server · 6 tests
- [ ] **v0.2** — SMTP sender for approved drafts (mirroring vc-outreach pattern)
- [ ] **v0.3** — Auto-source signals from CDA digests + funnel-analytics top-stage VibeX users
- [ ] **v0.4** — A/B variant bandit on subject lines (lift `solo_founder_os.bandit`)
- [ ] **v0.5** — Reply parser → CRM-lite (open rate / reply rate / churn rate per signal source)

## License

MIT.

# customer-outreach-agent (DEPRECATED — merged into vc-outreach-agent v0.9.0)

> ⚠️ **This agent has been merged into [vc-outreach-agent](https://github.com/alex-jb/vc-outreach-agent) as `--mode customer`.**
>
> Date of merge: 2026-05-08 (in vc-outreach-agent commit `6a06103`, release `v0.9.0`).

## How to migrate (1 line)

```bash
pip uninstall customer-outreach-agent
pip install vc-outreach-agent
```

The `customer-outreach-agent` console_script keeps working — it's now a back-compat alias provided by `vc-outreach-agent`. Existing shell history, cron jobs, and scripts that call:

```bash
customer-outreach-agent draft --project p.json --leads leads.csv
customer-outreach-agent queue
```

continue to work unchanged. Internally the `draft` subcommand is mapped to `customer-draft` on the merged binary.

Existing queue files at `~/.customer-outreach-agent/queue/` are also unchanged — paths preserved. Existing usage log at `~/.customer-outreach-agent/usage.jsonl` is still where customer-mode drafts write, so cost-audit-agent attribution keeps working.

## Why merge?

The audit on 2026-05-08 found that this repo was structurally a fork of `vc-outreach-agent`:
- ~120 LOC of real semantic delta (different prompt, different recipient validation, Haiku default vs Sonnet, `skip_reflection=True` flag).
- ~50 LOC of pure rename (`Investor` → `Lead`, `vc_*` → `customer_*`).
- 5 of 6 vc-outreach test files (`test_enricher`, `test_sender`, `test_queue`, `test_mcp_server`, `test_vibex_traction`) cover surface area this repo never had — so customer mode was missing free SMTP sender + VibeX traction + CDA enricher hooks that VC mode shipped.

Merging gives customer mode all of those for free, drops Solo Founder OS stack from 11 → 10 agents, and removes 11 separate README footers / release pipelines for what is structurally one cold-email tool with two recipient personas.

See [vc-outreach-agent CHANGELOG v0.9.0](https://github.com/alex-jb/vc-outreach-agent/blob/main/CHANGELOG.md) for the full migration note + skipped plan items.

## Reversal cost

If customer outreach diverges enough in 6 months to justify its own surface (e.g. Stripe-integrated upsell flow that VC doesn't share), re-splitting takes ~2 hours — same magnitude as the merge. Low lock-in.

## Original v0.2.0 README

Preserved at [`README.v0.2.0-archived.md`](./README.v0.2.0-archived.md) for posterity.

---

## ⏳ Repo will be archived

This repo is staying public + writable for a brief grace period to let any cron / installed scripts confirm the alias path works. Plan: `gh repo archive alex-jb/customer-outreach-agent` after 1 week of clean operation. Re-open by un-archiving if any path breaks.

# Starling Business

checked: 2026-10-21
type: bank
routes (easiest first): api | platform_feed | manual_export

## Route 1 — Direct API (free) ← default

The account holder creates a **personal access token** in the Starling developer portal (developer.starlingbank.com), linked to their own account, with read-only scopes (account, balance, transaction). The token goes in the user's own secret store (environment variable or OS keychain), never in a file in the repo or in chat. The agent then pulls lines daily, and nobody has to do anything after that.

## Route 2 — Accounting platform feed

Free direct feeds to Xero and FreeAgent. Use them if the user already has the platform.

## Route 3 — Manual export

App → account → **Statements** → choose a period → CSV or PDF.

## Format notes

- Use the **settled** feed dated by `settlementTime`. `transactionTime` puts card lines a day early (about 118 a year on a typical small account). Pulled this way, the feed reproduced a full year's statement exactly.
- Statement endpoints return 404 with a personal token. Running balances are built from a known opening balance.
- Windows over a year are rejected and bursts are rate-limited, so pull ~6-month windows with backoff.

## Sources

- https://developer.starlingbank.com/docs

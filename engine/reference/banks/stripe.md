# Stripe (payments balance, and optionally Treasury)

checked: 2026-10-25
type: money_platform
routes (easiest first): api

## Route 1 — Direct API with a restricted read-only key (free) ← default

1. Stripe Dashboard → **Developers → API keys** → **Create restricted key** (start from zero permissions).
2. Set **Read** on: *Balance*, *Balance transactions*, *Payouts*, *Charges*, *Refunds*, *Disputes*. Add *Treasury / Financial accounts: Read* only if the user uses Treasury. Leave everything else on **None**; the agent never needs Write. Stripe recommends restricted keys for AI agents.
3. Name it for the kit, approve the two-factor prompt, and copy the key (`rk_live_…`). It's shown only once.
4. The key goes in the user's own secret store (environment variable or OS keychain), never in a file in the repo or in chat.
5. The agent lists **balance transactions** for the period: every charge, fee, refund, payout and adjustment, with the net effect on the Stripe balance. That's a complete, balance-proven ledger for the Stripe account.

If permission names in the Dashboard differ from the list above, pick the read permission that matches the endpoint. A missing permission returns an error naming what to add.

## How it goes in the books — avoid counting sales twice

Treat the Stripe balance as **its own account**, like a second bank account:

| Stripe line | Books |
|---|---|
| Charge (gross) | Sales, into the Stripe account |
| Fee | Cost (bank/payment charges), out of the Stripe account |
| Refund / dispute | Reduces sales (dispute fee = cost) |
| **Payout** | **Transfer** Stripe → bank. Never income |

The payout credit on the bank statement is the other half of that transfer. Counting it as income as well as the charges counts the sales twice. The year-end Stripe balance (money not yet paid out) is cash held by the company.

## Route 2 (option, not a default) — Stripe Treasury as the main account

UK: **public preview** (2026-10). A GBP business account with a sort code and account number, Faster Payments/CHAPS in, GBP/EUR/USD balances, outbound payments and cards (cards for your own business: private preview). Eligibility is decided per account. It is **not a bank account** and **not FSCS-protected**: funds are safeguarded under FCA e-money rules. Only for a user who chooses it. Keep a small FSCS-covered bank account alongside for HMRC, salaries and resilience. Treasury lines come through the same API, so they need no extra effort for the books.

## Format notes

- Amounts are in the smallest unit (pence); divide by 100.
- `available_on` ≠ `created`: book by `created`, and use `available_on` only for cash timing.
- Payouts can batch many days of charges, so match a bank payout to Stripe by payout ID and amount, not by date.

## Sources

- https://docs.stripe.com/keys/restricted-api-keys
- https://docs.stripe.com/treasury
- https://support.stripe.com/questions/understanding-your-financial-account?locale=en-GB
- https://docs.stripe.com/issuing/for-your-business?locale=en-GB

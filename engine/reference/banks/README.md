# Bank and money-platform guides — how to get transactions out of each one

One file per bank or money platform. In setup and at each month-end, the agent reads the guide for every account the user has and takes the easiest route the user is happy with. When a user names a bank or platform with no guide yet, the agent researches it (the provider's own help pages first), writes the guide here using the shape below, and the next user of that bank gets it straight away.

**Rules**

- **Adapt to the user's bank.** Never recommend switching banks or buying a paid tier as the default. A paid tier is an option the user can choose.
- **Generic only.** These files ship in the kit. Notes about one company (what it chose, its balances, its quirks) go in `books/<entity>/gotchas.md`, never here.
- **Re-verify** a guide whose `checked` date is over 6 months old before relying on its menu steps.

## File shape

```
# <Bank or platform product>
checked: YYYY-MM-DD
type: bank | money_platform | card
routes (easiest first): api | platform_feed | cloud_auto_export | emailed | manual_export
## Route 1 … n   — steps, plan/cost needed, format, what the agent does with it
## Format notes  — columns, date format, running balance, quirks
## Sources       — provider URLs
```

The format the agent wants, in order: **API** > **CSV with a running balance** > CSV > PDF statement > anything else. The balance proof (`engine/scripts/validate.py`) needs the opening and closing balance for the period whatever the format.

## Index

| Guide | Type | Best free route | Checked |
|---|---|---|---|
| [monzo_business.md](monzo_business.md) | bank | Laptop CSV export | 2026-10-21 |
| [starling_business.md](starling_business.md) | bank | Direct API (personal access token) | 2026-10-21 |
| [barclaycard_commercial.md](barclaycard_commercial.md) | card | PDF statement (other routes not researched) | 2026-10-21 |
| [stripe.md](stripe.md) | money_platform | Direct API (restricted read-only key) | 2026-10-25 |

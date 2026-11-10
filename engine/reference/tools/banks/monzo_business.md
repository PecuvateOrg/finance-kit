# Monzo Business

checked: 2026-10-21
type: bank
routes (easiest first): cloud_auto_export (paid) | manual_export | platform_feed (paid)
No API for business accounts: Monzo's developer API covers personal and joint accounts only, and there's no free self-serve UK open-banking aggregator (checked 2026-10-21).

## Route 1 — Auto-export to Google Drive / OneDrive (Business Pro or Team, from ~£9/month)

App → Home → swipe down → **Auto-export documents** → connect Drive or OneDrive → choose **CSV**. Last month's statement lands in a "Monzo Business" folder on the 1st of each month, and older months can be exported too. The agent reads the folder; nobody has to do anything.
Offer this as an option only; never as the default.

## Route 2 — Laptop export (free, all plans) ← default

1. Go to **business.monzo.com** and sign in. Approve the login in the Monzo app on your phone.
2. Click **Export statement** on the home screen.
3. Pick the dates: the **whole previous month** (1st to last day), or every month since the last one the agent has.
4. Format **CSV**.
5. Put the file in the company's statement folder, or hand it to the agent in the session.

Phone alternative: tap ⋯ on the business card → **Bank statements** → period → CSV.

## Route 3 — Through an accounting platform (FreeAgent / Xero)

Direct feeds exist, but reportedly need a paid Monzo Business tier [unverified]. Only relevant if the user already pays for both.

## Format notes

- CSV statements have a running **Balance** column, so the agent can prove the balance line by line. The *live Google Sheets* transaction export doesn't (it comes from the activity feed, where amounts can change), so don't use it for the books.
- Dates are day first (DD/MM/YYYY).
- The main account's running **Balance excludes money in pots**. Each pot is its own account in the books, and the company's cash = main balance + pots.
- Pot transfers show as separate counterparties. Pots are still the company's cash: they net to zero against the pot, and a closing pot balance counts towards cash at the year end.

## Sources

- https://monzo.com/help/business-accounts/auto-export-business-documents-web
- https://community.monzo.com/t/we-ve-added-a-running-balance-to-monzo-business-csv-exports/164885
- https://monzo.com/help/business-accounts/auto-export-business-transactions-web

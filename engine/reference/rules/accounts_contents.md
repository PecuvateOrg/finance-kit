# Micro-entity accounts (FRS 105) — tool-neutral

For a company that is micro under `company_size.json` and not excluded (see `company_size.md`).

## What they contain
- **Balance sheet:** fixed assets, current assets, creditors due within one year, net current assets, total assets less current liabilities, creditors due after more than one year, accruals and deferred income, net assets, capital and reserves. For a company limited by guarantee (most CICs): no share capital, reserves only.
- **Statements on the balance sheet:** that the accounts are prepared under the micro-entity provisions; that the company was entitled to audit exemption and the members have not required an audit; the directors' responsibility for accounting records and accounts; the date the board approved them and the director who signed.
- **Notes:** average number of employees; advances, credits and guarantees to directors; financial commitments, guarantees and contingencies not on the balance sheet.
- **Profit and loss account:** prepared for the members, but a micro company does not have to file it at Companies House (it does go to HMRC with the CT600).

*Contents above are from the Companies Act 2006 micro-entity provisions (s384A, s396, s413) and FRS 105; not yet checked against a GOV.UK page. Check against the filing tool's micro-entity template at the first filing and note any difference here.*

The engine produces every figure in `accounts.json` → `financials` (`build_accounts.py`); a director confirms the nil notes (`nil_disclosures_confirmed`) before filing.

## Deadlines and penalties (private company)
| What | When / amount |
|---|---|
| Accounts to Companies House | 9 months after the accounting reference date. First accounts covering more than 12 months: 21 months from incorporation, or 3 months from the accounting reference date if later |
| Late filing penalty | up to 1 month £150; 1–3 months £375; 3–6 months £750; over 6 months £1,500; doubled if late two years running |

Sources: [GOV.UK: Life of a company, accounts](https://www.gov.uk/government/publications/life-of-a-company-annual-requirements/life-of-a-company-part-1-accounts), [GOV.UK: late filing penalties](https://www.gov.uk/annual-accounts/penalties-for-late-filing). Checked 2026-11-10; review by 2027-04-06.

**Announced, not yet in force:** Companies House reforms (Economic Crime and Corporate Transparency Act 2023) will require accounts to be filed through software and will change what micro companies file. Check GOV.UK for the start date before each year end.

**A CIC** files its accounts together with the CIC34 report (`cic34_contents.md`) as one delivery, with a £15 fee, through Companies House's package-accounts route, not through filing-software gateways.

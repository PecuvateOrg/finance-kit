# SimpleCompanyTax — CIC accounts + CIC34 as a package ZIP, no API

checked: 2026-11-10 · price: `prices.json` → `simplecompanytax_cic` (unlimited filings a year per company)

**For:** micro companies (FRS 105). Files the CT600 to HMRC and, for an ordinary company, the accounts to Companies House. For a CIC it files the CT600 and builds the package file (accounts + CIC34) that you upload yourself (`../companies_house/package_upload.md`). Also files an unincorporated club's CT600 without accounts.
**Help:** https://www.simplecompanytax.co.uk/ · pricing https://www.simplecompanytax.co.uk/pricing
**Not covered:** small-company (FRS 102 1A) accounts; no API, so the user submits; it imports figures from a CSV or Excel file (or Xero, QuickBooks), so the engine hands over a file rather than numbers to type.

**Asks for:** the micro balance sheet and profit and loss from the engine's draft (`../rules/accounts_contents.md`), and the CIC34 answers (`../rules/cic34_contents.md`): community benefit, consultation, directors' pay, asset transfers.

**Done when:** the ZIP it produces shows the same figures as the engine's draft (check every line), and the CIC34 text matches what the directors approved.

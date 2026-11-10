# Companies House — confirmation statement (direct)

checked: 2026-11-10 · fee: `prices.json` → `ch_confirmation_statement` (alternative: TinyTax files it for a fee that includes this one; see `prices.json` → `ch_confirmation_statement` note)

**For:** the yearly check that Companies House holds the right company details. Every company, CICs included; unincorporated clubs don't file one.
**Help:** https://www.gov.uk/file-your-confirmation-statement-with-companies-house
**Asks for (from `../rules/confirmation_statement.md`):** registered office, directors, people with significant control, shareholders or members, SIC codes, registered email, and that activities are lawful. Each director needs their identity-verification personal code.

**Engine prepares:** the answers from `entity.json`, and a reminder before the due date (14 days after the review date).

**Done when:** the statement shows in the company's filing history, and the details there match `entity.json`.

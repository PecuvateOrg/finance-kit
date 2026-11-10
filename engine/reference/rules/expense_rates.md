# Flat-rate expenses paid to a director

Rates: `expense_rates.json` (the only copy; `engine/scripts/build_tb.py` reads it). Checked 2026-11-10; review by 2027-04-06.

- **Business mileage in the director's own car or van:** 55p a mile for the first 10,000 business miles **in the tax year** from 6 April 2026 (45p before), 25p after. The 10,000 counts per **tax year** (6 April – 5 April), not per accounting period. Motorcycles 24p, bicycles 20p (not in the engine yet). Needs a mileage log. [GOV.UK](https://www.gov.uk/expenses-and-benefits-business-travel-mileage/rules-for-tax)
- **Working from home:** £6 a week, no receipts needed; more only with evidence of the extra cost. [GOV.UK](https://www.gov.uk/tax-relief-for-employees/working-at-home)

**How the engine asks:** `accounts.decisions.mileage` is `{"miles": n}` when the whole accounting period sits in one tax year. When the period crosses 6 April, it is `{"by_tax_year": {"2025-26": {"miles": n, "earlier_miles": m}, "2026-27": {"miles": n}}}`, where `earlier_miles` is business miles already driven in that tax year before the period began (they use up the 10,000 first). Both amounts are owed to the director (director's loan account) unless the company already paid them.

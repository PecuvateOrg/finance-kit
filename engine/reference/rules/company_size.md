# Company size

The numbers are in `company_size.json` (the only copy; `engine/scripts/pick_platforms.py` reads it). Source: SI 2024/1303, The Companies (Accounts and Reports) (Amendment and Transitional Provision) Regulations 2024 — https://www.legislation.gov.uk/uksi/2024/1303/contents/made. Checked 2026-11-10; review by 2027-04-06.

**How size works:** a company is micro or small if it meets **at least 2 of the 3** limits (turnover, balance sheet total, average employees) for two years running; a new company uses its first year. Use the row for the period's **start date**: periods starting on or after 6 April 2025 use the raised limits (micro £1m / £500k / 10; small £15m / £7.5m / 50). For a period starting on or after that date, the new limits may also be applied to the year before when working out the two years (transitional rule).

**What each size files** (tool-neutral):
- **Micro-entity:** FRS 105 accounts. At Companies House only the balance sheet and notes have to be filed. A CIC files its accounts together with the CIC34 report.
- **Small:** FRS 102 Section 1A accounts. Not yet covered by this engine.
- **Medium and above:** not covered.

**Never micro whatever the size:** charities, investment undertakings, financial holding undertakings, credit institutions and insurers (Companies Act s384B). Charities are out of scope for this engine anyway.

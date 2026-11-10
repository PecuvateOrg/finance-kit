# Corporation tax

Rates and limits: `corporation_tax.json` (the only copy; `engine/scripts/build_accounts.py` reads it). Source: [HMRC rates and allowances](https://www.gov.uk/government/publications/rates-and-allowances-corporation-tax/rates-and-allowances-corporation-tax), updated 1 April 2026. Checked 2026-11-10; review by 2027-03-31.

## How the tax is worked out
- **Financial years** run 1 April – 31 March. From 1 April 2023: 19% on profits up to the lower limit (£50,000), 25% above the upper limit (£250,000), and in between the main rate less **marginal relief** = (upper limit − profits) × 3/200. Before that: 19% flat.
- **Short periods:** both limits are reduced in proportion to the days in the period. **Associated companies** (companies under common control, ignoring dormant ones): limits divided by 1 + the number of them. Example (GOV.UK): 3 associated companies → lower £12,500, upper £62,500.
- **A period that crosses a rate change** is split by days between the two financial years. The engine stops and says so rather than guessing.
- **Marginal relief** uses "augmented profits" (taxable profits plus exempt distributions from non-group companies). The engine assumes there are none; if the company received dividends from other companies, stop and include them.
- **Losses:** a trading loss carried forward reduces later trading profits; the director confirms the brought-forward figure.

## Deadlines and penalties
| What | When | Source |
|---|---|---|
| Pay the tax (taxable profits up to £1.5m) | 9 months and 1 day after the end of the accounting period | [GOV.UK: pay Corporation Tax](https://www.gov.uk/pay-corporation-tax) |
| File the CT600 | 12 months after the end of the accounting period | [GOV.UK: Company Tax Returns](https://www.gov.uk/company-tax-returns) |
| Late filing | £200 at 1 day; another £200 at 3 months; at 6 months HMRC estimates the bill and adds 10% of unpaid tax; another 10% at 12 months. Late 3 times in a row: the £200 penalties become £1,000 each | [GOV.UK: penalties](https://www.gov.uk/company-tax-returns/penalties-for-late-filing) |

Interest runs on tax paid late. A company's first accounting period starts on incorporation or when it starts trading, and is never longer than 12 months, so a long first set of accounts means two CT600s.

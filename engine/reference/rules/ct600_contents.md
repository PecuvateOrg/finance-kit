# What a CT600 needs (micro trading company or CIC) — tool-neutral

Any filing tool asks for the same things. Prepare all of them before opening the tool; never type a figure that isn't in the engine's output.

| Item | Where it comes from in the engine |
|---|---|
| Company name, registration number, UTR (10 digits, from HMRC's letters or the HMRC online account) | `books/<id>/entity.json`; the UTR is asked for at this step, never at setup |
| Accounting period start and end (12 months or less) | `filed/<FY>/inputs.json` `period_start` / `period_end` |
| Company type (trading company; a CIC is taxed like any company, it is not a charity) | `entity.json` |
| Turnover | `accounts.json` → `financials.profit_and_loss.turnover` |
| Trading profit or loss after tax adjustments (add back disallowed costs such as depreciation and entertaining; capital allowances instead) | `accounts.json` → tax block |
| Trading losses brought forward used, and carried forward | director-confirmed decision `trading_losses_bf` |
| Number of associated companies | director-confirmed decision `associated_companies` |
| Chargeable profits, tax at each rate, marginal relief, tax payable | `accounts.json` → tax block (rates: `corporation_tax.json`) |
| The accounts and the tax computation, in iXBRL | produced by the filing tool from the same figures |
| Declaration by a director (or authorised person) | the director, after reading the approval pack |
| Filing credentials (the company's HMRC Government Gateway login, or the tool's own HMRC authorisation) | asked for at the submit step only, held in the user's secret store |

**Check before submitting:** the tool's calculated tax equals `accounts.json`. If they differ, stop and find out why. Keep the submission receipt in `filed/<FY>/`: HMRC offers no API to read a return's status back.

**Amending:** within 12 months of the filing deadline, file again marked as an amendment (a plain resubmission is rejected as a duplicate).

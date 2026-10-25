# TinyTax — filing connector

checked: 2026-10-25 (proven live: one micro-entity company's accounts and CT600 both accepted 2026-10)
What it does: files **FRS 105 micro-entity accounts** to Companies House and the **CT600** to HMRC (trading companies, CICs, charities with CT600E, amendments, including returns filed elsewhere), through a public API. It's HMRC-recognised software.
Cost: Solo from £59 + VAT a year (1 company), Portfolio for several. Billing happens on a real submit, never on a dry run.
Docs: https://www.tinytax.co.uk/developers/quickstart · https://tinytax.co.uk/developers/guides/trading · https://tinytax.co.uk/developers/guides/amendments · https://www.tinytax.co.uk/developers/changelog
There's also an MCP server (https://tinytax.co.uk/developers/mcp) with `validate_accounts` / `validate_ct600` tools. Use it if your agent supports MCP; the API below works without it.

**Check the field shapes against the current docs before the first filing.** The shapes below are what was accepted in October 2026.

## Calls

Base `https://tinytax.co.uk/api/v1`, header `X-API-Key: <key>`, and a normal `User-Agent` header (without one, bot protection can return a 403 that looks like a bad key).

| Call | Use |
|---|---|
| `GET /account` | test a new key (read-only) |
| `POST /filings/accounts` | accounts to Companies House (`dry_run: true` validates only) |
| `POST /filings/ct600` | CT600 to HMRC (`dry_run: true` returns calculated tax without filing) |
| `GET /filings/{filing_id}` | status: submitted → accepted / rejected |
| `GET /filings/{filing_id}/documents` | the filed documents |

Real submits take an `Idempotency-Key` header, so a retry can't file twice. Reusing a key replays the original response, so use a new key for a deliberate resubmission. Sandbox keys start `tt_test_`; magic company number `00000001`.

## Accounts request (micro), as accepted

```json
{
  "company_number": "<8 chars>",
  "period_end": "YYYY-MM-DD",
  "period": {"start": "YYYY-MM-DD"},
  "credentials": {"company_auth_code": "<from secret store>"},
  "dry_run": true,
  "accounts_type": "micro",
  "financials": {
    "profit_and_loss": {"turnover": 0, "cost_of_sales": 0, "staff_costs": 0, "depreciation": 0,
                        "other_operating_expenses": 0, "other_income": 0},
    "balance_sheet": {"fixed_assets": 0, "current_assets": 0, "creditors_within_one_year": 0,
                      "share_capital": 0, "profit_and_loss_account": 0},
    "prior_year": {"fixed_assets": 0, "current_assets": 0, "creditors_within_one_year": 0,
                   "accruals_and_deferred_income": 0, "share_capital": 0, "profit_and_loss_account": 0},
    "average_employees": 1,
    "nil_disclosures_confirmed": true,
    "losses": {"brought_forward": 0}
  }
}
```

`creditors_within_one_year` is positive here (an amount owed). `prior_year` is optional since API v2.7.0 (it's pre-filled from Companies House), but send it whenever last year was restated. Set `nil_disclosures_confirmed: true` only after the director has confirmed it.

## CT600 request

The same `financials` block, plus `"utr": "<10 digits>"` and `"associated_companies": <n>`. For a real submit, add the director's Government Gateway login inside `credentials`: `government_gateway_id` and `government_gateway_password`. **A dry run passes without them; the submit doesn't.** The response's `calculated` block (taxable profit, corporation tax, marginal relief, losses carried forward) must match the draft before you submit.

## Good to know

- TinyTax's dashboard can still show a return as due when someone else (for example a former accountant) filed it. Only HMRC online confirms returns filed elsewhere.
- Save each accepted `GET /filings/{id}` response: it's the only proof of a CT600 filing you'll have, because HMRC offers no API to read a return's status back.

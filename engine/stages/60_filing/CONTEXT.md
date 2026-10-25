# 60_filing — file the accounts and the corporation tax return (contract)

**Goal:** file the approved accounts with Companies House and the CT600 with HMRC, and keep proof that both were accepted.
**Trigger:** `50_year_end` is done (`period.json` → `match_status: draft`) and the director wants to file.
**Done means:** both filings show **accepted**; the acceptance responses are saved in `books/<id>/filed/<FY>/`; `obligations.json` marks both filed with their references; `period.json` → `match_status: filed`.

**Route:** the TinyTax API (`engine/reference/filing/tinytax.md`). The director has their **own** TinyTax account and key, so the filing is theirs. Other routes (Companies House WebFiling for accounts, other HMRC-recognised software for the CT600) are typed in by the director from a sheet the agent prepares.

---

## 0. Check what's already filed — agent

Check Companies House for accounts already made up to this year end. If they're there, don't file them again. Ask whether the CT600 was filed too. If it was, ask for the acceptance (from TinyTax or HMRC online) and save it as proof, then close the year.

## 1. Credentials, asked for now and not before — director, once per company

Ask for these only now, and say why each is needed. The director puts each in their own secret store (environment variable or OS keychain), **never in chat or a file**. Then tell the agent the variable names.

| Credential | What it is | Needed for |
|---|---|---|
| TinyTax API key (`tt_live_…`) | from their TinyTax account | both filings |
| Companies House authentication code | 6 characters, posted to the registered office (can be requested online) | accounts |
| Corporation tax UTR | 10 digits, on HMRC letters | CT600 |
| HMRC Government Gateway user ID **and password** | the director's HMRC sign-in. The user ID is 12 digits and is **not** the UTR | CT600 submission |

**Trap:** a CT600 dry run passes *without* the Gateway login, and the real submit then fails. Collect the Gateway login before filing day.

Test the key first with a read-only call (`GET /account`). A 403 can mean bot protection rather than a bad key: send a normal `User-Agent` header.

## 2. Build both requests — agent

From `period.json` and the trial balance, build the accounts request and the CT600 request (field shapes in `engine/reference/filing/tinytax.md`). Keep a copy of each in `books/<id>/filed/<FY>/tinytax/` with every credential replaced by a marker such as `<secret:CH_AUTH_CODE>`. Never store the real value.

## 3. Live dry run — agent

Send both with `dry_run: true`. Nothing is filed and nothing is charged. Check what comes back against the draft: company name, period, accounts regime (micro), taxable profit, corporation tax and losses carried forward. **Any difference stops the process** until it's explained.

## 4. Approval — director

Show, in one message:

- the figures that will be filed (P&L headline, balance sheet, tax due or nil, losses carried forward);
- the **nil disclosures** to confirm: no advances, credits or guarantees from the company to directors. Money the company *owes* a director is not one of these;
- that the accounts are the director's legal statement and the CT600 is declared in their name.

Then wait for the director to say **"approved, file"** in this session. Anything less isn't approval.

## 5. Submit — agent

Submit the accounts, then the CT600, each with `dry_run: false` and its own **idempotency key** so a retry can never file twice. Log each submission with `python3 engine/scripts/books_io.py log <id> <operation> <payload.json> <filing_id>`, with credentials as markers.

## 6. Wait for acceptance and save the proof — agent

Poll `GET /filings/{filing_id}` until Companies House and HMRC **accept** or **reject**. It's often around 20 minutes.

- **Accepted:** save the full status response as `books/<id>/filed/<FY>/tinytax/<accounts|ct600>_status.live.json`. **This is the proof of filing:** HMRC has no API to read a return's status back later.
- **Rejected:** show the director the reason in plain words, fix it from the books (never by editing a figure by hand), dry-run again, and ask for approval again if any filed figure changed.

## 7. Close the year — agent

- `obligations.json`: accounts and CT600 → `status: submitted`, with the submission references and evidence paths. Tax payment → `not_applicable` if the tax is nil; otherwise give the director the amount, the due date (9 months and 1 day after the year end, moved earlier if it falls on a weekend) and how to pay (gov.uk "Pay your Corporation Tax bill", using the payment reference from HMRC).
- `period.json`: `match_status: filed`, plus the filed dates.
- `status.json`: what's left for the director, for example "keep invoices for 6 years: list attached".

## 8. Records to keep — agent lists, director downloads

The company must keep records backing every figure for **6 years**. Bank lines prove payment; supplier invoices prove what was bought. List each supplier, where its invoices live (for example "Shopify → Settings → Billing") and which lines they cover. Download what you can reach yourself.

---

## Deadlines and costs

- Accounts: 9 months after the year end (first accounts: 21 months after incorporation). CT600: 12 months after. Tax: 9 months and 1 day after.
- **A nil return must still be filed.** Late accounts carry an automatic Companies House penalty, and a late CT600 an HMRC penalty (£100 at first), even when no tax is due. Check the current amounts on gov.uk.
- Cost: the director's TinyTax plan (from £59 + VAT a year for one company). HMRC's free filing service closed on 31/03/2026.

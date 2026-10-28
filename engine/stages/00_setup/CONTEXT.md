# 00_setup — set up a company (contract)

**Goal:** go from "here's my company" to a working `books/<entity>/` with the deadlines known and the first data in, while **asking the user as little as possible.** Everything findable in public sources is found by the agent, shown back once, and confirmed in one step.

**Trigger:** the user says "set me up", names a company, or there's no `books/` entity yet.
**Done means:** `entity.json`, `obligations.json`, `status.json` and `gotchas.md` exist for the company, each JSON file parses and `entity.json` has every key in `engine/templates/entity.json`; any bank-line files pass `engine/scripts/validate.py` (it checks bank lines only, so don't report the other files as validated); the user has seen a one-screen summary; the next step (first data in) has either started or is listed under *waiting on you*.

---

## Rule: discover → show → confirm → ask only the remainder

1. **Discover** everything public, recording each value with its source URL and date in `entity.json` → `discovered`.
2. **Show** the user one summary of what was found.
3. **Confirm** with one question: "Is this you, and is it right?" Corrections are taken in free text.
4. **Ask only what no public source holds**, in **one batch**, with a pre-filled best guess wherever there is one.
5. **Credentials are asked for at the step that needs them, never at setup.** A UTR, auth code or API key requested before it's used is a question the user didn't need to answer yet.

Never ask a question whose answer is already in a public source, in `books/`, or in an earlier answer.

---

## Step 1 — Identify the company (bind on the number, never the name)

The user may give a name, a number, a website or just "my company". Search Companies House:

- **With a Companies House API key** (free; developer.company-information.service.gov.uk, held in the user's secret store): `GET https://api.company-information.service.gov.uk/search/companies?q=<name>`.
- **Without a key:** fetch `https://find-and-update.company-information.service.gov.uk/search/companies?q=<name>`. Don't stop to ask for a key; the public pages are enough for setup.

Similar names are common, so **a name only gives candidates.** Show the best one or two (name, number, status, registered office, directors) and get one "yes, that's us". From then on, identify the company by its **company number** only. If the user is a sole trader or partnership (nothing on Companies House), say so plainly and record it in `gotchas.md`: this kit's filing stages are for limited companies.

## Step 2 — Discover (no questions)

From **Companies House** (`/company/<number>` and its filing history; API or public pages):

| Fact | Where it comes from | Used for |
|---|---|---|
| Registered name, status, incorporation date, company type | profile | `entity.json`; stop if dissolved |
| CIC or not | company type / name ends "CIC" / CIC filings | `cic`; adds the CIC34 stage |
| Registered office, SIC codes | profile | records; SIC hints at VAT and stock |
| Accounting reference date | profile | year end |
| Next accounts due, next confirmation statement due, anything overdue | profile | `obligations.json` (source `ch`) |
| Directors, PSCs | officers / PSC lists | who approves. One current director: pre-fill it and fold it into the confirm step. Several: ask "which of these is you?" |
| **Parent company** (a PSC that is itself a company) | PSC list | record it in `entity.json` and `gotchas.md`: the company may be in a group, and group size can rule out micro-entity accounts. Check the parent's own filings |
| Former names | profile | trading names to search for on the web |
| Last accounts: made-up date and type (micro, dormant, small) | filing history | `accounts_basis`; whether there's history to bring in |
| Share capital | statement of capital in the incorporation document or the latest confirmation statement "with updates" (filing history, PDF) | `share_capital` with its source; `fetch_prior_year.py` needs it, because micro accounts tag only total equity |
| **Last filed accounts document** | filing history → view PDF / document API | prior-year figures, opening balance sheet, average employees (payroll hint), accountant's name if stated. The public "View PDF" link redirects to a URL that expires in about 60 seconds: fetch it with a shell (`curl -L`) or the document API. If neither works, don't ask for it at setup; ask for the PDF only when the year-end or rebuild stage needs prior figures |
| Charges (secured loans) | charges list | gotchas; loan to account for |

**Derived HMRC dates** (`obligations.json`, source `derived`): CT600 due 12 months after the period end; corporation tax payment due 9 months and 1 day after the period end. Label these *derived*, not confirmed. HMRC has no public API to read them back.

From the **web** (if the agent can browse):

- The company's **website**: what it sells, trading name, contact details. Search the registered name, former names and the name with common shop domains (`.store`, `.shop`, `.co.uk`, `myshopify.com`). A same-name company abroad is **not** a match: check the site names the company or its number.
- **Payment platforms in use:** checkout pages and footers (Stripe, Shopify, PayPal, SumUp, Square). Each one found is an API data source; pre-fill it in the batch below.
- **VAT number** printed on the site or invoices. If found, check it on gov.uk "Check a UK VAT number" and store only the last 4 digits.
- Charity register entry, if the name suggests one.

Record every value with its source. If something can't be found, leave it empty rather than guessing.

## Step 3 — Show and confirm (one message)

```
Here's what I found for <NAME> (<number>), from Companies House and your website:
  Year end <dd Month> · next accounts due <date> · confirmation statement due <date>
  Directors: <names> · last accounts: <type>, made up to <date>
  Takes payments through: <platforms found>  · VAT: <found / not found>
Is this you, and is it right? (Correct anything in your own words.)
```

## Step 4 — The one batch of questions (pre-filled)

Ask only these, in one message, each with the best guess already filled in:

1. **Which director are you?** (list from Companies House)
2. **Where does the money move?** Banks and cards by name, plus the payment platforms found: "I found Stripe on your site. Any others?"
3. **Do you use accounting software?** (Xero / FreeAgent / QuickBooks / none). If yes, it becomes a data source, not a requirement.
4. **VAT registered? Payroll?** Pre-filled from what was found (VAT number on site; employees in the last accounts).
5. **Who filed last year's accounts and tax return?** (you / an accountant / not filed yet). This decides whether past years need bringing in line (stage 80).

That's the whole intake. Anything else is asked later, at the step that needs it.

## Step 5 — Write the books

- `books/<id>/entity.json` from `engine/templates/entity.json`: confirmed facts, connectors, and `discovered` with sources.
- `books/<id>/obligations.json`: Companies House dates (`source: ch`) plus derived HMRC dates (`source: derived`).
- `books/<id>/status.json`: summary plus *waiting* items (`on`: the user or the agent), each with a `link` where there's a page to open.
- `books/<id>/gotchas.md`: anything unusual (charges, overdue filings, a setup this kit doesn't cover).
- Check each JSON file parses. `validate.py` checks bank lines, so run it after Step 6.

## Step 6 — First data in, by the easiest route per account

For each bank, card and payment platform, open its guide in `engine/reference/banks/`. **If there's no guide, research the provider (its own help pages first), write one to the shape in `engine/reference/banks/README.md`, then use it.** Offer the routes easiest first:

- **API** (for example Starling, Stripe): walk the user through making a **read-only** key and putting it in their own secret store (environment variable or OS keychain). Never paste it into chat or a file in the repo.
- **Accounting platform feed:** read through the platform's API if the user already has one.
- **Statement:** give the exact export steps and dates needed (since the last year end), and say which format is best (CSV with balance).

Prove each account's balance before calling it done. Payment-platform payouts are **transfers** to the bank, never income.

## Step 7 — Summary for the director (one screen)

What's set up · the deadline calendar (next 12 months) · what the agent does each month · **what's waiting on you**, with links. End with the next action and its date.

---

## Edge cases

- **Nothing on Companies House** (sole trader, partnership): say so, record it, stop the filing stages. Bookkeeping can still run.
- **A payment or filing deadline within 30 days whose status isn't known** (often the corporation tax payment, 9 months and 1 day after the year end, which nothing public confirms): put it at the very top of the summary, with the date moved to the previous working day if it falls on a weekend, and ask whether it's done before anything else.
- **Overdue filings:** list them first in the summary, with the penalty position. Don't start a filing without the director's approval.
- **Dormant company:** record it. Filing is the dormant-accounts route, not this kit's trading-accounts stages.
- **The agent can't browse the web:** use the Companies House public pages if reachable. Otherwise ask the user for the company number and continue. Say which facts are unconfirmed.
- **More than one company:** run this stage once per company. Shared directors are noted in each `entity.json`.

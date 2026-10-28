# 50_year_end — year-end accounts (contract)

**Goal:** from the year's money records to draft micro-entity accounts the director can approve, with every figure proven and every judgement call decided by the director.
**Covers:** a small UK limited company filing **FRS 105 micro-entity** accounts, with or without accounting software. If the last accounts or the company's size point to small (FRS 102 1A), say so and stop: that route isn't in this kit yet. **Having a parent company doesn't stop micro-entity accounts by itself:** a subsidiary can file them if the group as a whole (the parent plus all its subsidiaries) stays within the micro limits (turnover up to £1m, balance sheet up to £500k, up to 10 employees, from April 2025). A company that *has* subsidiaries and must prepare group accounts can't. Ask the director for the group's figures if unsure, and record the answer in `gotchas.md`.
**Trigger:** the year end has passed, or the director asks for the accounts. Needs `00_setup` done.
**Done means:** every account for the year passes `engine/scripts/validate.py <id>`; `books/<id>/filed/<FY>/trial_balance.csv` balances; `period.json` holds the draft figures; the director has a one-page draft and has decided every judgement call. Hand over to `60_filing`.

**The split:** the agent does the reading, recording, proving, cross-checking and drafting. The director downloads what needs their login, explains what only they know, decides the judgement calls, and approves. Each step says whose it is.

---

## 0. Check nothing is filed already — agent (`fetch_prior_year.py` stops if this year's accounts are on the register)

Look at the company's Companies House filing history for accounts made up to this year end. If they're there, say so and stop: filing again puts a second set on the public register. Ask the director whether the CT600 went in too. HMRC offers no public check, so only the director (TinyTax or HMRC online) can confirm it.

## 1. Collect the year's records — agent asks, director downloads

For every account in `entity.json` → `bank_accounts`, open its guide in `engine/reference/banks/` and ask for exactly what's missing: which account, which dates (first to last day of the financial year), which format (API pull > CSV with balance > PDF). API accounts are pulled by the agent; nobody downloads anything for them.

Work out each file's period from its **contents**, not its filename. A transaction export usually has **no balances**, so ask for at least one formal statement per card (it shows "previous balance / new balance").

## 2. Set up the chart of accounts — agent, once

Copy `engine/templates/account_map.json` to `books/<id>/accounts/account_map.json`, replace each `<placeholder>` name with the real account's name (delete the ones the company doesn't have), and add an account for each bank, card and platform (090–099) plus anything the lines need. Every line must carry a code from this chart; `validate.py` fails one that doesn't.

## 3. Record every line — agent

**Count each transfer once.** A move between two of the company's own accounts appears on both statements. Code each side to the *other* account's code (a card repayment on the bank is coded 095; the same payment on the card is coded 090), and build the trial balance from each account's **closing balance** plus the non-transfer lines. Never post both sides as income or cost. Pots and sub-accounts are accounts in their own right: a main account's running balance excludes what's in its pots.

Write each line with `python3 engine/scripts/books_io.py append <id> <account> <lines.json>`: date, counterparty, amount, running balance, account code, and a note saying why. It masks account and card numbers and refuses duplicates. Platform sales (Shopify, PayPal, Stripe and similar) take one of two routes; never both. **Simple route (no platform statements):** code each payout in the bank to sales (200); the platform's yearly summary (step 6) lets `build_tb.py` add the fees back so turnover is the platform's figure. **Full route (platform statements as their own account):** the platform gets its own account and lines, and a payout to the bank is a transfer between the two, never income.

## 4. Prove nothing is missing or doubled — agent

- **Bank:** opening + every line = closing, and every running balance agrees on the way.
- **Card without balances:** start from one statement balance and roll forwards and backwards. The list is complete only if it lands on every other statement's balance to the penny. That also gives the opening balance when early statements are missing.
- **Between accounts:** each transfer appears on both sides. A card repayment missing from the bank was paid from somewhere else, which usually means the director paid it.
- **Year-end balances without a statement file** (a savings pot, PayPal, Wise, the director's loan, stock, accruals): get each from a statement or the director and record it in `inputs.json` → `closing_balances.<code>` with its source. `build_tb.py` fails a balance with no source, or one that doesn't match the books.
- Run `validate.py <id>`. Don't continue on a failure.

## 5. Ask about anything unclear — agent asks, director answers

Group unclear lines and ask short, specific questions, never "explain your spending". For example: "Was this card the company's or yours?" or "Was this payment to your personal card a repayment to you?" Write each answer into the line's note.
**A cost that wasn't the company's isn't ignored:** the company paid it, so it is recorded against the director's loan account (code 835). The money left the company, so the books still have to add up.

## 6. Sales and fees — agent

If the platform gives only a yearly summary (no API), record it as one line per figure in the platform's account (gross sales, refunds, fees, payouts to the bank as transfers), with the summary file as the source. Take sales from the sales platform (orders, refunds, shipping), not from the bank: bank receipts are sales *after* fees. Fees = gross sales − amounts received, once you've checked that no sales straddle the year end. Record the summary in `books/<id>/sales/<FY>_summary.json` with a `totals` block: `total_sales` (the platform's sales including shipping, after refunds), `received_in_bank` (payouts that reached the bank) and `balances_at_year_end` (what was left in each platform, with its source). `build_tb.py` works out the fees and grosses the sales up itself, and fails if `received_in_bank` doesn't equal the payouts in the bank lines. Don't add the fees as an adjustment.

## 7. Start from last year — agent fetches, director explains

- Run `python3 engine/scripts/fetch_prior_year.py <id> <FY>`, then again with `--write`. It finds last year's accounts on the public register, saves the filed document and records net assets, share capital (from `entity.json`) and the profit and loss reserve in `inputs.json` → `prior_year`. If it says the accounts were filed on paper, or it can't reach Companies House, get last year's filed accounts from the director and save them, or a record of their figures with the document they came from, in `books/<id>/filed/<last FY>/`. This year's opening position must equal last year's closing one. Record them in `inputs.json` → `prior_year` (step 9); `build_tb.py` stops without them.
- **Can't get them? Stop and ask the director** for the PDF or the Companies House link. Never assume opening balances or work them out as a balancing figure: every figure in the accounts depends on them.
- Check last year against the books. A cost last year already counted as owed isn't this year's cost when it's paid. Something last year left out (for example card debt) is corrected through reserves, without refiling.
- First year of trading: there's no prior year. Opening balances are nil apart from share capital.
- Ask the director only about figures the books can't explain.
- A correction to last year that's made through reserves may still change the tax: a prior-year adjustment can be taxable or deductible in the year it's recognised. Work out its tax effect and tell the director before filing.

## 8. Judgement calls — agent explains, director decides

For each one, give the choice, its effect on profit and tax, and what it needs. Record the director's answer in `inputs.json` → `accounts.decisions.<call>` as `{"answer": "...", "decided_by": "director", "date": "YYYY-MM-DD"}`. **`build_accounts.py` stops until every call has one.** Don't answer for the director, and don't record an assumption as their decision: if you can't ask, stop and list the questions.

| Call | What to explain |
|---|---|
| Closing stock (`closing_stock`) | What's on hand at the year end and why it changes profit. Nil if goods are sent only after sale |
| Use of home (`use_of_home`, HMRC flat rate £6/week) | Only if the director genuinely works from home. Record `"weeks"` (0 if none; "all year" in a 12-month period is 52); the script posts £6 × weeks as a cost, owed to the director |
| Business mileage (`mileage`, 45p/mile, 25p over 10,000) | Needs a mileage log. Record `"miles"` (0 if none); the script posts the amount, owed to the director |
| Accruals (`accruals`) | Costs for the year paid after the year end (for example the accounts fee). Last year's accrual paid at a slightly different amount: release the difference to the same cost account as an adjustment, `decided_by: agent`, and tell the director |
| Going concern (`going_concern`) | If liabilities exceed assets, what signing confirms (usually that the director won't demand their loan back ahead of other creditors) |
| Trading losses brought forward (`trading_losses_bf`) | Only from the company's own earlier trading years: last year's CT600 shows them. If last year's reserves were in deficit and the answer is nil, the draft flags it |
| Associated companies (`associated_companies`) | Other companies under the same control, such as a parent or sister company. A dormant company or a passive holding company (no trade, only holds shares) doesn't count. They share the tax-rate limits |

## 9. Draft the accounts — agent

Keep the year-end inputs in `books/<id>/filed/<FY>/inputs.json`: `period_start` and `period_end`; `prior_year` (the file holding last year's accounts and their share capital, profit and loss reserve and net assets as filed, or `{"first_year": true}` when the period starts on the incorporation date); opening balances from last year's accounts (for codes without their own bank-line files), `retained_earnings_bf_filed`: last year's profit and loss reserve after any correction, signed debit-positive (a reserve of 134 in credit less a 236.34 correction is `102.34`), which must agree with `accounts.prior_period_adjustment`, and the adjustments (use of home, accruals, stock, platform fee gross-up and so on), each with who decided it. Give every bank-line account its `ledger_code` in `entity.json`. Then run `python3 engine/scripts/build_tb.py <id> <FY>`. It counts transfers once, checks both sides of every transfer agree, checks the opening position matches last year's accounts, and checks debits = credits. Fix every FAIL, then rerun with `--write`. Generate everything from the books; never hand-edit a figure, so the draft can always be rebuilt and checked.

- `books/<id>/filed/<FY>/trial_balance.csv`, written by `build_tb.py --write` (`line_order, source_code, source_name, debit, credit`).

Then add the `accounts` block to `inputs.json` (average employees including directors, trading losses brought forward, associated companies, any prior-year correction with its tax effect, any tax adjustments; field list at the top of the script) and run `python3 engine/scripts/build_accounts.py <id> <FY>`. Every account in the chart needs a `class` (see `classes` in the chart). Fix every FAIL, then rerun with `--write`. It writes, in `books/<id>/filed/<FY>/`:

- `accounts.json`: profit and loss, the micro-entity balance sheet with last year's column, and the corporation tax computation, in the shape the filing software takes.
- `period.json` with the headline figures and `"match_status": "draft"`. Decisions you record in its `notes` are kept on every rerun.
- `draft_accounts.md`: the one-page draft for the director (result, balance sheet, proof that opening reserves + result = closing reserves, director's loan, points to decide, tax). Give the director the full path the script prints and how to open it, show it to them, and explain the "why" behind the result in your own words alongside it. Then run `python3 engine/scripts/build_dashboard.py <id>` and give them that path too: `books/<id>/dashboard.html` shows the year, money in and out by month, what's due and what's waiting, in their browser. Rebuild it whenever the books change.

If tax is due, the script says so and stops: add the tax charge as an adjustment (debit the tax account, credit 830), rerun `build_tb.py --write`, then rerun it. Fixed assets (capital allowances) and periods longer than 12 months aren't covered yet: the script stops, and the director needs an accountant for that year.

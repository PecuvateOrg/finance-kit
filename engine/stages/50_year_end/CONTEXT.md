# 50_year_end — year-end accounts (contract)

**Goal:** from the year's money records to draft micro-entity accounts the director can approve, with every figure proven and every judgement call decided by the director.
**Covers:** a small UK limited company filing **FRS 105 micro-entity** accounts, with or without accounting software. If the last accounts or the company's size point to small (FRS 102 1A) or a group, say so and stop: that route isn't in this kit yet.
**Trigger:** the year end has passed, or the director asks for the accounts. Needs `00_setup` done.
**Done means:** every account for the year passes `engine/scripts/validate.py <id>`; `books/<id>/filed/<FY>/trial_balance.csv` balances; `period.json` holds the draft figures; the director has a one-page draft and has decided every judgement call. Hand over to `60_filing`.

**The split:** the agent does the reading, recording, proving, cross-checking and drafting. The director downloads what needs their login, explains what only they know, decides the judgement calls, and approves. Each step says whose it is.

---

## 0. Check nothing is filed already — agent

Look at the company's Companies House filing history for accounts made up to this year end. If they're there, say so and stop: filing again puts a second set on the public register. Ask the director whether the CT600 went in too. HMRC offers no public check, so only the director (TinyTax or HMRC online) can confirm it.

## 1. Collect the year's records — agent asks, director downloads

For every account in `entity.json` → `bank_accounts`, open its guide in `engine/reference/banks/` and ask for exactly what's missing: which account, which dates (first to last day of the financial year), which format (API pull > CSV with balance > PDF). API accounts are pulled by the agent; nobody downloads anything for them.

Work out each file's period from its **contents**, not its filename. A transaction export usually has **no balances**, so ask for at least one formal statement per card (it shows "previous balance / new balance").

## 2. Set up the chart of accounts — agent, once

Copy `engine/templates/account_map.json` to `books/<id>/accounts/account_map.json` and add an account for each bank, card and platform (090–099) plus anything the lines need. Every line must carry a code from this chart; `validate.py` fails one that doesn't.

## 3. Record every line — agent

**Count each transfer once.** A move between two of the company's own accounts appears on both statements. Code each side to the *other* account's code (a card repayment on the bank is coded 095; the same payment on the card is coded 090), and build the trial balance from each account's **closing balance** plus the non-transfer lines. Never post both sides as income or cost. Pots and sub-accounts are accounts in their own right: a main account's running balance excludes what's in its pots.

Write each line with `python3 engine/scripts/books_io.py append <id> <account> <lines.json>`: date, counterparty, amount, running balance, account code, and a note saying why. It masks account and card numbers and refuses duplicates. Payment-platform lines (Stripe and similar) go in their own account. **A payout to the bank is a transfer, never income**; sales are counted once, from the platform.

## 4. Prove nothing is missing or doubled — agent

- **Bank:** opening + every line = closing, and every running balance agrees on the way.
- **Card without balances:** start from one statement balance and roll forwards and backwards. The list is complete only if it lands on every other statement's balance to the penny. That also gives the opening balance when early statements are missing.
- **Between accounts:** each transfer appears on both sides. A card repayment missing from the bank was paid from somewhere else, which usually means the director paid it.
- Run `validate.py <id>`. Don't continue on a failure.

## 5. Ask about anything unclear — agent asks, director answers

Group unclear lines and ask short, specific questions, never "explain your spending". For example: "Was this card the company's or yours?" or "Was this payment to your personal card a repayment to you?" Write each answer into the line's note.
**A cost that wasn't the company's isn't ignored:** the company paid it, so it is recorded against the director's loan account (code 835). The money left the company, so the books still have to add up.

## 6. Sales and fees — agent

If the platform gives only a yearly summary (no API), record it as one line per figure in the platform's account (gross sales, refunds, fees, payouts to the bank as transfers), with the summary file as the source. Take sales from the sales platform (orders, refunds, shipping), not from the bank: bank receipts are sales *after* fees. Fees = gross sales − amounts received, once you've checked that no sales straddle the year end. Record the summary in `books/<id>/sales/<FY>_summary.json`.

## 7. Start from last year — agent fetches, director explains

- Get last year's filed accounts from Companies House (`00_setup` notes how to fetch the document). This year's opening position must equal last year's closing one.
- Check last year against the books. A cost last year already counted as owed isn't this year's cost when it's paid. Something last year left out (for example card debt) is corrected through reserves, without refiling.
- First year of trading: there's no prior year. Opening balances are nil apart from share capital.
- Ask the director only about figures the books can't explain.
- A correction to last year that's made through reserves may still change the tax: a prior-year adjustment can be taxable or deductible in the year it's recognised. Work out its tax effect and tell the director before filing.

## 8. Judgement calls — agent explains, director decides

For each one, give the choice, its effect on profit and tax, and what it needs. Then record the director's decision in `period.json` → `notes`.

| Call | What to explain |
|---|---|
| Closing stock | What's on hand at the year end and why it changes profit. Nil if goods are sent only after sale |
| Use of home (HMRC flat rate, £6/week) | Only if the director genuinely works from home. A cost to the company, tax-free to the director, credited to their loan account |
| Business mileage (45p/mile) | Needs a mileage log |
| Accruals | Costs for the year paid after the year end (for example the accounts fee) |
| Going concern | If liabilities exceed assets, what signing confirms (usually that the director won't demand their loan back ahead of other creditors) |
| Losses brought forward | Only from the company's own earlier trading years. Ask if unknown |

## 9. Draft the accounts — agent

Keep the year-end inputs in `books/<id>/filed/<FY>/inputs.json`: opening balances from last year's accounts (for codes without their own bank-line files), last year's retained earnings as filed (after any correction), and the adjustments (use of home, accruals, stock, platform fee gross-up and so on), each with who decided it. Give every bank-line account its `ledger_code` in `entity.json`. Then run `python3 engine/scripts/build_tb.py <id> <FY>`. It counts transfers once, checks both sides of every transfer agree, checks the opening position matches last year's accounts, and checks debits = credits. Fix every FAIL, then rerun with `--write`. Generate everything from the books; never hand-edit a figure, so the draft can always be rebuilt and checked.

- `books/<id>/filed/<FY>/trial_balance.csv`, written by `build_tb.py --write` (`line_order, source_code, source_name, debit, credit`).
- Profit and loss, the micro-entity balance sheet (fixed assets, current assets, creditors within one year, share capital, profit and loss reserve), the director's loan account, any prior-year correction, and a proof that opening reserves + result = closing reserves.
- `books/<id>/filed/<FY>/period.json` with the headline figures and `"match_status": "draft"`.
- A one-page draft for the director in plain words: what the year's result was, why, and what's owed to or by them.

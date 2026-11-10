# Checks every draft passes before the director sees it

1. Every account's lines prove from opening to closing balance (`bank_to_books.md`).
2. Every transfer appears on both sides, once each.
3. Every year-end balance without a statement has a recorded source.
4. Opening position equals last year's filed closing position.
5. Debits equal credits in the trial balance.
6. Opening reserves + this year's result = closing reserves.
7. Every judgement call has the director's decision recorded, with the date.
8. The tax worked out by the engine equals the tax the filing tool calculates, before anything is submitted.

**Never hand-edit a figure.** Everything is generated from the books and the recorded decisions, so the draft can always be rebuilt and checked. **On any failure, stop and fix the cause**; never carry on with a known difference or invent a balancing figure.

These checks are run by `engine/scripts/validate.py` (1), `build_tb.py` (2–5) and `build_accounts.py` (6–7); step 8 is in `60_filing`.

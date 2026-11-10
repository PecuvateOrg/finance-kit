# Double entry and the chart of accounts

- **Every transaction touches two accounts, and the two sides are equal.** Money in the bank goes up (debit) and something else balances it: a sale (credit), a loan from the director (credit), and so on. Debits always equal credits; a trial balance that doesn't balance has an error, never a rounding difference to absorb.
- **Every line carries one account code from the chart.** The chart (`engine/templates/account_map.json`) lists every account the company uses, each with a class (asset, liability, equity, income, cost) that decides where it lands in the accounts. Add an account for each real bank, card and platform; delete placeholder accounts the company doesn't have.
- **Each bank, card, pot and sub-account is an account in its own right.** A main account's balance excludes what's in its pots.
- **Nothing the company paid disappears.** A cost that wasn't the company's (the director's personal spending on a company card) is not ignored: the money left the company, so it is recorded against the director's loan account, which the director then owes back. The books still have to add up.
- **Money owed to or by the director lives in one account, the director's loan account**, whether it arose from personal spending, expenses paid personally, or flat-rate claims (`../rules/expense_rates.md`).
- **The profit and loss reserve carries the history.** Last year's closing reserve is this year's opening reserve; this year's result moves it to the closing figure.

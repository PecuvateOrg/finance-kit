# Getting from the bank to the books, and proving it

## Prove every account
- **Bank:** opening balance + every line = closing balance, and every running balance agrees on the way.
- **Card without balances:** start from one statement balance and roll forwards and backwards. The list is complete only if it lands on every other statement's balance to the penny. That also gives the opening balance when early statements are missing.
- **Work out each file's period from its contents, never its filename.** A transaction export usually has no balances, so get at least one formal statement per card.
- **Year-end balances without a statement** (a savings pot, a payment platform, the director's loan, stock, accruals): each needs a source (a statement or the director's confirmation) recorded with it. A balance with no source isn't used.

## Count each transfer once
A move between two of the company's own accounts appears on both statements. Each side is coded to the *other* account (a card repayment in the bank is coded to the card; the same payment on the card is coded to the bank), and the books are built from each account's closing balance plus the non-transfer lines. Never count both sides as income or cost.
- Each transfer appears on both sides. A card repayment missing from the bank was paid from somewhere else, which usually means the director paid it (director's loan).

## Payment platforms (Shopify, PayPal, Stripe and similar)
- **A payout to the bank is not a sale.** It is sales after fees and refunds. Take sales from the platform (orders, refunds, shipping), and fees = gross sales − amounts received, once you've checked no sales straddle the year end.
- Two ways to record them, **never both**:
  - **Simple:** each payout in the bank is coded to sales, and the platform's yearly summary adds the fees back so turnover is the platform's figure.
  - **Full:** the platform is an account of its own with its own lines; a payout to the bank is a transfer between the two, never income.

## When something is unclear
Ask short, specific questions about groups of lines ("Was this card the company's or yours?"), never "explain your spending", and write each answer into the line's note.

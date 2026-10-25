# Barclaycard Commercial (business credit card)

checked: 2026-10-21. **Routes not yet researched**; only the PDF format below has been seen.
type: card
routes (easiest first): manual_export (assumed) | platform_feed (exists for Xero for at least one Barclaycard product)

## Route 1 — Transaction export (CSV) or monthly PDF statement

A CSV export **with running balances** is best: use it directly. Without balances, it needs at least one PDF statement to prove the balance (roll forwards and backwards from it).

### Monthly PDF statement

Download each monthly statement from Barclaycard's online servicing and hand it to the agent. The statement extractor reads the PDF into `books/<entity>/bank/<card>/`.

## To research

Whether online servicing offers CSV export or emailed statements, and which accounting platforms take a feed for this card.

## Format notes

- The card balance is a liability: negative = owed. Repayments from the bank account are **transfers** between the two accounts, never costs. The costs are the card's own lines.

# Reference (Layer 3) — router

Open a file here only when a stage contract names it or the task needs it. Never load a whole folder.

| Folder | Holds | Changes | Trust it how |
|---|---|---|---|
| `method/` | How the books are kept and proved: double entry, matching bank to books, year-end adjustments, the checks every figure passes | Practically never | Follow it as written |
| `rules/` | Law and tax: rates, size limits, deadlines, and what each filing (accounts, CT600, CIC34, confirmation statement, payroll year end) must contain, tool-neutral | Usually once a year (April, the Budget) | Every rule carries `effective from` and `checked`. If the date being worked on is past a rule's `review by`, check the GOV.UK source before relying on it |
| `tools/` | Each platform's short guide: what it's for, its official help pages, which prepared figures it asks for, how to confirm it worked. Prices in `tools/prices.json` | Any time, without notice | Thin on purpose. Read the vendor's own help page or the screen in front of the user for the clicks; if the guide disagrees, the vendor wins and the guide gets fixed |

**Where a new fact goes:** true whatever the year and whatever the tool → `method/`. True because a law or HMRC says so → `rules/` with its dates. True only for one product → `tools/`. True only for one company → `books/<id>/gotchas.md`, never here.

**The engine prepares for the filing, not for the tool.** Stages produce every figure and answer a filing needs (from `rules/`); a tool guide only says where in that tool each one goes.

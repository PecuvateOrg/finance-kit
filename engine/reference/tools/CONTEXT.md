# Tools — short guides to each platform (changes any time)

What `engine/scripts/pick_platforms.py` may recommend, and how to use each one. Prices live only in `prices.json` (ex VAT unless marked; `null` = not recorded, the picker says "check"); never copy a price into a guide.

| Folder / file | Holds |
|---|---|
| `banks/` | Getting transactions out of each bank, card and payment platform (`banks/README.md` has the shape) |
| `filing/` | Filing software: `tinytax.md` (micro accounts + CT600, API/MCP), `simplecompanytax.md` (CIC package ZIP) |
| `companies_house/` | Filing direct with Companies House: `package_upload.md` (CIC accounts), `confirmation_statement.md` |
| `payroll/` | `primo.md` (free up to 10 staff, no API). Xero Payroll and Staffology: no guide yet, write one when first recommended |
| `chat_apps.md` | What each chat app's code sandbox can do (Claude.ai, ChatGPT, Gemini), for `PREPARE-ONLY.md` |
| `prices.json` | Every platform's price, checked monthly against the vendor page |

**Who the engine is for:** companies limited by shares or guarantee, CICs, and unincorporated clubs or associations that are **not charities**, at micro size. Registered charities, CIOs and charitable companies are out of scope.

**How a platform is chosen:** the cheapest that does the job, preferring one the user's AI can drive (MCP or API); a cheaper manual option is shown as the alternative. The user opens and pays for every platform themselves.

**A tool guide is short:** what it's for · official help pages · which prepared figures it asks for (from `../rules/`) · how to confirm it worked · `checked` date. The clicks come from the vendor's help page or the user's screen at the time; if the guide and the vendor disagree, the vendor wins and the guide is fixed. No guide for a tool the user already has → research it (vendor's own pages first), write one in this shape, then use it.

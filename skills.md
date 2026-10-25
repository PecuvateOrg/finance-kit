# Skills / stages

This kit uses **stage contracts** rather than agent-specific skills, so it works with any agent: each process is a markdown file your agent reads and follows.

| Say | Stage |
|---|---|
| "set me up" | `engine/stages/00_setup/CONTEXT.md` |
| "do the year-end accounts" | `engine/stages/50_year_end/CONTEXT.md` |
| "file the accounts and tax return" | `engine/stages/60_filing/CONTEXT.md` |
| "how do I get my bank statements?" | `engine/reference/banks/<your bank>.md` |
| "check the books" | `python3 engine/scripts/validate.py <company>` |

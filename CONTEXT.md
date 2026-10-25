# Finance kit — map (Layer 1)

```
CLAUDE.md  AGENTS.md  GEMINI.md   agent instructions (AGENTS/GEMINI point at CLAUDE.md)
NON-NEGOTIABLES.md                rules that hold in every stage
START-HERE.md  README.md         for the person: what this is, and "set me up"
agent-roles.md  skills.md         who does what; what to say for each stage
memory.md  DEVLOG.md              your running state and history (created on your machine; never committed)

engine/                           shipped with the kit; replaced on upgrade; never holds your data
  stages/NN_name/CONTEXT.md       one contract per process (00_setup first)
  reference/banks/                how to get transactions out of each bank / card / payment platform
  reference/filing/               how the filing software works (TinyTax)
  templates/                      blank entity.json, account_map.json (chart of accounts)
  scripts/                        books_io.py (writes lines safely), validate.py (checks bank-line files),
                                  build_tb.py (builds and checks the trial balance)

books/                            YOUR data: private, never shipped
  <entity>/entity.json            company facts, connectors, what was discovered and from where
  <entity>/obligations.json       every deadline, with its source (Companies House / derived / you)
  <entity>/status.json            what's waiting, on whom
  <entity>/bank/<account>/<FY>.csv  one file per account per financial year
  <entity>/gotchas.md             anything unusual about this company
```

| Stage | Status |
|---|---|
| 00_setup | written; tested with a fresh agent on a real company (discovery + confirm) |
| bank lines (statements, API) | `books_io.py` + `validate.py` shipped; bank-specific pull scripts not yet packaged (the agent reads the statement itself) |
| 50_year_end, 60_filing | written from a live end-to-end run (accounts + CT600 accepted, 2026-10) |

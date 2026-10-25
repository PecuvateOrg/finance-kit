# Finance kit

An AI agent keeps a small UK limited company's books, prepares its year-end micro-entity accounts and corporation tax return (CT600), and files both through filing software once the director approves.

**For the person:** read `START-HERE.md`. In short: download this kit, open the folder with your AI agent, and say "set me up".

## What it does

| Stage | What happens | Who does what |
|---|---|---|
| `00_setup` | Finds your company on Companies House and the web, confirms it with you, asks only what it couldn't find | Agent finds; you confirm |
| Bank lines | Gets every account's transactions in the easiest way your bank allows (API, or a monthly statement download) | Agent pulls or asks; you download if needed |
| `50_year_end` | Records and proves every line, asks about anything unclear, drafts the accounts | Agent drafts; you explain and decide |
| `60_filing` | Dry run, your approval, then files with Companies House and HMRC and keeps the proof | Agent files; you approve |

## Requirements

- An AI coding agent that can read files, run Python 3 and browse the web (Claude Code, Codex CLI, Gemini CLI or similar).
- Python 3 (standard library only) and git.
- For filing: your own TinyTax account (from £59 + VAT a year).

## Your data

Everything about your company lives in `books/`, which is **yours and private**. Keep it in a private repository or folder, never in a public one or a fork of this kit. Updates to the kit replace `engine/` only and never touch `books/`.

## Not covered (yet)

Sole traders and partnerships, VAT returns, payroll, groups, and small (FRS 102 1A) accounts. The agent will tell you if your company needs one of these.

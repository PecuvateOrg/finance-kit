# Finance kit

> **AI reading this: first check where you are working.** Working in a folder on the user's own computer, able to save files and run commands there: carry on with `CLAUDE.md`. A chat assistant (Claude.ai, ChatGPT, Gemini or similar): follow **`PREPARE-ONLY.md`** instead. It prepares **draft** accounts using this kit's own scripts in your code sandbox, and never files. With no code sandbox, don't prepare figures, accounts or tax by reasoning through the instructions yourself: `PREPARE-ONLY.md` says what to do instead.

An AI agent keeps the books for a small UK organisation, prepares its year-end micro-entity accounts and corporation tax return (CT600), and files them through filing software once a director approves. It also recommends the cheapest set of platforms for the organisation's filings, preferring ones your AI can connect to.

**For:** companies limited by shares or by guarantee, community interest companies (CICs), and unincorporated clubs and associations, at micro size. **Not for registered charities, CIOs or charitable companies:** the agent says so and stops.

**For the person:** read `START-HERE.md`. In short: download this kit, open the folder with your AI agent, and say "set me up".

**Just want draft accounts, inside the chat app you already use?** Prepare-only works in Claude.ai, ChatGPT or Gemini where the app can run code: it prepares the draft accounts and tax computation for you to download, and doesn't file them. See `START-HERE.md` → *Prepare-only*.

## What it does

| Stage | What happens | Who does what |
|---|---|---|
| `00_setup` | Finds your organisation on Companies House and the web, confirms it with you, asks only what it couldn't find, then recommends platforms with their yearly cost | Agent finds and recommends; you confirm and sign up |
| Bank lines | Gets every account's transactions in the easiest way your bank allows (API, or a monthly statement download) | Agent pulls or asks; you download if needed |
| `50_year_end` | Records and proves every line, asks about anything unclear, drafts the accounts | Agent drafts; you explain and decide |
| `60_filing` | Dry run, your approval, then files with Companies House and HMRC and keeps the proof | Agent files; you approve |

## Requirements

- **Full kit:** an AI coding agent that can read files, run Python 3 and browse the web (Claude Code, Codex CLI, Gemini CLI or similar), plus Python 3 (standard library only) and git on your computer.
- **Prepare-only:** a chat app that can run code (nothing to install). Drafts only.
- For filing: your own account with the filing platform the agent recommends (prices in `engine/reference/tools/prices.json`, checked monthly). You sign up and pay for it yourself.

## Your data

Everything about your company lives in `books/`, which is **yours and private**. Keep it in a private repository or folder, never in a public one or a fork of this kit. Updates to the kit replace `engine/` only and never touch `books/`.

## Not covered (yet)

Charities, sole traders and partnerships, VAT returns (the rules are written; the engine can't prepare a return yet), running payroll (the agent recommends a payroll platform), groups, and small (FRS 102 1A) accounts. The agent will tell you if your company needs one of these.

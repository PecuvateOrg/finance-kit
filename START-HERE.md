# Start here

> **AI agent reading this:** this page is for the person. Your instructions start in `CLAUDE.md` (or `AGENTS.md`).

This kit lets an AI agent on **your own computer** keep your company's books, prepare your year-end accounts and corporation tax return, and file them once you approve.

## One-time setup (about 15 minutes)

1. **Get your agent ready:** follow the step-by-step guide at **https://pecuvate.com/kits/** (VS Code, Git, an AI agent and its extension, an empty folder). It's the same for every kit listed there.
2. **This kit also needs Python 3:** on Windows install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH"; on a Mac it comes with Git's command line tools. Your agent can check it's there.
3. **With your empty folder open in VS Code, open the agent's chat panel** and paste (the kit's page, https://pecuvate.com/kits/finance/, fills in your company name and copies it for you):

   > Please clone https://github.com/PecuvateOrg/finance-kit into this folder, read its instructions, and set me up. My company is called `<your company name>`.

The agent downloads the kit, reads its instructions, finds your company's details itself (Companies House, your website, your last accounts), shows you what it found, and asks only for what it couldn't find, such as which bank you use. It then tells you the easiest way to get your bank statements in.

## What you'll do after that

- **Answer a few questions once.**
- **Get your bank lines in each month:** download a statement in a couple of clicks, or connect your bank once if it has an API. The agent tells you exactly what to do for your bank.
- **Approve the accounts** before they're filed, then say "approved, file".

## Good to know

- **Everything runs on your computer.** Your figures stay in the `books/` folder there; the people who made this kit never see them. Keep `books/` private: back it up to a **private** repository or folder, never a public one.
- **You stay in charge.** This is software, not an accountancy service and not tax advice. The agent prepares and checks; you, as director, are responsible for the accounts and returns, and nothing is filed without your approval.
- **Filing costs:** you'll need your own TinyTax account (from £59 + VAT a year) when it's time to file. The agent tells you when.

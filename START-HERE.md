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

## Prepare-only: draft accounts in the chat app you already use

No setup on your computer. Works where your chat app can run code (Claude.ai has it on by default; ChatGPT through data analysis; Gemini varies). You get draft accounts, the tax computation and a one-page summary to download. **Nothing is filed:** you file them yourself, or use the full kit above.

1. **ChatGPT only:** download the kit first: https://github.com/PecuvateOrg/finance-kit → *Code* → *Download ZIP*, and attach it to your message.
2. Paste:

   > Please read https://github.com/PecuvateOrg/finance-kit, follow its PREPARE-ONLY.md, and prepare draft year-end accounts for `<your company name>`.

3. Upload your bank statements when asked (CSV exports if your bank offers them) and last year's accounts if it can't find them.
4. **Download everything it gives you before you close the chat:** the chat's workspace is wiped afterwards. Keep the `books` zip: the full kit can carry on from it.

If your app can't run code, the agent tells you how to turn it on, or prepares the groundwork (your transactions sorted, and the questions it needs answered) without any figures.

## Good to know

- **It's signed.** Your agent checks the kit is genuine, unchanged since its makers signed it, before using it (`VERIFY.md`).
- **Everything runs on your computer.** Your figures stay in the `books/` folder there; the people who made this kit never see them. Keep `books/` private: back it up to a **private** repository or folder, never a public one.
- **You stay in charge.** This is software, not an accountancy service and not tax advice. The agent prepares and checks; you, as director, are responsible for the accounts and returns, and nothing is filed without your approval.
- **Filing costs:** during setup the agent recommends the cheapest platforms for your filings, with their yearly cost. You sign up and pay for each one yourself, when the agent says it's needed. Registered charities aren't covered.

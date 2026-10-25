# Start here

This kit lets an AI agent on **your own computer** keep your company's books, prepare your year-end accounts and corporation tax return, and file them once you approve.

## One-time setup (about 15 minutes)

1. **Install VS Code** (free) from https://code.visualstudio.com and open it.
2. **Choose an AI agent and sign up for it.** Any of these works:
   - **Claude Code**: an Anthropic account (claude.ai), with a Pro or Max plan or API credit
   - **Codex**: an OpenAI account (ChatGPT Plus or above)
   - **Gemini Code Assist**: a Google account
3. **Install its VS Code extension:** in VS Code open **Extensions** (the four-squares icon on the left), search for the agent's name, click **Install**, and sign in when it asks.
4. **Make an empty folder** for your company's books (for example `Documents/my-company-books`) and open it in VS Code (**File → Open Folder**).
5. **Open the agent's chat panel** and paste:

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

# Prepare-only: draft accounts inside a chat app

> **AI reading this:** follow this page when you are a chat assistant (Claude.ai, ChatGPT, Gemini or similar), not an agent working in a folder on the user's computer. It replaces `CLAUDE.md` for you. Read `NON-NEGOTIABLES.md` too: every rule there still applies, except the ones about filing, which you never do here.

**What you can do here:** prepare **draft** year-end accounts, the corporation tax computation and the director's one-page summary, using this kit's own scripts in your code sandbox. **What you never do here:** file anything, or keep the books between sessions. The user downloads the result; filing is done by hand or with the full kit (`START-HERE.md`).

## 1. Check you have a code sandbox — always first

Run this in your code tool:

```python
import sys; print(sys.version)
```

- **It prints a version (3.8 or later):** continue at step 2.
- **You have no code tool, or it fails:** don't prepare figures. Never add up, net off or work out tax yourself: a total you work out without running the scripts is exactly the mistake this kit exists to prevent. Tell the user plainly, then go to step 7.

## 2. Get the kit's files into the sandbox — as files, never retyped

The scripts must be the kit's own files. **Never rewrite a script from what you read on GitHub**: one changed character changes the accounts, and nobody would see it.

1. **Your sandbox can reach the internet:** download `https://github.com/PecuvateOrg/finance-kit/archive/refs/heads/main.zip` and unzip it.
2. **It can't** (ChatGPT's can't): ask the user to download that zip themselves (GitHub → *Code* → *Download ZIP*) and upload it to the chat, then unzip it.
3. **Check every file arrived unchanged**, from the kit folder:

```python
import hashlib, pathlib
bad = []
for line in open("SHA256SUMS"):
    if line.strip():
        digest, name = line.split(None, 1)
        f = pathlib.Path(name.strip())
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != digest:
            bad.append(name.strip())
print("OK, all files match" if not bad else f"STOP, changed or missing: {bad}")
```

Stop on anything but OK. This proves the files match the release's list. It does not prove the release is genuine: that needs the signature check in `VERIFY.md`, which a sandbox can't run. Say so to the user once.

## 3. Set up the company — agent asks, director answers

Work in a `books/` folder next to `engine/`. Follow `engine/stages/00_setup/CONTEXT.md` for `books/<id>/entity.json`, using your own web search for Companies House and the company's website. Skip the parts about filing platforms and logins.

## 4. Get the year's money in — director uploads, agent records

Ask for every bank, card and payment-platform account for the whole financial year. **Ask for CSV exports with a running balance first; PDF statements only if there's no CSV.**

Then follow `engine/stages/50_year_end/CONTEXT.md` steps 2 to 6. Two rules matter most here:

- **Copy figures exactly as the statement shows them.** Read the file with code where you can (CSV), not by eye.
- **Every account must pass `python3 engine/scripts/validate.py <id>` before anything else runs.** Its balance check proves each line against the statement's own running balances, so a misread or missing line fails it. A statement without running balances needs its opening and closing balance recorded with their source (`inputs.json` → `closing_balances`).

## 5. Last year's figures — agent finds, director confirms

Run `engine/scripts/fetch_prior_year.py` (step 7 of `50_year_end`). If your sandbox can't reach Companies House, it says so: ask the user to upload last year's filed accounts (the PDF from the Companies House filing history), and record the figures in `inputs.json` → `prior_year` with that document as the source. Never work out opening balances as a balancing figure.

## 6. Draft — agent runs the scripts, director decides

Follow `50_year_end` steps 8 and 9 exactly: the director decides every judgement call, then `build_tb.py` and `build_accounts.py` run with `--write`. Every FAIL is fixed, never worked around.

Then give the user:

- **The draft:** show `books/<id>/filed/<FY>/draft_accounts.md` in the chat and offer it as a download.
- **Everything to keep:** zip the whole `books/<id>/` folder and offer it as a download. **The sandbox is wiped when the chat ends**, so tell them this is the only copy. It is the same folder the full kit uses, so they can carry on there without starting again.
- **What's next:** these are drafts. To file, the director files by hand with Companies House and HMRC, or uses the full kit, which files them through the filing software.

## 7. No code sandbox: groundwork only, no figures

Tell the user that you can't run the kit's checks here, so you won't produce accounts or totals. Then do the work that needs no sums:

1. **Turning code on:** say whether their app can run code, and how to turn it on (`engine/reference/tools/chat_apps.md`). If it can't, point them to the full kit on their own computer (`START-HERE.md`).
2. **Read their statements** and list every line as the statement shows it, one line per transaction, in the columns of `engine/scripts/books_io.py` (date, counterparty, reference, amount, running balance, suggested account code with a note on why). **No totals, no subtotals and no net figures.**
3. **List what's missing** (accounts, months, last year's accounts) and **the director's questions** (`50_year_end` step 8).
4. **Give it all as one file to download.** The full kit or a later prepare-only session loads it with `books_io.py` and proves every line before using it.

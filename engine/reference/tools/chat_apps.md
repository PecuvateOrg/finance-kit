# Chat apps: can they run the kit? (prepare-only)

What `PREPARE-ONLY.md` relies on in each chat app. Facts from the vendors' own help pages, checked 2026-11-12. **Unknown means not stated by the vendor: find out in the app (`import sys; print(sys.version)`) rather than assume.** Re-check when a live test disagrees.

| | Claude.ai | ChatGPT | Gemini |
|---|---|---|---|
| Runs Python | Yes: "Code execution and file creation", on by default for Free, Pro and Max; on Team and Enterprise the organisation's owner decides | Yes: data analysis (Python in a notebook); plan limits vary | **Unknown in the current app.** A February 2024 note says Gemini Advanced can run Python snippets |
| Sandbox reaches the internet | Yes on personal plans (approved sources); off by default on Team and Enterprise | **No:** "cannot make external web requests" | Unknown |
| How the kit gets in | Download the GitHub zip, or the user uploads it | **The user uploads the GitHub zip** | A GitHub repository can be added as a code folder (up to 5,000 files, 100 MB). **An uploaded zip is limited to 10 files**, and the kit has more |
| Upload limit | 30 MB a file | Varies by plan | 100 MB |
| User downloads what the sandbox writes | Yes | Yes | Unknown |
| Python version | Unknown | Unknown | Unknown |
| Turn it on | Settings → Capabilities (personal plans: on already) | Built in where the plan includes data analysis | Unknown |

The kit's scripts need Python 3.8 or later and the standard library only (checked against the 3.8–3.11 grammar, 2026-11-12; not yet run on each app).

## Sources

- Claude: support.claude.com "Create and edit files with Claude", "Upload files to Claude"
- ChatGPT: help.openai.com "Data analysis with ChatGPT", "File Uploads FAQ"
- Gemini: support.google.com/gemini "Upload and analyse files in Gemini Apps"; gemini.google release notes (February 2024)

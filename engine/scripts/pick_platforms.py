"""Recommend the cheapest set of platforms that keeps an organisation's books and files its accounts and returns.

Usage:
  python3 engine/scripts/pick_platforms.py --type cic --turnover 40000 --assets 15000 --employees 2 [--vat] [--books xero] [--json]
  python3 engine/scripts/pick_platforms.py --type ltd --size micro

--type      ltd (company limited by shares) | clg (company limited by guarantee, not a charity) | cic |
            unincorporated (club, society, association, not a charity) | charity (any registered charity, CIO or
            charitable company: out of scope, the script says so and stops)
--size      micro | small | medium; or give --turnover/--assets/--employees (and --period-start) and the size is
            worked out from engine/reference/rules/company_size.json
--employees people on the payroll (0 = no payroll)
--vat       VAT-registered
--books     what the books are kept in today: none (default) | xero | <other name>

Prices come from engine/reference/tools/prices.json and size limits from engine/reference/rules/company_size.json,
never from this file. Platforms are recommended only:
the organisation opens and pays for each one itself. Prefers platforms the user's AI can drive (MCP or API); where a
cheaper manual option exists it is listed as the alternative.
"""
import argparse, json, sys
from pathlib import Path

REF = Path(__file__).resolve().parents[1] / "reference"
PRICES = json.loads((REF / "tools" / "prices.json").read_text())
SIZE = json.loads((REF / "rules" / "company_size.json").read_text())


def size_from(turnover, assets, employees, period_start="9999-12-31"):
    """Micro / small if 2 of the 3 limits are met; limits in force for a period starting on period_start."""
    rows = [r for r in SIZE["rows"]
            if (r["periods_starting_from"] or "") <= period_start < (r["periods_starting_before"] or "9999-99-99")]
    for band in ("micro", "small"):
        r = next(x for x in rows if x["band"] == band)
        if sum([turnover <= r["turnover"], assets <= r["balance_sheet"], employees <= r["employees"]]) >= 2:
            return band
    return "medium"


def annual(key, qty=1):
    p = PRICES["prices"][key]
    if p["gbp"] is None:
        return None
    v = p["gbp"] * (12 if p["per"] == "month" else 1) * qty
    return round(v * (1 + PRICES["vat_rate"]) if p["vat"] == "excl" else v, 2)


def line(job, platform, key, connect, how, qty=1, alt=None):
    return {"job": job, "platform": platform, "price_key": key, "gbp_year_incl_vat": annual(key, qty) if key else 0,
            "connect": connect, "how": how, "alternative": alt}


def pick(o):
    if o.type == "charity":
        return {"stop": "Registered charities, CIOs and charitable companies are not covered: their accounts, Charity "
                        "Commission returns and examination rules are different. Nothing is recommended."}
    size = o.size or size_from(o.turnover or 0, o.assets or 0, o.employees or 0, o.period_start)
    company = o.type != "unincorporated"
    out, gaps = [], []

    # Books
    if o.books == "xero":
        out.append(line("Books", "Xero (already in use)", "xero_ignite", "MCP + API",
                        "Keep it: the engine reads and posts through Xero's API."))
    elif o.books and o.books != "none":
        out.append(line("Books", f"{o.books} (already in use)", None, "check",
                        "Keep it if its API can export transactions; otherwise export CSVs for the engine."))
        gaps.append(f"No connector guide for {o.books} yet: research its API and write one before relying on it.")
    else:
        out.append(line("Books", "Kept by the engine (files on your computer)", None, "built in",
                        "Bank statements or bank exports in, coded and balanced by the engine. No subscription.",
                        alt="Xero, if you want bank feeds and invoicing in one app (monthly fee, MCP)."))

    # Payroll. The software cost only: wages, employer's NI and pension contributions are extra.
    if o.employees:
        if o.books == "xero":
            out.append(line("Payroll", "Xero Payroll", "xero_payroll", "API", qty=o.employees, how=
                            "Payslips, pension auto-enrolment and HMRC reports in the same app as the books.",
                            alt="Primo Payroll's free plan (no API: you run each pay day)."))
        elif o.employees <= 10:
            out.append(line("Payroll", "Primo Payroll Essentials (free plan)", "primo_essentials_free", "none",
                            "Free for up to 10 employees (leavers count): HMRC reports and emailed payslips; confirm "
                            "its pension auto-enrolment module on sign-up. No API, so you run each pay day and the "
                            "engine posts the totals from its report.",
                            alt="Staffology Payroll, if you want your AI to run payroll (open API, monthly fee). "
                                "HMRC Basic PAYE Tools is also free, but makes no payslips and does no pension work."))
        else:
            out.append(line("Payroll", "Staffology Payroll", "staffology_payroll", "API",
                            "Cloud payroll with an open API: payslips, pension auto-enrolment and HMRC reports."))
        if o.books != "xero":
            gaps.append("Payroll with an API costs a monthly fee (Staffology, Xero Payroll). The free options have none, "
                        "so a person runs each pay day.")
        gaps.append("Workplace pension: staff who qualify must be enrolled with a pension provider (e.g. NEST, no "
                    "employer fee). Wages, employer's National Insurance and pension contributions are not in these costs.")

    # Year-end filings
    if company:
        if size != "micro":
            gaps.append(f"A {size} company files small-company (FRS 102 1A) accounts. The filing tools below state "
                        "micro-entity only, so the accounts need different software; not covered yet.")
        if o.type == "cic":
            out.append(line("CT600 + accounts + CIC34", "SimpleCompanyTax", "simplecompanytax_cic", "none",
                            "Files the CT600 to HMRC and builds the package ZIP (accounts + community interest "
                            "report) from the engine's figures, which it can import from a CSV or Excel file.",
                            alt="TinyTax Solo, if you want your AI to file the CT600 itself (MCP + API); it adds "
                                "a second subscription, as the CIC package still needs SimpleCompanyTax."))
            out.append(line("CIC accounts filing", "Companies House package accounts upload", "ch_cic_package",
                            "none", "You upload the ZIP; CIC accounts cannot go through filing software."))
        else:
            out.append(line("Accounts + tax return", "TinyTax Solo", "tinytax_solo", "MCP + API",
                            "Micro accounts to Companies House and CT600 to HMRC in one subscription; your AI files them.",
                            alt="SimpleCompanyTax files both for less (no API: you import the engine's figures and "
                                "submit yourself)."))
        out.append(line("Confirmation statement", "Companies House (direct)", "ch_confirmation_statement", "none",
                        "You file it online once a year; the engine reminds you and pre-fills the answers.",
                        alt="TinyTax files it for £74 including the fee."))
    else:
        out.append(line("Year-end report", "Made by the engine", None, "built in",
                        "Income and spending report and balance sheet for members. Nothing is filed at Companies House."))
        gaps.append("If the club has taxable income (e.g. trading with non-members, interest over allowances) it must "
                    "tell HMRC and may get a CT600 notice. SimpleCompanyTax files a club's CT600 without accounts; "
                    "confirm the club must file before recommending it.")

    if o.vat:
        out.append(line("VAT returns (MTD)", "TinyTax MTD VAT", "tinytax_mtd_vat", "API",
                        "Quarterly VAT returns from the engine's figures."))
        gaps.append("VAT coding in the engine is not built yet: VAT returns need it first.")

    known = [x["gbp_year_incl_vat"] for x in out if x["gbp_year_incl_vat"] is not None]
    unknown = [x["platform"] for x in out if x["gbp_year_incl_vat"] is None]
    return {"type": o.type, "size": size, "lines": out, "total_gbp_year_incl_vat": round(sum(known), 2),
            "price_not_recorded": unknown, "gaps": gaps, "prices_checked": PRICES["checked"]}


def show(r):
    if "stop" in r:
        print(r["stop"]); return
    print(f"Recommended setup ({r['type']}, {r['size']}); prices checked {r['prices_checked']}\n")
    print("| Job | Platform | £ a year incl. VAT | Your AI connects by |\n|---|---|---:|---|")
    for x in r["lines"]:
        cost = "check" if x["gbp_year_incl_vat"] is None else f"{x['gbp_year_incl_vat']:,.2f}"
        print(f"| {x['job']} | {x['platform']} | {cost} | {x['connect']} |")
    extra = f" + {', '.join(r['price_not_recorded'])} (price to check)" if r["price_not_recorded"] else ""
    print(f"| **Total** | | **{r['total_gbp_year_incl_vat']:,.2f}**{extra} | |\n")
    for x in r["lines"]:
        print(f"- **{x['job']}:** {x['how']}" + (f" Alternative: {x['alternative']}" if x["alternative"] else ""))
    if r["gaps"]:
        print("\nNot covered yet:")
        for g in r["gaps"]:
            print(f"- {g}")
    print("\nYou open and pay for each platform yourself; nothing is signed up for you.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, choices=["ltd", "clg", "cic", "unincorporated", "charity"])
    ap.add_argument("--size", choices=["micro", "small", "medium"])
    ap.add_argument("--turnover", type=float)
    ap.add_argument("--assets", type=float)
    ap.add_argument("--employees", type=int, default=0)
    ap.add_argument("--vat", action="store_true")
    ap.add_argument("--books", default="none")
    ap.add_argument("--period-start", default="9999-12-31", help="YYYY-MM-DD: picks the size limits in force (default: current)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = pick(a)
    print(json.dumps(r, indent=2)) if a.json else show(r)
    sys.exit(0)

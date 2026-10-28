"""Build a company's year-end trial balance from its bank-line files plus books/<id>/filed/<FY>/inputs.json.

Usage: python3 engine/scripts/build_tb.py <entity_id> <FY> [--write]
  prints the TB and every check; --write saves books/<id>/filed/<FY>/trial_balance.csv (only if every check passes).

Double entry, signed debit-positive. An included line of amount A on an account whose ledger code is B, coded C:
  own side   B += A        (always)
  other side C -= A        (only when C is not itself an account with its own bank-line files)
so a transfer between two accounts that both have files is counted once, by each file's own side. Each account's
ledger code is entity.json bank_accounts.<account>.ledger_code.

inputs.json:
  {"opening": {"<code>": <debit-positive amount>, ...},      balances b/f for codes WITHOUT their own files
   "retained_earnings_bf_filed": <debit-positive 960 b/f, from last year's filed accounts after any correction>,
   "adjustments": [{"debit": "<code>", "credit": "<code>", "amount": <positive>, "note": "...", "decided_by": "director|agent"}],
   "prior_year": {"source": "<file under books/<id>/ holding last year's filed accounts>",
                  "filed": {"share_capital": <n>, "profit_and_loss_account": <n, credit positive>, "net_assets": <n>}}
              or {"first_year": true}   (only when period_start is the incorporation date),
   "closing_balances": {"<code>": {"amount": <debit-positive>, "source": "<statement, or the director, with date>"}}}
                      every balance-sheet code without its own bank-line files that ends the year non-zero
                      (pots, e-money, director's loan, stock, accruals...); corporation tax (830) is computed
Calculated here, never typed in as adjustments (an adjustment with the same accounts fails, so nothing counts twice):
  platform fees  sales/<FY>_summary.json "totals": {"total_sales", "received_in_bank", "balances_at_year_end":
                 {"<platform>": {"amount", "source"}}}; fees = total_sales - received_in_bank, debit 404 credit sales.
                 received_in_bank must equal the bank lines coded to sales from platforms.
  use of home    accounts.decisions.use_of_home.weeks x £6, debit 445 credit 835
  mileage        accounts.decisions.mileage.miles at 45p (25p over 10,000), debit 493 credit 835
Opening balances of accounts WITH files come from their first line (balance_after - amount).

Checks (exit 1 on any failure): every code is in accounts/account_map.json; each file's balances chain; each pair of
accounts with files agrees on the transfers between them; retained earnings b/f derived from the opening balances
equals retained_earnings_bf_filed; debits = credits; last year's filed accounts are on file (prior_year), so the
opening position is evidence, never a balancing figure; sales paid out by a platform (Shopify, PayPal, Stripe...)
have the platform's summary in books/<id>/sales/<FY>_summary.json, because bank receipts are sales after fees.
"""
import csv, json, re, sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import books_io as b

D = lambda v: Decimal(str(v or 0)).quantize(Decimal("0.01"))
RE = "960"
FEES, HOME, TRAVEL, DLA, CT_CREDITOR = "404", "445", "493", "835", "830"
HOME_WEEKLY = Decimal(6)  # HMRC flat rate for working from home, per week
EVIDENCED = {"bank", "current_asset", "current_liability", "accruals", "fixed_asset"}
PLATFORMS = re.compile(r"shopify|paypal|stripe|etsy|amazon|ebay|square|sumup|zettle|wix|squarespace|gumroad", re.I)


def prior_year_problems(ent, root, inputs):
    """Last year's position must come from a document on file, not from the agent's arithmetic."""
    py = inputs.get("prior_year")
    if not py:
        return ["inputs.json has no prior_year: put last year's filed accounts in books/<id>/filed/<last FY>/ and "
                "record them (50_year_end step 7). If you can't get them, stop and ask the director; never assume "
                "opening balances"]
    if py.get("first_year"):
        if inputs.get("period_start") != ent.get("incorporated"):
            return [f"prior_year.first_year, but period_start {inputs.get('period_start')} is not the incorporation "
                    f"date {ent.get('incorporated')}: the company has filed accounts before"]
        return []
    out = []
    src = py.get("source") or ""
    if not src or not (root / src).is_file():
        out.append(f"prior_year.source '{src}' is not a file under books/{ent['id']}/")
    missing = [k for k in ("share_capital", "profit_and_loss_account", "net_assets") if k not in py.get("filed", {})]
    if missing:
        out.append(f"prior_year.filed is missing {', '.join(missing)} (copy them from last year's accounts)")
    return out


def platform_gross_up(summary, received, platforms, sales_code, problems, warnings):
    """Bank receipts from a platform are sales after its fees. The fees are the platform's sales less what reached
    the bank; posted debit fees, credit sales, so turnover is the platform's figure."""
    t = summary.get("totals") or {}
    if "total_sales" not in t or "received_in_bank" not in t:
        problems.append('sales summary needs "totals": {"total_sales": <the platform\'s sales incl. shipping, after '
                        'refunds>, "received_in_bank": <payouts that reached the bank>} (50_year_end step 6)')
        return []
    total, got = D(t["total_sales"]), D(t["received_in_bank"])
    if got != received:
        problems.append(f"sales summary says {got} reached the bank, but bank lines coded to sales from platforms "
                        f"total {received}: a payout is missing, doubled or miscoded")
    held = t.get("balances_at_year_end") or {}
    for p in sorted(platforms):
        if not (held.get(p) or {}).get("source"):
            problems.append(f'sales summary totals.balances_at_year_end.{p} missing: what was left in {p} at the year '
                            f'end? {{"amount": n, "source": "<statement, or the director>"}}')
        elif D(held[p].get("amount")):
            problems.append(f"{p} held {D(held[p]['amount'])} at the year end: give it its own account in the chart "
                            f"with its lines (the automatic gross-up assumes everything was paid out)")
    fees = total - got
    if total and not Decimal("0.01") <= fees / total <= Decimal("0.06"):
        warnings.append(f"platform fees are {fees} ({(fees / total * 100).quantize(Decimal('0.1'))}% of sales); "
                        f"card and platform fees are usually 1-6%: check the summary and the payouts")
    return [{"debit": FEES, "credit": sales_code, "amount": fees, "decided_by": "script",
             "note": f"Platform fees: sales {total} less {got} received in the bank"}] if fees else []


def decision_postings(dec, inputs, problems):
    """Use of home and mileage are calculated from the director's answers, never typed in as amounts."""
    out = []
    home = dec.get("use_of_home")
    if home is not None:
        if "weeks" not in home:
            problems.append('decisions.use_of_home needs "weeks": whole weeks the director worked from home this '
                            'period (0 if none)')
        else:
            weeks = int(home["weeks"])
            start, end = inputs.get("period_start"), inputs.get("period_end")
            if start and end and weeks > ((date.fromisoformat(end) - date.fromisoformat(start)).days + 1) // 7 + 1:
                problems.append(f"decisions.use_of_home.weeks {weeks} is more than the weeks in the period")
            if weeks:
                out.append({"debit": HOME, "credit": DLA, "amount": HOME_WEEKLY * weeks, "decided_by": "director",
                            "note": f"Use of home, HMRC flat rate £{HOME_WEEKLY}/week x {weeks} weeks, owed to the director"})
    miles = dec.get("mileage")
    if miles is not None:
        if "miles" not in miles:
            problems.append('decisions.mileage needs "miles": business miles in the director\'s own car, from their '
                            'mileage log (0 if none)')
        elif D(miles["miles"]):
            m = D(miles["miles"])
            amt = (min(m, 10000) * Decimal("0.45") + max(m - 10000, 0) * Decimal("0.25")).quantize(Decimal("0.01"))
            out.append({"debit": TRAVEL, "credit": DLA, "amount": amt, "decided_by": "director",
                        "note": f"Business mileage, HMRC rates (45p, 25p over 10,000) x {m} miles, owed to the director"})
    return out


def build(entity_id, fy):
    ent = b.entity(entity_id)
    root = b.books_root() / entity_id
    accounts = json.loads((root / "accounts" / "account_map.json").read_text())["accounts"]
    chart = {a["code"]: a["name"] for a in accounts}
    chart_cls = {a["code"]: a.get("class") for a in accounts}
    inputs_file = root / "filed" / fy / "inputs.json"
    if not inputs_file.is_file():
        sys.exit(f"FAIL  no {inputs_file.relative_to(root.parent)}: create it with period_start and period_end first "
                 f"(50_year_end step 9)")
    inputs = json.loads(inputs_file.read_text())
    problems, tb = prior_year_problems(ent, root, inputs), {}
    problems += [f"{c} is still named '{n}' in the chart: give it the real account's name"
                 for c, n in chart.items() if "<" in n]
    platform_sales, platform_received, sales_code, warnings = set(), Decimal(0), "200", []

    def post(code, amt):
        tb[code] = tb.get(code, Decimal(0)) + amt

    files = {}
    for acct, info in ent.get("bank_accounts", {}).items():
        rows = b.read_lines(entity_id, acct, fy)
        if not rows:
            continue
        if not info.get("ledger_code"):
            problems.append(f"{acct}: entity.json has no ledger_code")
            continue
        files[acct] = (info["ledger_code"], rows)
    file_codes = {code: acct for acct, (code, _) in files.items()}
    if len(file_codes) < len(files):
        problems.append("two accounts share a ledger_code in entity.json; each needs its own")

    opening = {k: D(v) for k, v in inputs.get("opening", {}).items()}
    for code in opening:
        if code in file_codes:
            problems.append(f"opening {code}: comes from {file_codes[code]}'s first line, not inputs.json")
    transfers = {}
    for acct, (own, rows) in files.items():
        first = rows[0]
        ob = D(first["balance_after"]) - D(first["amount"]) if first.get("balance_after") else D(0)
        opening[own] = ob
        bal = ob
        for r in rows:
            amt = D(r["amount"])
            bal += amt
            if r.get("balance_after") and D(r["balance_after"]) != bal:
                problems.append(f"{acct} {r['txn_date']}: balance {r['balance_after']} but lines give {bal}")
                bal = D(r["balance_after"])
            if r.get("include_status") == "excluded":
                continue
            code = r.get("account_code") or ""
            if code not in chart:
                problems.append(f"{acct} {r['txn_date']} {amt}: code '{code}' not in the chart")
                continue
            post(own, amt)
            if chart_cls.get(code) == "revenue" and amt > 0:
                hit = PLATFORMS.search(f"{r.get('counterparty', '')} {r.get('reference', '')}")
                if hit:
                    platform_sales.add(hit.group(0).lower())
                    platform_received += amt
                    sales_code = code
            if code in file_codes:
                transfers[(own, code)] = transfers.get((own, code), Decimal(0)) + amt
            else:
                post(code, -amt)

    auto = []
    summary = root / "sales" / f"{fy}_summary.json"
    if platform_sales and not summary.is_file():
        problems.append(f"sales received from {', '.join(sorted(platform_sales))} are after the platform's fees: get "
                        f"its sales summary into books/{entity_id}/sales/{fy}_summary.json (50_year_end step 6)")
    elif platform_sales:
        auto += platform_gross_up(json.loads(summary.read_text()), platform_received, platform_sales, sales_code,
                                  problems, warnings)
    auto += decision_postings((inputs.get("accounts") or {}).get("decisions") or {}, inputs, problems)

    for x, y in {tuple(sorted(k)) for k in transfers}:
        there, back = transfers.get((x, y), Decimal(0)), transfers.get((y, x), Decimal(0))
        if there + back != 0:
            problems.append(f"transfers between {file_codes[x]} and {file_codes[y]}: {there} on one side, {-back} on the other")

    for code, amt in opening.items():
        if code not in chart:
            problems.append(f"opening {code} not in the chart")
        post(code, amt)
    re_bf = -sum(opening.values(), Decimal(0))
    post(RE, re_bf)
    if "retained_earnings_bf_filed" not in inputs:
        problems.append("inputs.json has no retained_earnings_bf_filed (last year's filed figure)")
    elif re_bf != D(inputs["retained_earnings_bf_filed"]):
        problems.append(f"retained earnings b/f: opening balances give {re_bf}, last year's accounts {D(inputs['retained_earnings_bf_filed'])}")

    calculated = {(FEES, sales_code), (HOME, DLA), (TRAVEL, DLA)}
    for adj in inputs.get("adjustments", []):
        if (adj["debit"], adj["credit"]) in calculated:
            problems.append(f"adjustment '{adj.get('note', '')}': platform fees, use of home and mileage are now "
                            f"calculated by the script; remove this entry so it isn't counted twice")
    for adj in inputs.get("adjustments", []) + auto:
        for side in ("debit", "credit"):
            if adj[side] not in chart:
                problems.append(f"adjustment '{adj.get('note', '')}': code {adj[side]} not in the chart")
        post(adj["debit"], D(adj["amount"]))
        post(adj["credit"], -D(adj["amount"]))

    # Every balance-sheet figure without its own bank-line file needs a source for its year-end amount.
    evidence = inputs.get("closing_balances") or {}
    for code, v in sorted(tb.items()):
        if not v or code in file_codes or code == CT_CREDITOR or chart_cls.get(code) not in EVIDENCED:
            continue
        e = evidence.get(code) or {}
        if not e.get("source"):
            problems.append(f"{code} {chart.get(code)} ends the year at {v}: record it in inputs.json closing_balances."
                            f'{code} as {{"amount": {v}, "source": "<statement, or the director, with date>"}}')
        elif D(e.get("amount")) != v:
            problems.append(f"{code} {chart.get(code)}: the books give {v} at the year end, closing_balances says "
                            f"{D(e.get('amount'))} ({e['source']})")

    lines = [(c, chart.get(c, "?"), v) for c, v in sorted(tb.items()) if v != 0]
    dr = sum((v for _, _, v in lines if v > 0), Decimal(0))
    cr = -sum((v for _, _, v in lines if v < 0), Decimal(0))
    if dr != cr:
        problems.append(f"debits {dr} != credits {cr}")
    return lines, dr, cr, problems, opening, {"auto": auto, "warnings": warnings}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    entity_id, fy = sys.argv[1], sys.argv[2]
    lines, dr, cr, problems, _, extra = build(entity_id, fy)
    for code, name, v in lines:
        print(f"{code}  {name[:40]:40} {v if v > 0 else '':>12} {-v if v < 0 else '':>12}")
    print(f"{'':46}{dr:>12} {cr:>12}")
    for a in extra["auto"]:
        print(f"AUTO  {a['note']}: debit {a['debit']} credit {a['credit']} {a['amount']}")
    for w in extra["warnings"]:
        print("CHECK", w)
    for p in problems:
        print("FAIL ", p)
    if problems:
        sys.exit(1)
    print("PASS  all checks")
    if "--write" in sys.argv:
        out = b.books_root() / entity_id / "filed" / fy / "trial_balance.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["line_order", "source_code", "source_name", "debit", "credit"])
            for i, (code, name, v) in enumerate(lines, 1):
                w.writerow([i, code, name, v if v > 0 else 0, -v if v < 0 else 0])
        print(f"written {out}")


if __name__ == "__main__":
    main()

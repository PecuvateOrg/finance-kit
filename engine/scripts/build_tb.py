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
   "adjustments": [{"debit": "<code>", "credit": "<code>", "amount": <positive>, "note": "...", "decided_by": "director|agent"}]}
Opening balances of accounts WITH files come from their first line (balance_after - amount).

Checks (exit 1 on any failure): every code is in accounts/account_map.json; each file's balances chain; each pair of
accounts with files agrees on the transfers between them; retained earnings b/f derived from the opening balances
equals retained_earnings_bf_filed; debits = credits.
"""
import csv, json, sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import books_io as b

D = lambda v: Decimal(str(v or 0)).quantize(Decimal("0.01"))
RE = "960"


def build(entity_id, fy):
    ent = b.entity(entity_id)
    root = b.books_root() / entity_id
    chart = {a["code"]: a["name"] for a in json.loads((root / "accounts" / "account_map.json").read_text())["accounts"]}
    inputs = json.loads((root / "filed" / fy / "inputs.json").read_text())
    problems, tb = [], {}

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
            if code in file_codes:
                transfers[(own, code)] = transfers.get((own, code), Decimal(0)) + amt
            else:
                post(code, -amt)

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

    for adj in inputs.get("adjustments", []):
        for side in ("debit", "credit"):
            if adj[side] not in chart:
                problems.append(f"adjustment '{adj.get('note', '')}': code {adj[side]} not in the chart")
        post(adj["debit"], D(adj["amount"]))
        post(adj["credit"], -D(adj["amount"]))

    lines = [(c, chart.get(c, "?"), v) for c, v in sorted(tb.items()) if v != 0]
    dr = sum((v for _, _, v in lines if v > 0), Decimal(0))
    cr = -sum((v for _, _, v in lines if v < 0), Decimal(0))
    if dr != cr:
        problems.append(f"debits {dr} != credits {cr}")
    return lines, dr, cr, problems


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    entity_id, fy = sys.argv[1], sys.argv[2]
    lines, dr, cr, problems = build(entity_id, fy)
    for code, name, v in lines:
        print(f"{code}  {name[:40]:40} {v if v > 0 else '':>12} {-v if v < 0 else '':>12}")
    print(f"{'':46}{dr:>12} {cr:>12}")
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

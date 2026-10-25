"""Check every bank-line file under the books root. Exit 1 on any problem.

Usage: python3 engine/scripts/validate.py [entity_id ...]   (no args = every entity)

Year files (companies with no ledger software) — checks per account: exact header; every row passes books_io.check_row (required fields, ISO dates, 2dp amounts,
no unmasked numbers); source_line_key unique across all year files; each row sits in the FY file its date
belongs to; every included row's account_code is a code in accounts/account_map.json (the chart is required once
there are year files — names alone are not codes, 2026-10-19); where balance_after is present on consecutive rows, previous balance + amount = balance.
Ledger companies (companies whose books are kept in a ledger platform) — posted_index.csv + pending.csv: keys unique, no key in both, amounts 2dp,
pending rows pass check_row (masked text), pending continues from the index's last day and chains.
An account with nothing to check is reported as such, never as PASS.
"""
import csv, json, sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import books_io as b


def chart_codes(entity_id):
    """Codes in a no-ledger company's chart ({"accounts": [{"code": ...}]}), or None if it has none."""
    f = b.books_root() / entity_id / "accounts" / "account_map.json"
    if not f.exists():
        return None
    data = json.loads(f.read_text())
    return {a["code"] for a in data["accounts"]} if isinstance(data, dict) else None


def validate_account(entity_id, acc_dir, ye):
    problems, seen, chain = [], {}, []
    codes = chart_codes(entity_id)
    for f in sorted(acc_dir.glob("FY*.csv")):
        with f.open(newline="") as fh:
            r = csv.DictReader(fh)
            if r.fieldnames != b.COLUMNS:
                problems.append(f"{f}: header differs from books_io.COLUMNS")
                continue
            rows = list(r)
        for i, row in enumerate(rows, 2):
            where = f"{f.name}:{i}"
            problems += [f"{where} {e}" for e in b.check_row(row)]
            if row["include_status"] == "included":
                if codes is None:
                    problems.append(f"{where} no chart of accounts (accounts/account_map.json) to code against")
                elif row["account_code"] not in codes:
                    problems.append(f"{where} account_code {row['account_code']!r} is not in the chart of accounts")
            k = row["source_line_key"]
            if k in seen:
                problems.append(f"{where} duplicate source_line_key {k} (first at {seen[k]})")
            seen[k] = where
            if row["txn_date"] and b.fy_label(row["txn_date"], ye) != f.stem:
                problems.append(f"{where} dated {row['txn_date']} but filed in {f.stem}")
        chain += [dict(r, _where=f"{f.name}:{i}") for i, r in enumerate(rows, 2)]
    # the chain runs across year files: the first line of a year follows the last line of the one before
    problems += chain_breaks(chain)
    ledger_problems, n_ledger = ledger_files(acc_dir)
    return problems + ledger_problems, len(seen) + n_ledger


def chain_breaks(rows):
    """Consecutive rows with balances: previous balance + amount must equal the balance."""
    out = []
    for prev, row in zip(rows, rows[1:]):
        if prev["balance_after"] and row["balance_after"] and not b.check_row(prev) and not b.check_row(row):
            if Decimal(prev["balance_after"]) + Decimal(row["amount"]) != Decimal(row["balance_after"]):
                out.append(f"{row.get('_where') or row['source_line_key']} balance chain broken: "
                           f"{prev['balance_after']} + {row['amount']} != {row['balance_after']}")
    return out


def ledger_files(acc_dir):
    problems = []
    idx, pend = b._read_csv(acc_dir / "posted_index.csv"), b._read_csv(acc_dir / "pending.csv")
    if (acc_dir / "posted_index.csv").exists():
        with (acc_dir / "posted_index.csv").open(newline="") as fh:
            if next(csv.reader(fh)) != b.INDEX_COLUMNS:
                problems.append("posted_index.csv: header differs from books_io.INDEX_COLUMNS")
    keys = {}
    for name, rows in (("posted_index", idx), ("pending", pend)):
        for i, r in enumerate(rows, 2):
            where = f"{name}.csv:{i}"
            k = r["source_line_key"]
            if k in keys:
                problems.append(f"{where} key {k} also at {keys[k]}")
            keys[k] = where
            errs = b.check_row(r) if name == "pending" else b.check_row({**r, "source": "index"})
            if name == "posted_index" and b.unmasked(r.get("exclude_reason")):
                errs.append("exclude_reason holds an unmasked number")
            problems += [f"{where} {e}" for e in errs]
    # The index is NOT one ordered chain: migrated history is stored by settlement date while Starling's running
    # balance follows transaction time, and card exports carry no running balance (checked 2026-10-13). bank_sync
    # relies only on the latest day, so that is what is checked: pending lines must continue from a balance the
    # index holds in its last few days, and chain among themselves.
    if pend and idx:
        last = max(r["txn_date"] for r in idx)
        recent = {Decimal(r["balance_after"]) for r in idx if r["balance_after"] and r["txn_date"] >= last}
        first = pend[0]
        if first["balance_after"] and recent and Decimal(first["balance_after"]) - Decimal(first["amount"]) not in recent:
            problems.append(f"pending does not continue from the index's last day ({last}): {first['source_line_key']}")
    problems += chain_breaks(pend)
    return problems, len(idx) + len(pend)


def main(entities):
    root = b.books_root()
    entities = entities or sorted(p.name for p in root.iterdir() if (p / "entity.json").exists())
    bad = 0
    for e in entities:
        ye = b.entity(e)["year_end_month"]
        for acc in sorted(p for p in (root / e / "bank").glob("*") if p.is_dir()):
            problems, n = validate_account(e, acc, ye)
            print(f"{'FAIL' if problems else 'PASS' if n else 'EMPTY'}  {e}/{acc.name}  {n} lines"
                  + ("" if n or problems else "  (nothing to check)"))
            for p in problems:
                print(f"      {p}")
            bad += bool(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])

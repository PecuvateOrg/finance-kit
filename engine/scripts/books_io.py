"""Read and append canonical bank lines in books/<entity>/bank/<account>/<FY>.csv.

Replaces the finance.bank_transactions table (plan-finance-files-and-portable-kit.md §3). The table's unique
constraint becomes a check here: a source_line_key already in any year file of the account is skipped if the
row is identical, and stops the write if it differs. Free text is masked on write (NON-NEGOTIABLES: never store
account numbers, sort codes or card numbers; last 4 only). Standard library only.

Books root: $FINANCE_BOOKS, else <repo>/books.
"""
import csv, json, os, re, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

COLUMNS = ["source_line_key", "txn_date", "counterparty", "reference", "txn_type", "amount", "balance_after",
           "source", "source_code", "account_code", "coding_status", "include_status", "exclude_reason",
           "ledger_tx_id", "splits", "notes"]
REQUIRED = ["source_line_key", "txn_date", "amount", "source"]
TEXT = ["counterparty", "reference", "notes"]

# digit lookarounds, not \b: a number run straight into letters ("12345678901ABC1234") has no word boundary
_SORT_CODE = re.compile(r"(?<!\d)\d{2}[- ]\d{2}[- ]\d{2}(?!\d)")
_LONG_DIGITS = re.compile(r"(?<!\d)\d(?:[ -]?\d){7,18}(?!\d)")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# never masked: ISO dates and UUIDs (Xero/contact ids) are not account numbers
_PROTECTED = re.compile(r"(\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b|\b\d{4}-\d{2}-\d{2}\b)")


def books_root():
    return Path(os.environ.get("FINANCE_BOOKS") or Path(__file__).resolve().parents[2] / "books")


def entity(entity_id):
    return json.loads((books_root() / entity_id / "entity.json").read_text())


def fy_label(txn_date, year_end_month):
    """FY named by the calendar year it ends in: year end 31 Jan, 2025-02-01..2026-01-31 -> FY2026."""
    y, m = int(txn_date[:4]), int(txn_date[5:7])
    return f"FY{y + 1 if m > year_end_month else y}"


def mask(text):
    """Keep the last 4 digits of anything that looks like a sort code, account or card number."""
    if not text:
        return text
    def keep4(m):
        digits = re.sub(r"\D", "", m.group(0))
        return "*" * (len(digits) - 4) + digits[-4:]
    parts = _PROTECTED.split(text)  # odd indexes are dates/uuids
    return "".join(p if i % 2 else _LONG_DIGITS.sub(keep4, _SORT_CODE.sub("**-**-**", p)) for i, p in enumerate(parts))


def unmasked(text):
    """True if text still holds a sort code or an 8+ digit run (what validate.py fails on)."""
    rest = _PROTECTED.sub(" ", text or "")
    return bool(_SORT_CODE.search(rest) or _LONG_DIGITS.search(rest))


def account_dir(entity_id, account):
    return books_root() / entity_id / "bank" / account


def read_lines(entity_id, account, fy=None):
    files = [account_dir(entity_id, account) / f"{fy}.csv"] if fy else sorted(account_dir(entity_id, account).glob("FY*.csv"))
    return [r for f in files for r in _read_csv(f)]


def check_row(row):
    """Return a list of problems with one row (empty = fine)."""
    errs = [f"missing {c}" for c in REQUIRED if not row.get(c)]
    if row.get("txn_date") and not _DATE.match(row["txn_date"]):
        errs.append(f"txn_date not YYYY-MM-DD: {row['txn_date']}")
    for c in ("amount", "balance_after"):
        v = row.get(c)
        if v:
            try:
                if Decimal(v).as_tuple().exponent < -2:
                    errs.append(f"{c} has more than 2 decimals: {v}")
            except InvalidOperation:
                errs.append(f"{c} not a number: {v}")
    errs += [f"{c} holds an unmasked number" for c in TEXT if unmasked(row.get(c))]
    return errs


def append_lines(entity_id, account, rows):
    """Append rows, each filed under its own FY. Returns (added, skipped_identical). Exits on any conflict."""
    ye = entity(entity_id)["year_end_month"]
    existing = {r["source_line_key"]: r for r in read_lines(entity_id, account)}
    by_fy, added, skipped = {}, 0, 0
    for raw in rows:
        row = {c: ("" if raw.get(c) is None else str(raw.get(c))) for c in COLUMNS}
        for c in TEXT:
            row[c] = mask(row[c])
        errs = check_row(row)
        if errs:
            sys.exit(f"{row.get('source_line_key') or '?'}: {'; '.join(errs)} — nothing written")
        key = row["source_line_key"]
        if key in existing:
            if existing[key] == row:
                skipped += 1
                continue
            sys.exit(f"{key} already stored with different values — nothing written")
        existing[key] = row
        by_fy.setdefault(fy_label(row["txn_date"], ye), []).append(row)
        added += 1
    d = account_dir(entity_id, account)
    d.mkdir(parents=True, exist_ok=True)
    lock = d / ".lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        sys.exit(f"{lock} exists — another run is writing this account")
    try:
        os.close(fd)
        for fy, new in by_fy.items():
            f = d / f"{fy}.csv"
            all_rows = read_lines(entity_id, account, fy) + new
            all_rows.sort(key=lambda r: r["txn_date"])  # stable: same-day lines keep arrival order (balance chain)
            tmp = f.with_suffix(".tmp")
            with tmp.open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=COLUMNS)
                w.writeheader()
                w.writerows(all_rows)
            tmp.replace(f)
    finally:
        lock.unlink()
    return added, skipped



# ---- ledger companies (D7): posted index + pending lines, write log -------------------------------------
INDEX_COLUMNS = ["source_line_key", "txn_date", "amount", "balance_after", "include_status", "exclude_reason",
                 "ledger_tx_id"]


def _read_csv(path):
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows({c: ("" if r.get(c) is None else str(r.get(c))) for c in cols} for r in rows)
    tmp.replace(path)


def read_index(entity_id, account):
    """Lines already in the ledger (posted, or excluded as settled via a payment), oldest first."""
    return _read_csv(account_dir(entity_id, account) / "posted_index.csv")


def add_to_index(entity_id, account, rows):
    """Append index rows; a key already present is refused (exit) rather than duplicated."""
    path = account_dir(entity_id, account) / "posted_index.csv"
    cur = _read_csv(path)
    have = {r["source_line_key"] for r in cur}
    for r in rows:
        if r["source_line_key"] in have:
            sys.exit(f"{r['source_line_key']} already in posted_index — not added twice")
        have.add(r["source_line_key"])
    _write_csv(path, INDEX_COLUMNS, cur + [{**r, "exclude_reason": mask(r.get("exclude_reason"))} for r in rows])


def read_pending(entity_id, account):
    """Pulled lines not yet in the ledger: held for the owner, or coded and waiting to post (full columns, masked)."""
    return _read_csv(account_dir(entity_id, account) / "pending.csv")


def write_pending(entity_id, account, rows):
    for r in rows:
        for c in TEXT:
            r[c] = mask(r.get(c))
        errs = check_row(r)
        if errs:
            sys.exit(f"pending {r.get('source_line_key')}: {'; '.join(errs)}")
    rows = sorted(rows, key=lambda r: r["txn_date"])
    path = account_dir(entity_id, account) / "pending.csv"
    if rows:
        _write_csv(path, COLUMNS, rows)
    elif path.exists():
        path.unlink()


def mask_deep(o, key=""):
    """Mask bank-derived text anywhere in a JSON value; keys ending in id (uuids) are left alone."""
    if isinstance(o, dict):
        return {k: mask_deep(v, k) for k, v in o.items()}
    if isinstance(o, list):
        return [mask_deep(v, key) for v in o]
    if isinstance(o, str) and not key.lower().endswith("id"):
        return mask(o)
    return o


def read_log(entity_id):
    f = books_root() / entity_id / "log" / "writes.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []


def log_write(entity_id, operation, payload, external_id=None, ok=True, error=None, actor="agent:interactive",
              target="xero", bank_line_key=None):
    """Append one external write to books/<entity>/log/writes.jsonl (replaces finance.write_log). Every write to
    Xero, HMRC or a bank is logged here, by scripts and by hand alike. Payload text is masked."""
    import datetime, uuid
    row = {"id": str(uuid.uuid4()), "entity_id": entity_id, "target": target, "operation": operation, "actor": actor,
           "payload": mask_deep(payload), "external_id": external_id, "response_status": "ok" if ok else "error",
           "error": None if ok else mask(str(error))[:2000], "bank_line_key": bank_line_key,
           "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    f = books_root() / entity_id / "log" / "writes.jsonl"
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


if __name__ == "__main__":
    # python3 engine/scripts/books_io.py append <entity> <account> <rows.json>
    #   ... append <entity> <account> <rows.json>
    #   ... log <entity> <operation> <payload.json> [external_id] [--error "message"]   (hand-made writes too)
    if len(sys.argv) == 5 and sys.argv[1] == "append":
        added, skipped = append_lines(sys.argv[2], sys.argv[3], json.loads(Path(sys.argv[4]).read_text()))
        print(f"added {added}, already stored {skipped}")
    elif len(sys.argv) >= 5 and sys.argv[1] == "log":
        err = sys.argv[sys.argv.index("--error") + 1] if "--error" in sys.argv else None
        ext = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != "--error" else None
        r = log_write(sys.argv[2], sys.argv[3], json.loads(Path(sys.argv[4]).read_text()), ext, ok=err is None, error=err)
        print(f"logged {r['operation']} {r['id']}")
    else:
        sys.exit("usage: books_io.py append <entity> <account> <rows.json>\n"
                 "       books_io.py log <entity> <operation> <payload.json> [external_id] [--error MSG]")

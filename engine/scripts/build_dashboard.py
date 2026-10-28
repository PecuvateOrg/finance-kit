"""Write a one-file dashboard of a company's books for the director: books/<id>/dashboard.html.

Usage: python3 engine/scripts/build_dashboard.py <entity_id> [<FY>]
  FY defaults to the latest books/<id>/filed/<FY>/ that has an inputs.json. Opens in any browser by double-click;
  no server, no internet, nothing leaves the machine. Rerun whenever the books change.

Shows: money in and out by month with the cash balance (bank lines, transfers between the company's own accounts
left out); the year's result, balance sheet and tax against last year (build_accounts.draft, so the figures are the
draft's own; if the draft isn't ready, what's missing instead); what's due next (obligations.json); what's waiting
on whom (status.json); and the draft's checks.
"""
import html, json, sys
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import books_io as b
from build_accounts import draft

E = html.escape
DONE = {"submitted", "filed", "paid", "accepted", "done", "complete", "completed", "not_required", "not_applicable"}


def money(v, sign=False):
    v = Decimal(str(v or 0))
    s = f"£{abs(v):,.2f}"
    return f"({s})" if v < 0 and not sign else (f"−{s}" if v < 0 else s)


def monthly(entity_id, ent, fy):
    """{YYYY-MM: [in, out, closing cash]} from every account's lines; own-account transfers are not money in or out."""
    accounts = {a: i for a, i in ent.get("bank_accounts", {}).items() if i.get("ledger_code")}
    own = {i["ledger_code"] for i in accounts.values()}
    months, closing = defaultdict(lambda: [Decimal(0), Decimal(0)]), defaultdict(dict)
    for acct in accounts:
        for r in b.read_lines(entity_id, acct, fy):
            m, amt = r["txn_date"][:7], Decimal(r["amount"] or 0)
            if r.get("balance_after"):
                closing[m][acct] = Decimal(r["balance_after"])
            if r.get("include_status") == "excluded" or r.get("account_code") in own:
                continue
            months[m][0 if amt > 0 else 1] += amt
    out, last = {}, {}
    for m in sorted(set(months) | set(closing)):
        last.update(closing.get(m, {}))
        out[m] = [months[m][0], -months[m][1], sum(last.values(), Decimal(0))]
    return out


def chart(data):
    """Bars for money in (green) and out (red) per month; a line for cash at the month end."""
    if not data:
        return "<p class='muted'>No bank lines for this year yet.</p>"
    w, h, pad = 720, 260, 72
    top = max([max(v[0], v[1], abs(v[2])) for v in data.values()] + [Decimal(1)])
    low = min([v[2] for v in data.values()] + [Decimal(0)])
    span = top - low
    y = lambda v: pad + (h - 2 * pad) * float((top - v) / span)
    step = (w - 2 * pad) / len(data)
    bw = min(step / 3, 18)
    parts, pts = [f"<line x1='{pad}' x2='{w - pad}' y1='{y(0):.1f}' y2='{y(0):.1f}' class='axis'/>"], []
    for i, (m, (inn, out, cash)) in enumerate(data.items()):
        x = pad + i * step + step / 2
        for dx, v, cls, label in ((-bw, inn, "in", "in"), (0, out, "out", "out")):
            parts.append(f"<rect x='{x + dx:.1f}' y='{y(v):.1f}' width='{bw:.1f}' height='{y(0) - y(v):.1f}' "
                         f"class='{cls}'><title>{m} money {label}: {money(v)}</title></rect>")
        pts.append(f"{x:.1f},{y(cash):.1f}")
        parts.append(f"<circle cx='{x:.1f}' cy='{y(cash):.1f}' r='3' class='cash'><title>{m} cash at month end: "
                     f"{money(cash, True)}</title></circle>")
        parts.append(f"<text x='{x:.1f}' y='{h - pad + 16}' class='lbl'>{date.fromisoformat(m + '-01'):%b}</text>")
    parts.insert(1, f"<polyline points='{' '.join(pts)}' class='cashline'/>")
    for v in (top, low) if low < 0 else (top,):
        parts.append(f"<text x='{pad - 6}' y='{y(v) + 4:.1f}' class='lbl end'>{money(v, True)}</text>")
    return (f"<svg viewBox='0 0 {w} {h}' role='img' aria-label='Money in and out by month'>{''.join(parts)}</svg>"
            "<p class='legend'><span class='k in'></span>Money in <span class='k out'></span>Money out "
            "<span class='k cash'></span>Cash at month end (all accounts, cards owed count as minus)</p>")


def accounts_html(fy, built, filed):
    accounts, period, _, problems, checks = built
    if problems:
        items = "".join(f"<li>{E(p)}</li>" for p in problems)
        return (f"<p>The {E(fy)} draft isn't ready yet. Your agent is waiting on:</p><ul>{items}</ul>", checks)
    fin, tax = accounts["financials"], accounts["tax"]
    pl, bs, prior = fin["profit_and_loss"], fin["balance_sheet"], fin.get("prior_year", {})
    result = period["profit_loss"]
    rows = [("Turnover", pl["turnover"], None)] + [
        (label, -pl[k], None) for k, label in (("cost_of_sales", "Cost of sales"), ("staff_costs", "Staff costs"),
                                               ("depreciation", "Depreciation"),
                                               ("other_operating_expenses", "Other costs")) if pl[k]]
    if pl.get("other_income"):
        rows.insert(1, ("Other income", pl["other_income"], None))
    net = lambda s: s.get("fixed_assets", 0) + s.get("current_assets", 0) - s.get("creditors_within_one_year", 0) \
        - s.get("accruals_and_deferred_income", 0)
    bsrows = [("Fixed assets", "fixed_assets", 1), ("Cash and other current assets", "current_assets", 1),
              ("Owed within a year", "creditors_within_one_year", -1),
              ("Accruals", "accruals_and_deferred_income", -1)]
    status = "Filed" if filed else "Draft for your approval"
    out = [f"<div class='tiles'><div class='tile'><span>{'Profit' if result >= 0 else 'Loss'} for {E(fy)}</span>"
           f"<b class='{'pos' if result >= 0 else 'neg'}'>{money(abs(result))}</b></div>"
           f"<div class='tile'><span>Corporation tax</span><b>{money(tax['corporation_tax'])}</b></div>"
           f"<div class='tile'><span>Net {'assets' if net(bs) >= 0 else 'liabilities'}</span><b>{money(abs(net(bs)))}</b></div>"
           f"<div class='tile'><span>Status</span><b class='small'>{status}</b></div></div>",
           "<div class='two'><table><caption>Profit and loss</caption>"]
    out += [f"<tr><td>{E(l)}</td><td class='n'>{money(v)}</td></tr>" for l, v, _ in rows]
    out += [f"<tr class='tot'><td>{'Profit' if result >= 0 else 'Loss'}</td><td class='n'>{money(result)}</td></tr>",
            "</table><table><caption>Balance sheet</caption><tr><th></th><th class='n'>This year</th>"
            "<th class='n'>Last year</th></tr>"]
    out += [f"<tr><td>{l}</td><td class='n'>{money(s * bs.get(k, 0))}</td><td class='n'>"
            f"{money(s * prior.get(k, 0)) if prior else '–'}</td></tr>" for l, k, s in bsrows
            if bs.get(k) or prior.get(k)]
    out += [f"<tr class='tot'><td>Net {'assets' if net(bs) >= 0 else 'liabilities'}</td><td class='n'>{money(net(bs))}"
            f"</td><td class='n'>{money(net(prior)) if prior else '–'}</td></tr></table></div>",
            f"<p class='muted'>Losses carried forward to set against future profits: "
            f"{money(tax['losses_carried_forward'])}. Last year's column includes any correction made this year.</p>"]
    return "".join(out), checks


def due_html(root):
    f = root / "obligations.json"
    data = json.loads(f.read_text()) if f.is_file() else []
    data = data.get("obligations", []) if isinstance(data, dict) else data  # older hand-made shape
    rows = [{**o, "due_date": o.get("due_date") or o.get("due"), "description": o.get("description") or o.get("name")}
            for o in data if isinstance(o, dict)]
    rows = [o for o in rows if o["due_date"] and (o.get("status") or "").lower() not in DONE]
    if not rows:
        return "<p class='muted'>Nothing outstanding.</p>"
    today, out = date.today(), ["<table>"]
    for o in sorted(rows, key=lambda o: o["due_date"])[:6]:
        days = (date.fromisoformat(o["due_date"]) - today).days
        cls = "neg" if days < 0 else ("warn" if days <= 30 else "")
        when = f"{-days} days overdue" if days < 0 else ("today" if days == 0 else f"in {days} days")
        out.append(f"<tr><td>{E(o.get('description') or o.get('type', ''))}</td><td class='n'>"
                   f"{date.fromisoformat(o['due_date']):%d %b %Y}</td><td class='n {cls}'>{when}</td></tr>")
    return "".join(out) + "</table>"


def waiting_html(root):
    f = root / "status.json"
    s = json.loads(f.read_text()) if f.is_file() else {}
    out = [f"<p>{E(s['summary'])}</p>"] if s.get("summary") else []
    items = []
    for w in s.get("waiting", []):
        link = w.get("link") or {}
        a = f" <a href='{E(link['href'])}'>{E(link.get('label', 'Open'))}</a>" if link.get("href") else ""
        items.append(f"<li><b>{E(w.get('on', ''))}:</b> {E(w.get('item', ''))}{a}</li>")
    return "".join(out) + (f"<ul>{''.join(items)}</ul>" if items else "<p class='muted'>Nothing waiting.</p>")


CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1b;--muted:#6b6b66;--line:#e3e2dd;--in:#2e8b57;--out:#c0473a;--cash:#2f5fb3;--warn:#a86a00}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#20201e;--ink:#eceae4;--muted:#a3a19a;--line:#34332f;--in:#5cc08a;--out:#e07a6d;--cash:#7ea6f0;--warn:#e0a84a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 48px}h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:0 0 12px}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin-top:16px}
.muted{color:var(--muted);font-size:13px}.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:16px}
.tile{border:1px solid var(--line);border-radius:8px;padding:12px}.tile span{display:block;color:var(--muted);font-size:13px}.tile b{font-size:22px}.tile b.small{font-size:16px}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}table{width:100%;border-collapse:collapse}
caption{text-align:left;font-weight:600;padding-bottom:6px}td,th{padding:6px 4px;border-bottom:1px solid var(--line);text-align:left;font-weight:normal}
th{color:var(--muted);font-size:13px}.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.tot td{font-weight:600}
.pos{color:var(--in)}.neg{color:var(--out)}.warn{color:var(--warn)}svg{width:100%;height:auto}
rect.in{fill:var(--in)}rect.out{fill:var(--out)}.axis{stroke:var(--line)}.cashline{fill:none;stroke:var(--cash);stroke-width:2}.cash{fill:var(--cash)}
.lbl{fill:var(--muted);font-size:11px;text-anchor:middle}.lbl.end{text-anchor:end}.legend{font-size:13px;color:var(--muted)}
.k{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 12px}.k.in{background:var(--in)}.k.out{background:var(--out)}.k.cash{background:var(--cash)}
a{color:var(--cash)}li{margin:4px 0}footer{margin-top:24px;font-size:12px;color:var(--muted);text-align:center}
"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    entity_id = sys.argv[1]
    root = b.books_root() / entity_id
    ent = b.entity(entity_id)
    years = sorted(p.parent.name for p in (root / "filed").glob("FY*/inputs.json"))
    fy = sys.argv[2] if len(sys.argv) > 2 else (years[-1] if years else None)
    if fy and (root / "filed" / fy / "inputs.json").is_file():
        pj = root / "filed" / fy / "period.json"
        filed = pj.is_file() and json.loads(pj.read_text()).get("match_status") == "filed"
        acc, checks = accounts_html(fy, draft(entity_id, fy), filed)
    else:
        acc, checks = "<p class='muted'>No year-end started yet.</p>", []
        fy = fy or b.fy_label(date.today().isoformat(), int(ent.get("year_end_month") or 12))
    check_html = ("<ul>" + "".join(f"<li>{E(c)}</li>" for c in checks) + "</ul>") if checks else \
        "<p class='muted'>No unusual results.</p>"
    mark, page = b.maker_mark()
    page_html = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' "
            f"content='width=device-width,initial-scale=1'><title>{E(ent.get('name', entity_id))} accounts</title>"
            f"<style>{CSS}</style></head><body><main><h1>{E(ent.get('name', entity_id))}</h1>"
            f"<p class='muted'>Built {date.today():%d %b %Y} from the books on this computer. It doesn't update "
            f"itself: ask your agent to rebuild it after the books change.</p>"
            f"<section><h2>The year at a glance: {E(fy)}</h2>{acc}</section>"
            f"<section><h2>Money in and out by month</h2>{chart(monthly(entity_id, ent, fy))}</section>"
            f"<div class='two'><section><h2>Coming up</h2>{due_html(root)}</section>"
            f"<section><h2>Waiting on</h2>{waiting_html(root)}</section></div>"
            f"<section><h2>Worth a second look</h2>{check_html}</section>"
            f"<footer>{E(mark)} · <a href='{E(page)}'>{E(page.split('//')[1].rstrip('/'))}</a> · software that "
            f"helps you prepare your own accounts; not accountancy advice.</footer></main></body></html>")
    out = root / "dashboard.html"
    out.write_text(page_html)
    print(f"written {out.resolve()}")
    print(f"Tell the director: open {out.resolve()} in your browser (double-click it, or right-click it in VS Code "
          f"and choose 'Reveal in File Explorer' / 'Reveal in Finder'). It stays on this computer.")


if __name__ == "__main__":
    main()

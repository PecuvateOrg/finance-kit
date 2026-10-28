"""Draft a company's micro-entity accounts and corporation tax figures from its trial balance.

Usage: python3 engine/scripts/build_accounts.py <entity_id> <FY> [--write]
  prints the draft and every check; --write saves, in books/<id>/filed/<FY>/ (only if every check passes):
    accounts.json      the figures in the filing software's `financials` shape, plus the tax computation
    period.json        headline figures, "match_status": "draft" (keeps any existing "notes")
    draft_accounts.md  the one-page draft for the director
  A period.json already marked "filed" is never overwritten: the draft is compared with it instead.

Rebuilds the trial balance with build_tb.build (so its checks run again) and checks it equals the saved
trial_balance.csv. Every account's "class" in accounts/account_map.json decides its line:
  P&L      revenue -> turnover, other_income, direct_costs -> cost of sales, staff_costs, depreciation,
           expense -> other charges, tax -> tax on profit
  balance  fixed_asset, current_asset, bank (debit balance = current asset, credit = creditor),
           current_liability -> creditors within one year, accruals -> accruals and deferred income,
           equity (960 = profit and loss reserve, the rest = share capital)
Last year's column comes from the opening balances (restated, if a correction went through reserves).

inputs.json needs "period_start" and "period_end" (YYYY-MM-DD) and gains an "accounts" block:
  {"average_employees": <n, directors count>, "trading_losses_bf": <from the company's own earlier years>,
   "associated_companies": <n>,
   "decisions": {"<closing_stock|use_of_home|mileage|accruals|trading_losses_bf|associated_companies|going_concern>":
     {"answer": "...", "decided_by": "director", "date": "YYYY-MM-DD"}},   (every one; going_concern only when
     net liabilities. The draft stops until each has the director's answer: the agent never assumes them)
   "prior_period_adjustment": {"amount": <effect on reserves b/f, negative reduces them>, "tax_effect": <added
     to taxable profit, negative = deductible>, "note": "...", "decided_by": "director|agent"},   (if any)
   "tax_adjustments": [{"amount": <added to taxable profit>, "code": "<account, if it adds one back>",
     "note": "...", "decided_by": "..."}]}  (if any; 420 Entertainment needs one: client entertainment is added
     back in full, staff entertainment is allowed, so amount 0 with a note)

Tax: small profits rate, marginal relief and main rate (limits shared between associated companies and
scaled to the period's length), after trading losses b/f. Not covered, so the script stops: fixed assets or
depreciation (capital allowances), periods starting before 2023-04-01, periods longer than 12 months.
"""
import csv, json, sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import books_io as b
from build_tb import build, D, RE, DLA

PL = {"revenue": "turnover", "other_income": "other_income", "direct_costs": "cost_of_sales",
      "staff_costs": "staff_costs", "depreciation": "depreciation", "expense": "other_operating_expenses",
      "tax": "tax"}
BS = {"fixed_asset", "current_asset", "bank", "current_liability", "accruals", "equity"}
SMALL, MAIN, LOWER, UPPER = Decimal("0.19"), Decimal("0.25"), Decimal(50000), Decimal(250000)
R = lambda v: v.quantize(Decimal("0.01"), ROUND_HALF_UP)
# Facts only the director knows; each needs {"answer": "...", "decided_by": "director"} in accounts.decisions.
DECISIONS = ["closing_stock", "use_of_home", "mileage", "accruals", "trading_losses_bf", "associated_companies"]


def balance_sheet(bal, cls):
    """bal: {code: debit-positive balance}. Returns the micro balance sheet, every figure positive."""
    s = dict.fromkeys(["fixed_assets", "current_assets", "creditors_within_one_year",
                       "accruals_and_deferred_income", "share_capital", "profit_and_loss_account"], Decimal(0))
    for code, v in bal.items():
        c = cls.get(code)
        if c == "fixed_asset":
            s["fixed_assets"] += v
        elif c == "current_asset" or (c == "bank" and v > 0):
            s["current_assets"] += v
        elif c in ("current_liability", "bank"):
            s["creditors_within_one_year"] -= v
        elif c == "accruals":
            s["accruals_and_deferred_income"] -= v
        elif c == "equity":
            s["profit_and_loss_account" if code == RE else "share_capital"] -= v
    return s


def corporation_tax(profit, start, end, associated):
    days = (end - start).days + 1
    share = Decimal(min(days, 365)) / Decimal(365) / (associated + 1)  # a full year gets the full limits
    lower, upper = LOWER * share, UPPER * share
    if profit <= 0:
        return Decimal(0), Decimal(0)
    if profit <= lower:
        return R(profit * SMALL), Decimal(0)
    if profit >= upper:
        return R(profit * MAIN), Decimal(0)
    relief = R((upper - profit) * Decimal(3) / Decimal(200))
    return R(profit * MAIN) - relief, relief


def draft(entity_id, fy):
    root = b.books_root() / entity_id
    out = root / "filed" / fy
    lines, dr, cr, problems, opening, extra = build(entity_id, fy)
    warnings = list(extra["warnings"])
    chart = json.loads((root / "accounts" / "account_map.json").read_text())["accounts"]
    cls = {a["code"]: a.get("class") for a in chart}
    names = {a["code"]: a["name"] for a in chart}
    inputs = json.loads((out / "inputs.json").read_text())
    acc = inputs.get("accounts", {})
    for k in ("period_start", "period_end"):
        if k not in inputs:
            problems.append(f"inputs.json {k} missing (YYYY-MM-DD)")
    for k in ("average_employees", "trading_losses_bf", "associated_companies"):
        if k not in acc:
            problems.append(f"inputs.json accounts.{k} missing (ask the director; see 50_year_end step 8)")

    tb_csv = out / "trial_balance.csv"
    if not tb_csv.exists():
        problems.append("no trial_balance.csv: run build_tb.py --write first")
    else:
        saved = {r["source_code"]: D(r["debit"]) - D(r["credit"]) for r in csv.DictReader(open(tb_csv))}
        if saved != {c: v for c, _, v in lines}:
            problems.append("trial_balance.csv differs from the books: rerun build_tb.py --write")

    bal = {c: v for c, _, v in lines}
    for code in set(bal) | set(opening):
        c = cls.get(code)
        if c not in PL and c not in BS:
            problems.append(f"{code} {names.get(code, '?')}: class '{c}' isn't a P&L or balance sheet class")
        if c in ("fixed_asset", "depreciation") and (bal.get(code) or opening.get(code)):
            problems.append(f"{code} {names.get(code)}: fixed assets need capital allowances, not in the kit yet")

    pl = dict.fromkeys(PL.values(), Decimal(0))
    for code, v in bal.items():
        if cls.get(code) in PL:
            pl[PL[cls[code]]] += v
    turnover, other_income = -pl["turnover"], -pl["other_income"]
    before_tax = turnover + other_income - pl["cost_of_sales"] - pl["staff_costs"] - pl["depreciation"] \
        - pl["other_operating_expenses"]
    result = before_tax - pl["tax"]

    # The TB's 960 is last year's reserve; add this year's result to close it.
    now = balance_sheet(bal, cls)
    now["profit_and_loss_account"] += result
    prior = balance_sheet({**opening, RE: -sum(opening.values(), Decimal(0))}, cls)
    net = lambda s: s["fixed_assets"] + s["current_assets"] - s["creditors_within_one_year"] \
        - s["accruals_and_deferred_income"]
    for label, s in (("this year", now), ("last year", prior)):
        if net(s) != s["share_capital"] + s["profit_and_loss_account"]:
            problems.append(f"balance sheet {label}: net assets {net(s)} != capital and reserves "
                            f"{s['share_capital'] + s['profit_and_loss_account']}")

    warnings += sense_checks(bal, opening, cls, names, turnover, pl, result)

    ppa = acc.get("prior_period_adjustment") or {}
    # The opening position, before any correction through reserves, must be last year's accounts as filed.
    filed = (inputs.get("prior_year") or {}).get("filed") or {}
    as_filed = {"share_capital": prior["share_capital"],
                "profit_and_loss_account": prior["profit_and_loss_account"] - D(ppa.get("amount")),
                "net_assets": net(prior) - D(ppa.get("amount"))}
    for k, v in as_filed.items():
        if k in filed and v != D(filed[k]):
            problems.append(f"opening {k.replace('_', ' ')} {v} is not last year's filed {D(filed[k])}: fix the "
                            f"opening balances from the filed accounts, or record a prior_period_adjustment")

    decisions = acc.get("decisions") or {}
    needed = DECISIONS + (["going_concern"] if net(now) < 0 else [])
    for k in needed:
        d = decisions.get(k) or {}
        if not d.get("answer") or d.get("decided_by") != "director":
            problems.append(f"decisions.{k}: needs the director's answer (decided_by: director). Ask them; never "
                            f"assume it (50_year_end step 8)")
    if as_filed["profit_and_loss_account"] < 0 and not D(acc.get("trading_losses_bf")):
        warnings.append(f"Last year's reserves were in deficit ({as_filed['profit_and_loss_account']}) but trading "
                        f"losses b/f are nil: check last year's CT600 for losses carried forward before filing")
    if ppa and not all(k in ppa for k in ("amount", "tax_effect", "decided_by")):
        problems.append("prior_period_adjustment needs amount, tax_effect and decided_by (50_year_end step 7)")
    taxable = before_tax + D(ppa.get("tax_effect")) + sum((D(t["amount"]) for t in acc.get("tax_adjustments", [])),
                                                         Decimal(0))
    losses_bf = D(acc.get("trading_losses_bf"))
    used = min(losses_bf, max(taxable, Decimal(0)))
    chargeable = max(taxable, Decimal(0)) - used
    losses_cf = losses_bf - used + max(-taxable, Decimal(0))
    if bal.get("420") and "420" not in {t.get("code") for t in acc.get("tax_adjustments", [])}:
        problems.append("420 Entertainment has a balance: add a tax_adjustments entry with code 420 (client "
                        "entertainment is added back; staff entertainment is allowed, amount 0)")
    start = date.fromisoformat(inputs.get("period_start") or "1900-01-01")
    end = date.fromisoformat(inputs.get("period_end") or "1900-01-01")
    dated = "period_start" in inputs and "period_end" in inputs
    if dated and start < date(2023, 4, 1):
        problems.append("period starts before 2023-04-01: tax rates differ, not in the kit")
    if dated and (end - start).days + 1 > 366:
        problems.append("period longer than 12 months: two tax periods, not in the kit")
    ct, relief = corporation_tax(chargeable, start, end, int(acc.get("associated_companies") or 0))
    if ct != pl["tax"]:
        problems.append(f"tax charged in the books is {pl['tax']} but the computation gives {ct}: add an "
                        f"adjustment (debit the tax account, credit 830) to inputs.json, then rerun build_tb.py")

    f = lambda v: float(R(v))
    financials = {
        "profit_and_loss": {k: f(v) for k, v in (("turnover", turnover), ("cost_of_sales", pl["cost_of_sales"]),
                            ("staff_costs", pl["staff_costs"]), ("depreciation", pl["depreciation"]),
                            ("other_operating_expenses", pl["other_operating_expenses"]),
                            ("other_income", other_income))},
        "balance_sheet": {k: f(v) for k, v in now.items() if v or k != "accruals_and_deferred_income"},
        "average_employees": acc.get("average_employees"),
        "losses": {"brought_forward": f(losses_bf)},
    }
    if any(opening.values()):
        financials["prior_year"] = {k: f(v) for k, v in prior.items()
                                    if v or k != "accruals_and_deferred_income"}
    tax = {"profit_before_tax": f(before_tax), "prior_period_adjustment_tax_effect": f(D(ppa.get("tax_effect"))),
           "tax_adjustments": acc.get("tax_adjustments", []), "taxable_profit": f(chargeable),
           "losses_used": f(used), "losses_carried_forward": f(losses_cf), "marginal_relief": f(relief),
           "corporation_tax": f(ct), "associated_companies": acc.get("associated_companies")}
    period = {"entity_id": entity_id, "period_start": inputs.get("period_start"), "period_end": inputs.get("period_end"),
              "prepared_by": "agent", "accounts_basis": "FRS105_micro", "turnover": f(turnover),
              "profit_loss": f(result), "current_assets": f(now["current_assets"]),
              "creditors_within_one_year": -f(now["creditors_within_one_year"] + now["accruals_and_deferred_income"]),
              "net_assets": f(net(now)), "prior_period_adjustment": f(D(ppa.get("amount"))),
              "taxable_profit": f(chargeable), "ct_liability": f(ct), "trading_losses_bf": f(losses_bf),
              "trading_losses_cf": f(losses_cf), "tb_total": f(dr), "match_status": "draft"}
    dla = ("835", opening.get("835", Decimal(0)), bal.get("835", Decimal(0)))
    md = one_pager(b.entity(entity_id), inputs, financials, tax, period, now, prior, ppa, dla, lines, names, cls,
                   warnings, extra["auto"])
    return {"financials": financials, "tax": tax}, period, md, problems, warnings


def sense_checks(bal, opening, cls, names, turnover, pl, result):
    """Results that are possible but usually mean a missing or miscoded line. Shown to the director, not blocking."""
    out = []
    if turnover > 0 and pl["cost_of_sales"] > turnover:
        out.append(f"Cost of sales ({pl['cost_of_sales']}) is more than turnover ({turnover}): check for stock "
                   f"still on hand or sales coded elsewhere")
    if turnover < 0:
        out.append(f"Turnover is negative ({turnover}): refunds or fees are probably coded to sales")
    for code, v in bal.items():
        c = cls.get(code)
        if c == "current_asset" and v < 0:
            out.append(f"{code} {names.get(code)} is an asset but has a credit balance ({v})")
        if c in ("current_liability", "accruals") and v > 0 and code != DLA:
            out.append(f"{code} {names.get(code)} is a liability but has a debit balance ({v})")
    cash = lambda d: sum((v for k, v in d.items() if cls.get(k) == "bank"), Decimal(0))
    moved = cash(bal) - cash(opening)
    if result > 0 and moved < -result:
        out.append(f"A profit of {result} but cash fell by {-moved}: check for sales missing from the books or "
                   f"costs counted twice")
    if result < 0 and moved > -result:
        out.append(f"A loss of {-result} but cash rose by {moved}: check for income coded as a transfer or loan")
    return out


def one_pager(ent, inputs, fin, tax, period, now, prior, ppa, dla, lines, names, cls, warnings, auto):
    m = lambda v: f"({abs(v):,.2f})" if v < 0 else f"{abs(v):,.2f}"
    pl, end = fin["profit_and_loss"], inputs.get("period_end")
    result = Decimal(str(period["profit_loss"]))
    out = [f"# {ent.get('name', ent['id'])}: draft accounts, year to {end}", "",
           f"**Status:** draft for the director's approval, generated by `engine/scripts/build_accounts.py` from "
           f"the books. If the books change, regenerate it; never edit a figure here.", "",
           "## 1. Result", "",
           f"**A {'profit' if result >= 0 else 'loss'} of £{abs(result):,.2f}.** "
           + (f"Corporation tax: **£{tax['corporation_tax']:,.2f}**." if tax["corporation_tax"]
              else "No corporation tax is payable.")
           + (f" Losses of £{tax['losses_carried_forward']:,.2f} carry forward against future profits."
              if tax["losses_carried_forward"] else ""), "",
           "| Profit and loss | £ |", "|---|---:|", f"| Turnover | {m(pl['turnover'])} |"]
    if pl["other_income"]:
        out.append(f"| Other income | {m(pl['other_income'])} |")
    for code, name, v in lines:
        if cls.get(code) in ("direct_costs", "staff_costs", "depreciation", "expense", "tax"):
            out.append(f"| {names.get(code, name)}{' (credit, reduces costs)' if v < 0 else ''} | {m(-v)} |")
    out += [f"| **{'Profit' if result >= 0 else 'Loss'} for the year** | **{m(result)}** |", "",
            f"## 2. Balance sheet at {end}", "",
            ("Last year's column is restated: it includes the correction to last year (section 3), so it differs "
             "from the accounts filed last year. That is the figure to file as the comparative." if ppa else
             "Last year's column is last year's accounts as filed."), "",
            "| | This year £ | Last year £ |", "|---|---:|---:|"]
    rows = [("Fixed assets", "fixed_assets", 1), ("Current assets", "current_assets", 1),
            ("Creditors: due within one year", "creditors_within_one_year", -1),
            ("Accruals and deferred income", "accruals_and_deferred_income", -1)]
    for label, k, sign in rows:
        if now[k] or prior[k]:
            out.append(f"| {label} | {m(sign * now[k])} | {m(sign * prior[k])} |")
    net = lambda s: s["share_capital"] + s["profit_and_loss_account"]
    out += [f"| **Net {'assets' if net(now) >= 0 else 'liabilities'}** | **{m(net(now))}** | **{m(net(prior))}** |",
            f"| Share capital | {m(now['share_capital'])} | {m(prior['share_capital'])} |",
            f"| Profit and loss reserve | {m(now['profit_and_loss_account'])} | {m(prior['profit_and_loss_account'])} |",
            "", "## 3. Proof that it adds up", "", "| | £ |", "|---|---:|"]
    if ppa:
        out += [f"| Reserves at the start, as filed last year | {m(prior['profit_and_loss_account'] - D(ppa['amount']))} |",
                f"| Correction to last year ({ppa.get('note', '')}) | {m(D(ppa['amount']))} |"]
    out += [f"| Reserves at the start{', restated' if ppa else ''} | {m(prior['profit_and_loss_account'])} |",
            f"| {'Profit' if result >= 0 else 'Loss'} for the year | {m(result)} |",
            f"| **Reserves at the end** | **{m(now['profit_and_loss_account'])}** |", "",
            f"The trial balance totals £{period['tb_total']:,.2f} on each side.", "",
            "## 4. Director's loan account", "",
            f"Start of year: {owed(dla[1])}. End of year: **{owed(dla[2])}**.", "",
            "## 5. Points for the director", ""]
    points = [f"**Check.** {w}" for w in warnings]
    if net(now) < 0:
        points.append("**Going concern.** The company owes more than it holds. Signing the accounts confirms it can "
                      "carry on, usually because the director won't ask for their loan back before other creditors "
                      "are paid.")
    if dla[2] > 0:
        points.append(f"**You owe the company £{dla[2]:,.2f}.** If it isn't repaid within 9 months of the year end, "
                      "the company pays s455 tax (33.75% of the amount), refunded when the loan is repaid. A loan "
                      "over £10,000 can also be a taxable benefit for you.")
    for adj in auto:
        points.append(f"Calculated from the records: {adj['note']} (£{D(adj['amount']):,.2f}).")
    for adj in inputs.get("adjustments", []):
        if adj.get("decided_by") == "director":
            points.append(f"You decided: {adj['note']} (£{D(adj['amount']):,.2f}).")
    if ppa:
        points.append(f"Correction to last year: {ppa.get('note', '')}. It goes through reserves, so last year "
                      "isn't refiled; its tax effect is " + (f"£{D(ppa.get('tax_effect')):,.2f}."
                                                             if D(ppa.get("tax_effect")) else "nil."))
    out += [f"{i}. {p}" for i, p in enumerate(points, 1)] or ["None."]
    out += ["", "## 6. Tax", "", "| | £ |", "|---|---:|",
            f"| Profit before tax | {m(Decimal(str(tax['profit_before_tax'])))} |",
            f"| Losses brought forward used | ({tax['losses_used']:,.2f}) |",
            f"| Taxable profit | {tax['taxable_profit']:,.2f} |",
            f"| Corporation tax{' (after marginal relief)' if tax['marginal_relief'] else ''} | {tax['corporation_tax']:,.2f} |",
            f"| Losses carried forward | {tax['losses_carried_forward']:,.2f} |", ""]
    mark, page = b.maker_mark()
    out += ["---", f"*{mark} · {page} · software that helps you prepare your own accounts; not accountancy advice.*", ""]
    return "\n".join(out)


def owed(v):
    v = D(v)
    return "nil" if not v else (f"£{-v:,.2f} owed to the director" if v < 0 else f"£{v:,.2f} owed by the director")


def compare(period, filed):
    diffs = [f"{k}: draft {period[k]}, filed {filed[k]}" for k in period
             if k in filed and k != "match_status" and isinstance(period[k], float)
             and abs(period[k] - float(filed[k])) > 0.005]
    return diffs


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    entity_id, fy = sys.argv[1], sys.argv[2]
    accounts, period, md, problems, _ = draft(entity_id, fy)
    print(md)
    print(json.dumps(accounts["financials"], indent=1))
    for p in problems:
        print("FAIL ", p)
    if problems:
        sys.exit(1)
    print("PASS  all checks")
    out = b.books_root() / entity_id / "filed" / fy
    existing = json.loads((out / "period.json").read_text()) if (out / "period.json").exists() else {}
    if existing.get("match_status") == "filed":
        diffs = compare(period, existing)
        for d in diffs:
            print("DIFF ", d)
        print("already filed: nothing written" + ("" if diffs else "; draft equals the filed figures"))
        sys.exit(1 if diffs else 0)
    if "--write" in sys.argv:
        if existing.get("notes"):
            period["notes"] = existing["notes"]
        (out / "accounts.json").write_text(json.dumps(accounts, indent=1) + "\n")
        (out / "period.json").write_text(json.dumps(period, indent=2) + "\n")
        (out / "draft_accounts.md").write_text(md)
        print(f"written {out}/accounts.json, period.json, draft_accounts.md")
        print(f"Tell the director: your draft accounts are in {(out / 'draft_accounts.md').resolve()} "
              f"(open it in VS Code and press Ctrl+Shift+V, Cmd+Shift+V on a Mac, to read it formatted). "
              f"For charts, run build_dashboard.py.")


if __name__ == "__main__":
    main()

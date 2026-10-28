"""Fetch last year's filed accounts from Companies House and record them as the opening position's evidence.

Usage: python3 engine/scripts/fetch_prior_year.py <entity_id> <FY> [--write]
  prints what it found; --write saves the filed document to books/<id>/filed/<last FY>/companies_house_accounts.xhtml
  and sets inputs.json "prior_year" (only if every check passes). Needs period_start in books/<id>/filed/<FY>/inputs.json.

Reads the company's public filing history (no API key), finds the accounts made up to the day before period_start,
and downloads their tagged (iXBRL) version. Net assets come from the tags. Micro-entity accounts tag only total
equity, so share capital comes from entity.json "share_capital": {"amount": n, "source": "<statement of capital,
with date>"}, and the profit and loss reserve is net assets less share capital.

Checks (exit 1 on any failure): accounts for that date are on the register; they were filed digitally (a paper
filing has no tags: ask the director for the figures instead); the document's company number is this company's;
its balance sheet date is the one expected; share capital has a source.
"""
import functools, html, json, re, sys, urllib.error, urllib.request
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import books_io as b

SITE = "https://find-and-update.company-information.service.gov.uk"
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}


@functools.lru_cache(maxsize=None)  # the filing history is read twice: this year's check and last year's accounts
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "finance-kit (prior-year fetch)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        sys.exit(f"FAIL  Companies House answered {e.code} for {url}" + (": check the company number in entity.json"
                                                                         if e.code == 404 else ""))
    except urllib.error.URLError as e:
        sys.exit(f"FAIL  can't reach Companies House ({e.reason}): try again, or ask the director for last year's "
                 f"accounts")


def find_accounts(number, made_up_to):
    """The filing-history row for accounts made up to that date: (description, tagged-document path or None)."""
    for page in range(1, 6):
        rows = re.findall(r"<tr>(.*?)</tr>", get(f"{SITE}/company/{number}/filing-history?category=accounts&page={page}"), re.S)
        if len(rows) <= 1:
            break
        for row in rows:
            text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", row)))
            m = re.search(r"made up to (\d{1,2}) (\w+) (\d{4})", text)
            if m and date(int(m[3]), MONTHS[m[2]], int(m[1])) == made_up_to:
                tagged = re.search(r'href="([^"]+document\?format=xhtml[^"]*)"', row)
                return text[:120].strip(), html.unescape(tagged[1]) if tagged else None
    return None, None


def facts(doc):
    """{(tag, date): value} for undimensioned figures; dimensioned contexts are left out."""
    ctx = {}
    for cid, body in re.findall(r'<xbrli:context id="([^"]+)">(.*?)</xbrli:context>', doc, re.S):
        if "dimension=" not in body:
            d = re.findall(r"<xbrli:(?:instant|endDate)>([^<]+)<", body)
            ctx[cid] = d[-1].strip() if d else None
    out = {}
    for attrs, val in re.findall(r"<ix:nonFraction([^>]*)>([^<]*)</ix:nonFraction>", doc):
        a = dict(re.findall(r'([\w:]+)="([^"]*)"', attrs))
        if a.get("contextRef") in ctx:
            v = Decimal(val.replace(",", "") or 0).scaleb(int(a.get("scale", 0)))
            out[(a["name"], ctx[a["contextRef"]])] = -v if a.get("sign") == "-" else v
    text = {n: re.sub(r"<[^>]+>", "", v).strip()
            for n, v in re.findall(r'<ix:nonNumeric[^>]*name="([^"]+)"[^>]*>(.*?)</ix:nonNumeric>', doc, re.S)}
    return out, text


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    entity_id, fy = sys.argv[1], sys.argv[2]
    ent = b.entity(entity_id)
    root = b.books_root() / entity_id
    inputs_file = root / "filed" / fy / "inputs.json"
    inputs = json.loads(inputs_file.read_text()) if inputs_file.is_file() else {}
    if not inputs.get("period_start"):
        sys.exit(f"FAIL  {inputs_file.relative_to(root.parent)} needs period_start first")
    made_up_to = date.fromisoformat(inputs["period_start"]) - timedelta(days=1)
    number, problems = ent.get("company_number") or "", []

    # 50_year_end step 0: this year's accounts already on the register means filing again would duplicate them.
    period = root / "filed" / fy / "period.json"
    already = inputs.get("period_end") and find_accounts(number, date.fromisoformat(inputs["period_end"]))[0]
    if already and not (period.is_file() and json.loads(period.read_text()).get("match_status") == "filed"):
        sys.exit(f"FAIL  this year's accounts are already on the register ({already}): don't prepare them to file "
                 f"again. Tell the director, and ask whether the CT600 went in too")

    desc, tagged = find_accounts(number, made_up_to)
    if not desc:
        sys.exit(f"FAIL  no accounts made up to {made_up_to} on the register for {number}: if this is the first year, "
                 f'set prior_year {{"first_year": true}}; otherwise ask the director')
    print(f"found  {desc}")
    if not tagged:
        sys.exit("FAIL  those accounts were filed on paper (no tagged version): ask the director for the figures and "
                 "record prior_year by hand (50_year_end step 7)")
    doc = get(SITE + tagged)
    vals, text = facts(doc)
    end = made_up_to.isoformat()

    filed_number = text.get("bus:UKCompaniesHouseRegisteredNumber", "").replace(" ", "")
    if filed_number.lstrip("0") != number.lstrip("0"):
        problems.append(f"document is for company '{filed_number}', not {number}")
    net = vals.get(("core:NetAssetsLiabilities", end), vals.get(("core:Equity", end)))
    if net is None:
        problems.append(f"no net assets tagged at {end}: the balance sheet date doesn't match; check the filing")
    sc = ent.get("share_capital") or {}
    if sc.get("amount") is None or not sc.get("source"):
        problems.append('entity.json has no share_capital {"amount": n, "source": "..."}: take it from the latest '
                        "statement of capital (incorporation or confirmation statement) or ask the director")

    for (name, d), v in sorted(vals.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        print(f"       {d}  {name.split(':')[1]:52} {v}")
    for p in problems:
        print("FAIL ", p)
    if problems:
        sys.exit(1)

    share = Decimal(str(sc["amount"]))
    prev_fy = b.fy_label(end, int(ent.get("year_end_month") or 12))
    rel = f"filed/{prev_fy}/companies_house_accounts.xhtml"
    prior = {"source": rel, "fetched_from": SITE + tagged, "fetched": date.today().isoformat(),
             "filed": {"share_capital": float(share), "profit_and_loss_account": float(net - share),
                       "net_assets": float(net)},
             "share_capital_source": sc["source"]}
    print(f"PASS  net assets {net}, share capital {share} ({sc['source']}), profit and loss reserve {net - share}")
    if "--write" in sys.argv:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(doc)
        inputs["prior_year"] = prior
        inputs_file.write_text(json.dumps(inputs, indent=1) + "\n")
        print(f"written {rel} and inputs.json prior_year")


if __name__ == "__main__":
    main()

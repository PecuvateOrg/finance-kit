# Primo Payroll — payroll for up to 10 staff, no API

checked: 2026-11-10 · price: `prices.json` → `primo_essentials_free`, `primo_essentials_50`

**For:** running pay days, payslips and the HMRC reports (FPS/EPS) for an organisation the engine keeps the books for. Free plan: up to 10 employees, leavers included.
**Help:** https://www.primopayroll.co.uk/ · pricing https://www.primopayroll.co.uk/pricing
**Not covered by the engine:** there is no API, so the user runs each pay day in Primo. Confirm on sign-up that the plan covers pension auto-enrolment; if not, the pension provider (e.g. NEST) is set up separately.

**Asks for (from `../rules/payroll_year_end.md`):** the tax year's rates and thresholds, which Primo sets itself; the engine only checks them.

**Engine reads back:** the payroll summary report for each pay run (gross pay, PAYE, employee and employer NI, pension both sides, net pay). The engine posts those totals to the wages, PAYE/NI and pension accounts, then matches the net pay and the HMRC payment to the bank lines.

**Done when:** each FPS shows as accepted in Primo, the posted totals equal the report, and the PAYE/NI liability clears to £0 when HMRC is paid.

# Payroll: each pay day and the year end — tool-neutral

For 2026/27 (6 April 2026 – 5 April 2027). Sources: [GOV.UK rates and thresholds for employers 2026 to 2027](https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027), [payroll annual reporting](https://www.gov.uk/payroll-annual-reporting), [pay PAYE](https://www.gov.uk/pay-paye-tax), [what to report](https://www.gov.uk/guidance/what-payroll-information-to-report-to-hmrc), [Employment Allowance](https://www.gov.uk/claim-employment-allowance), [Pensions Regulator](https://www.thepensionsregulator.gov.uk/en/employers). Checked 2026-11-10; review by 2027-04-06.

## Figures (2026/27)
| Item | Amount |
|---|---|
| Employer's (secondary) National Insurance | 15% above the secondary threshold |
| Secondary threshold | £5,000 a year (£417 a month, £96 a week) |
| Primary threshold (employee NI starts) | £12,570 a year (£1,048 a month) |
| Lower earnings limit | £6,708 a year (£559 a month) |
| Employment Allowance | up to £10,500 off employer's NI a year. Not available if the company's only director is the only employee paid above the secondary threshold |
| Pension: auto-enrolment earnings trigger | £10,000 a year (£833 a month), staff aged 22 to State Pension age |
| Pension: qualifying earnings band | £6,240 – £50,270 a year |
| Pension: minimum contributions | 8% of qualifying earnings in total, at least 3% from the employer (Pensions Regulator; confirm on its contributions page) |

## Each pay day
- Send a Full Payment Submission (FPS) to HMRC **on or before** pay day.
- Send an Employer Payment Summary (EPS) **by the 19th** of the following tax month when there's something to claim or nothing was paid (e.g. Employment Allowance, statutory pay recovery).
- Pay HMRC **by the 22nd** of the next tax month if paying electronically (monthly), or the 22nd after the quarter if paying quarterly.
- Pay pension contributions to the scheme by its due date.

## Year end
| What | When |
|---|---|
| Final FPS of the year (marked final) | on or before the last pay day of the tax year |
| P60 to every employee employed on 5 April | by 31 May |
| Expenses and benefits (P11D / P11D(b)) if any | by 6 July |
| Pension: declaration of compliance (new employer) | within 5 months of the duties start date; re-enrolment every 3 years |

**What the engine does:** works out what each step needs from the payroll tool's reports, posts wages, employer's NI, pension and PAYE owed to the books, and checks the PAYE paid matches HMRC's statement. Running the pay run and sending the FPS is done in the payroll tool (`../tools/`).

# 100 synthetic 18-month calendars: longitudinal red-team report

- Calendar span: January 1, 2025–June 30, 2026 (18 calendar months per case).
- Fictional AI expectation begins October 1, 2025 (nine months before / nine months after).
- 100 distinct synthetic calendars, 15 scenario families, 125,166 events in total.
- All 100 cases passed the longitudinal invariants and scenario-specific assertions after implementation.
- The existing prototype tests and six new longitudinal regression tests also pass.

## Tested patterns
Recorded PTO, sick time, holidays, personal appointments, unavailable blocks, protected breaks, reduced or increased recorded leave, after-hours AI-labeled work, overlapping leave/work, double bookings, team-heavy meetings, tentative/declined events, team-only events, sparse calendars, and changed appointment scheduling.

## Guardrails and limits
Recorded leave and breaks are not proof of leave actually taken, health status, leave entitlement, or leave appropriateness. A before/after difference cannot establish that the AI expectation caused the change. Calendar labels cannot prove AI adoption or actual attendance. Medical appointment titles and diagnoses are neither accepted nor processed; only coarse unavailable categories are used. The longitudinal module is independent of the existing Streamlit app and live LLM path; it does not represent 100 live LLM responses. The generated dataset is synthetic and does not validate generalization to real employee calendars, which may have missing data, inconsistent categories, multiple time zones, overnight events, and different working patterns.

Run: `PYTHONPATH=. python evals/run_18_month_redteam.py`

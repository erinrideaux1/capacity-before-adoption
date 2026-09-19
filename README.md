# Capacity Before Adoption

**A human-centered AI and workforce transformation prototype by Erin Rideaux.**

> Before adding a new priority, have we created capacity for it?

Organizations ask leaders to develop AI capabilities while delivering their existing responsibilities. This prototype turns that people-and-business problem into observable calendar signals and questions for a leader conversation. Blank calendar space is not treated as proven capacity.

## Erin's role

Erin defined the HR diagnostic and human-centered evaluation criteria, guided the scenarios and interpretation boundaries, and developed the executable prototype with AI coding assistance. This portfolio demonstrates organizational transformation judgment applied to AI adoption.

## Explore the prototype

The Streamlit application includes:

- Four-week capacity analysis: occupied time, overlapping invitations, fragmented open time, uninterrupted blocks, protected planning time, and leader-team interactions.
- Three synthetic demonstration calendars, including overlapping commitments and a comparatively open schedule.
- A separate 18-month comparison of recorded breaks, leave, after-hours work, and conflicts with unavailable time.
- Deterministic discovery briefs that work without an API key.
- Optional live-model interpretation of aggregated short-calendar metrics.

The two analysis views use different CSV schemas. The longitudinal view requires a separate upload; example files are in `evals/stress_18_month_calendars/`.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Choose an included scenario to begin. No API key is needed for the deterministic demonstration.

## Validation status

On September 19, 2026, the automated suite passed **44 of 44 tests** on Windows after fixing temporary-file handling in the longitudinal upload flow.

```bash
python -m unittest discover -s evals -p "test_*.py"
```

The package also contains 100 synthetic four-week calendars, 100 synthetic 18-month histories, and offline evaluation reports. Automated checks include arithmetic, overlap handling, sparse-calendar regression, interpretation validation, and simulated UI control flow.

**Not yet verified:** interactive browser behavior, deployment, and actual live-model responses. Mocked model tests and deterministic briefs are not live-model evaluations.

## Human judgment and privacy boundaries

Calendar patterns support discovery, not employee scoring. The prototype cannot establish actual attendance, motivation, health, leave appropriateness, meeting value, causality, or actual AI adoption. Human review remains necessary.

Use synthetic data for portfolio demonstrations. Do not upload real employee calendars to a public demo. Team meeting time is already included in occupied time and must not be counted twice. Team-only events without the leader are context, not deductions from the leader's available time.

The optional live-model pathway sends aggregated numeric short-calendar metrics, not names or event titles. The longitudinal brief remains offline. Output validation checks structure and limited phrases; it does not guarantee safe or accurate interpretation.

## Optional live-model evaluation

Set `OPENAI_API_KEY` privately in your local environment, then run:

```bash
python -m evals.run_live_evaluation
```

API charges may apply. Never commit keys or include them in screenshots. Review all outputs against the diagnostic framework before claiming live-model validation.

## Project structure

- `app.py`: Streamlit demonstration interface
- `analysis/`: deterministic calculations and interpretation modules
- `data/`: short-calendar demo scenarios
- `evals/`: tests, synthetic histories, and offline results
- `framework/diagnostic_framework.md`: HR diagnostic principles
- `PORTFOLIO_NEXT_STEPS.md`: deployment and validation checklist

See `evals/STRESS_TEST_100.md` and `evals/REDTEAM_18_MONTH_REPORT.md` for historical evaluation details. Their test counts reflect the stage at which those reports were written.

**Design principle: Calendar patterns are evidence for discovery, not evidence for judgment.**

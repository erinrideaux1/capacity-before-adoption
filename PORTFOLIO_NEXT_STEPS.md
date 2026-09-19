# Portfolio release checklist

## What exists
- Four-week capacity analysis with deterministic calculations and optional LLM-assisted interpretation.
- Separate 18-month longitudinal comparison with privacy-minimal categories and deterministic interpretation.
- 100 synthetic 18-month calendars, offline stress-test results, and automated regression tests.

## What is not yet verified
- A deployed Streamlit browser session, accessibility and mobile layout.
- 100 real model-generated interpretations; offline deterministic briefs are not live-model evaluations.
- Production suitability, consent governance, or a causal relationship between a new AI expectation and time-use changes.

## Steps requiring the repository owner
1. Create or select a GitHub repository and publish these files. Keep API keys out of Git and use synthetic demonstration data only.
2. Deploy the Streamlit app with `app.py` as entrypoint and `requirements.txt` as dependencies.
3. Optionally provide an API key through a private deployment secret to run live LLM evaluations. Do not commit a key or paste it into public issue threads.
4. Open the deployed URL and verify the short-calendar and longitudinal upload journeys interactively.

## Recommended portfolio wording
"I defined the HR diagnostic and human-centered evaluation criteria, developed an executable prototype with AI coding assistance, and tested deterministic calendar calculations against 100 synthetic 18-month histories. The live-model and deployed-browser evaluations are separate validation steps."

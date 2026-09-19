"""Opt-in real API evaluation. Never prints or stores the API key.

Run: OPENAI_API_KEY=... python -m evals.run_live_evaluation
Live model output requires human review; schema validation is not semantic verification.
"""
import json, os
from pathlib import Path
from analysis.capacity_analysis import analyze_calendar
from analysis.llm_interpretation import interpret_with_llm

ROOT=Path(__file__).resolve().parents[1]
KEY=os.environ.get('OPENAI_API_KEY')
if not KEY:
    raise SystemExit('No OPENAI_API_KEY set; no live evaluation performed.')
for scenario in ('maya_calendar','maya_complex_calendar','daniel_calendar'):
    _,metrics=analyze_calendar(ROOT/'data'/f'{scenario}.csv')
    try:
        brief=interpret_with_llm(metrics,KEY)
        print(json.dumps({'scenario':scenario,'schema_and_basic_guardrails':'passed',
                          'metrics':metrics,'model_brief':brief},indent=2))
    except Exception as exc:
        print(json.dumps({'scenario':scenario,'status':'error','error':str(exc)}))

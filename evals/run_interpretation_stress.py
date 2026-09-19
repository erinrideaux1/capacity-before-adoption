"""Offline 100-calendar longitudinal interpretation stress test (not live LLM)."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'))
from longitudinal import analyze_longitudinal
from longitudinal_brief import make_longitudinal_brief
paths=sorted((ROOT/'evals'/'stress_18_month_calendars').glob('*.csv'))
assert len(paths)==100, f'Expected 100, got {len(paths)}'
results=[]
for path in paths:
    periods=analyze_longitudinal(path,'2025-10-01')
    brief=make_longitudinal_brief(periods)
    blob=json.dumps(brief).lower()
    assert len(brief['observations'])>=3
    assert len(brief['discovery_questions'])>=2
    assert 'does not establish' in blob
    assert 'do not infer medical status' in blob
    assert not any(x in blob for x in ('diagnosis:','is unhealthy','misused sick leave','caused burnout','failed to take appropriate sick leave'))
    results.append({'calendar':path.name,'status':'passed','before':periods['before'],'after':periods['after'],'brief':brief})
out=ROOT/'evals'/'offline_interpretation_100_results.json'
out.write_text(json.dumps(results,indent=2))
print(f'OFFLINE_LONGITUDINAL_INTERPRETATION: {len(results)}/100 passed')
print(f'RESULTS: {out}')

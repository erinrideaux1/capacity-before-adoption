"""Reproducible 100-calendar, 18-month synthetic stress test."""
import csv, random, json, os
from datetime import date,timedelta
from pathlib import Path
from analysis.longitudinal import analyze_longitudinal

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'stress_18_month_calendars'; DATA.mkdir(exist_ok=True)
START=date(2025,1,1); END=date(2026,6,30); CHANGE=date(2025,10,1)
FIELDS=['date','start_min','end_min','category','status','leader_attending']
SCENARIOS=['baseline','leave_protected','leave_declines','leave_increases','after_hours_rises',
 'breaks_decline','appointments_rescheduled','team_heavy','double_booked','sparse',
 'ai_labeled','sick_time_variable','holidays','conflicting_leave_work','mixed_complex']

def event(d,a,b,cat,status='confirmed',leader='yes'):
 return dict(date=d.isoformat(),start_min=a,end_min=b,category=cat,status=status,leader_attending=leader)

def generate(i):
 rng=random.Random(920260+i); scenario=SCENARIOS[(i-1)%len(SCENARIOS)]
 path=DATA/f'calendar_{i:03d}_{scenario}.csv'; rows=[]; d=START
 while d<=END:
  if d.weekday()<5:
   after=d>=CHANGE; month_index=(d.year-2025)*12+d.month
   holiday=(d.month,d.day) in ((1,1),(7,4),(12,25))
   pto=(d.month in (3,7,12) and d.day in (10,11,12))
   if scenario=='leave_declines' and after: pto=False
   if scenario=='leave_increases' and after and d.day in (10,11): pto=True
   sick=(d.day==17 and d.month in (2,5,8,11))
   if scenario=='sick_time_variable': sick=(d.day in (17,18) and month_index%3==0)
   if holiday: rows.append(event(d,480,1050,'holiday'))
   elif pto: rows.append(event(d,480,1050,'pto'))
   elif sick: rows.append(event(d,480,1050,'sick'))
   else:
    if scenario!='sparse' or d.day%3==0:
     rows.append(event(d,540,600,'team' if scenario=='team_heavy' else 'meeting'))
     rows.append(event(d,660,720,'customer'))
     if scenario in ('double_booked','mixed_complex'): rows.append(event(d,570,630,'team'))
     if scenario in ('ai_labeled','mixed_complex') and after: rows.append(event(d,840,900,'ai'))
    if not (scenario=='breaks_decline' and after):rows.append(event(d,750,780,'break'))
    if d.day==15:
     # Sensitive reason is intentionally absent from input; category is all we need.
     rows.append(event(d,900,990,'personal_appointment'))
    if scenario=='appointments_rescheduled' and after and d.day==16:rows.append(event(d,900,990,'personal_appointment'))
    if scenario in ('after_hours_rises','mixed_complex') and after:rows.append(event(d,1080,1140,'ai'))
    if scenario=='conflicting_leave_work' and d.day==16:
     rows.append(event(d,840,960,'unavailable'));rows.append(event(d,900,930,'meeting'))
    if rng.random()<.08:rows.append(event(d,900,960,'team','tentative'))
    if rng.random()<.04:rows.append(event(d,900,960,'meeting','declined'))
    if rng.random()<.04:rows.append(event(d,900,960,'team','confirmed','no'))
  d+=timedelta(days=1)
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
 return scenario,path,len(rows)

def run():
 output=[];failures=[]
 for i in range(1,101):
  sc,path,n=generate(i)
  try:
   r=analyze_longitudinal(path,CHANGE.isoformat()); b,a=r['before'],r['after']
   assert b['weeks_observed']>0 and a['weeks_observed']>0
   for x in (b,a):
    assert x['available_window_hours']>=0
    assert x['available_window_hours']<=x['working_window_hours']+0.01
    assert abs(x['available_window_hours']+x['unavailable_hours']-x['working_window_hours'])<.01
    assert x['work_within_window_hours']<=x['available_window_hours']+.01
   if sc=='leave_declines':assert a['recorded_leave_days_per_week']<b['recorded_leave_days_per_week']
   if sc=='leave_increases':assert a['recorded_leave_days_per_week']>b['recorded_leave_days_per_week']
   if sc=='after_hours_rises':assert a['after_hours_per_week']>b['after_hours_per_week']
   if sc=='breaks_decline':assert a['recorded_break_days_per_week']<b['recorded_break_days_per_week']
   if sc=='conflicting_leave_work':assert a['work_during_recorded_leave_hours']>0
   output.append(dict(id=i,scenario=sc,events=n,status='pass',before=b,after=a))
  except Exception as e:
   failures.append(dict(id=i,scenario=sc,error=str(e)));output.append(dict(id=i,scenario=sc,events=n,status='fail',error=str(e)))
 with (ROOT/'stress_18_month_results.json').open('w') as f:json.dump(output,f,indent=2)
 with (ROOT/'stress_18_month_summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['id','scenario','events','status','before_leave_days_per_week','after_leave_days_per_week','before_break_days_per_week','after_break_days_per_week','before_after_hours_per_week','after_after_hours_per_week']);w.writeheader()
  for r in output:
   b=r.get('before',{});a=r.get('after',{})
   w.writerow(dict(id=r['id'],scenario=r['scenario'],events=r['events'],status=r['status'],before_leave_days_per_week=b.get('recorded_leave_days_per_week'),after_leave_days_per_week=a.get('recorded_leave_days_per_week'),before_break_days_per_week=b.get('recorded_break_days_per_week'),after_break_days_per_week=a.get('recorded_break_days_per_week'),before_after_hours_per_week=b.get('after_hours_per_week'),after_after_hours_per_week=a.get('after_hours_per_week')))
 print('calendars',len(output),'passed',len(output)-len(failures),'failed',len(failures),'events',sum(r['events'] for r in output))
 print('scenario_counts', {s:sum(r['scenario']==s for r in output) for s in SCENARIOS})
 if failures:print('failures',failures[:10])
 return len(failures)
if __name__=='__main__':raise SystemExit(bool(run()))

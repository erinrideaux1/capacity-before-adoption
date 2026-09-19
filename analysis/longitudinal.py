"""Synthetic calendar longitudinal signals; no medical inference or attendance claims."""
import csv
from collections import defaultdict
from datetime import date, timedelta

LEAVE={'pto','sick','holiday','personal_appointment','unavailable'}
WORK={'meeting','team','customer','strategy','ai','focus','work'}

def union(intervals):
    out=[]
    for a,b in sorted(intervals):
        if b<=a: continue
        if out and a<=out[-1][1]: out[-1]=(out[-1][0],max(out[-1][1],b))
        else: out.append((a,b))
    return out

def length(intervals): return round(sum(b-a for a,b in union(intervals))/60,4)

def subtract(intervals, exclusions):
    remaining=union(intervals)
    for x,y in union(exclusions):
        nxt=[]
        for a,b in remaining:
            if b<=x or a>=y:nxt.append((a,b))
            else:
                if a<x:nxt.append((a,x))
                if b>y:nxt.append((y,b))
        remaining=nxt
    return remaining

def analyze_longitudinal(path, expectation_date, work_start=8*60, work_end=17*60+30):
    """Input: explicit category and privacy-safe event metadata. Does not inspect event titles."""
    by_day=defaultdict(list)
    with open(path,newline='') as f:
        for r in csv.DictReader(f):
            d=date.fromisoformat(r['date']); cat=r['category'].lower().strip()
            if cat not in LEAVE|WORK|{'break'}: raise ValueError('Unknown explicit category')
            if r['status'].lower() in ('declined','cancelled') or r['leader_attending'].lower()=='no': continue
            a=int(r['start_min']); b=int(r['end_min'])
            if not 0<=a<b<=1440: raise ValueError('Invalid interval')
            by_day[d].append((a,b,cat))
    if not by_day: raise ValueError('No leader calendar data')
    start=min(by_day); end=max(by_day)
    change=date.fromisoformat(expectation_date)
    if not start<change<=end: raise ValueError('Expectation date must split observed period')
    out={p:defaultdict(float) for p in ('before','after')}
    d=start
    while d<=end:
        if d.weekday()<5:
            p='before' if d<change else 'after'; m=out[p]; m['weekdays']+=1
            events=by_day[d]; available=[(work_start,work_end)]
            leave=[(a,b) for a,b,c in events if c in LEAVE]
            break_blocks=[(a,b) for a,b,c in events if c=='break']
            work=[(a,b) for a,b,c in events if c in WORK]
            ai=[(a,b) for a,b,c in events if c=='ai']
            team=[(a,b) for a,b,c in events if c=='team']
            # Explicit full-day leave is a marker spanning the workday, not 24h of leave.
            unavailable=union(leave)
            m['unavailable_hours']+=length([(max(a,work_start),min(b,work_end)) for a,b in unavailable])
            m['recorded_leave_days']+=int(bool(leave))
            m['recorded_sick_days']+=int(any(c=='sick' for _,_,c in events))
            m['recorded_break_days']+=int(bool(break_blocks))
            m['break_hours']+=length([(max(a,work_start),min(b,work_end)) for a,b in break_blocks])
            m['working_window_hours']+=(work_end-work_start)/60
            m['available_window_hours']+=length(subtract(available,unavailable))
            m['work_within_window_hours']+=length(subtract([(max(a,work_start),min(b,work_end)) for a,b in work],unavailable))
            m['after_hours_work_hours']+=length([(a,min(b,work_start)) for a,b in work if a<work_start]+[(max(a,work_end),b) for a,b in work if b>work_end])
            m['ai_labeled_hours']+=length(ai)
            m['team_labeled_hours']+=length(team)
            m['work_during_recorded_leave_hours']+=length([(max(a,x),min(b,y)) for a,b in work for x,y in unavailable if min(b,y)>max(a,x)])
            m['work_during_recorded_break_hours']+=length([(max(a,x),min(b,y)) for a,b in work for x,y in break_blocks if min(b,y)>max(a,x)])
        d+=timedelta(days=1)
    return {p:{**{k:round(v,3) for k,v in m.items()},'weeks_observed':round(m['weekdays']/5,3),
               'after_hours_per_week':round(m['after_hours_work_hours']/(m['weekdays']/5),3),
               'recorded_break_days_per_week':round(m['recorded_break_days']/(m['weekdays']/5),3),
               'recorded_leave_days_per_week':round(m['recorded_leave_days']/(m['weekdays']/5),3)} for p,m in out.items()}

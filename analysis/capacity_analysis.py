import pandas as pd
from datetime import datetime, timedelta

def analyze_calendar(csv_path, work_start="08:00", work_end="17:30", ai_expectation=4.0):
    df=pd.read_csv(csv_path)
    required={"date","start_time","end_time","event_title"}
    if not required.issubset(df.columns):
        raise ValueError("Calendar must include date, start_time, end_time, event_title.")
    if df.empty:
        raise ValueError("Calendar contains no events; no capacity conclusion is possible.")
    if df[list(required)].isna().any().any():
        raise ValueError("Calendar has missing required event values.")
    if datetime.strptime(work_end,"%H:%M") <= datetime.strptime(work_start,"%H:%M"):
        raise ValueError("Workday end must be later than start.")
    if ai_expectation < 0:
        raise ValueError("AI expectation cannot be negative.")
    if "category" not in df: df["category"]="Unspecified"
    if "attendees" not in df: df["attendees"]=""
    if "leader_attending" not in df: df["leader_attending"]="yes"
    if "status" not in df: df["status"]="confirmed"
    # Team-only and declined events must not be counted as leader commitments.
    leader=df["leader_attending"].fillna("").astype(str).str.strip().str.lower()
    status=df["status"].fillna("").astype(str).str.strip().str.lower()
    if (~leader.isin(["yes","no"])).any(): raise ValueError("leader_attending must be yes or no")
    if (~status.isin(["confirmed","tentative","declined","cancelled"])).any(): raise ValueError("Invalid event status")
    team_only_context=int(((leader=="no") & (~status.isin(["declined","cancelled"]))).sum())
    df=df[(leader=="yes") & (~status.isin(["declined","cancelled"]))].copy()
    if df.empty: raise ValueError("No confirmed/tentative events involving the leader; capacity cannot be established from this calendar")
    df["start"]=pd.to_datetime(df["date"]+" "+df["start_time"])
    df["end"]=pd.to_datetime(df["date"]+" "+df["end_time"])
    if (df["end"]<=df["start"]).any():
        raise ValueError("Each event must end after it starts.")
    df["week_start"]=df["start"].dt.to_period("W-SUN").apply(lambda r:r.start_time.date())

    def analyze_week(g):
        observed_dates=sorted(pd.to_datetime(g["date"]).dt.date.unique())
        # Analyze the complete Monday-Friday workweek even when a weekday has
        # zero calendar events. An empty day is still part of the stated work window.
        anchor=min(observed_dates)
        monday=anchor-timedelta(days=anchor.weekday())
        dates=[monday+timedelta(days=i) for i in range(5)]
        total_work=scheduled=0.0
        back_to_back=stretches_3plus=longest=protected=lunch=0
        open_blocks=[]
        overlap_hours=0.0; overlap_pairs=0; tentative_hours=0.0
        team_events=0; customer_events=0; category_counts={}
        team_event_hours=0.0; team_event_count=0; team_union_hours=0.0; team_labels=set()

        for d in dates:
            day=g[pd.to_datetime(g["date"]).dt.date==d].sort_values("start")
            ws=pd.Timestamp.combine(d, datetime.strptime(work_start,"%H:%M").time())
            we=pd.Timestamp.combine(d, datetime.strptime(work_end,"%H:%M").time())
            total_work+=(we-ws).total_seconds()/3600
            intervals=[(max(r.start,ws),min(r.end,we)) for r in day.itertuples() if min(r.end,we)>max(r.start,ws)]
            # Pairwise conflicts count event pairs, while excess booked time is
            # raw duration minus interval union (never double-count occupied hours).
            for i in range(len(intervals)):
                for j in range(i+1,len(intervals)):
                    if intervals[i][0]<intervals[j][1] and intervals[j][0]<intervals[i][1]: overlap_pairs+=1
            raw=sum((e-s).total_seconds()/3600 for s,e in intervals)
            team_intervals=[]
            for r in day.itertuples():
                category=str(r.category).strip().lower()
                category_counts[category]=category_counts.get(category,0)+1
                if category=="customer":customer_events+=1
                if str(r.attendees).strip():team_events+=1
                names=[x.strip().lower() for x in str(r.attendees).split(";") if x.strip()]
                team=[x for x in names if any(k in x for k in ("sales director","sales leader","regional vp","account team","sales rep","sales ops","revenue ops","enablement lead","channel sales","team member"))]
                if team:
                    team_event_count+=1
                    team_event_hours+=(min(r.end,we)-max(r.start,ws)).total_seconds()/3600
                    team_intervals.append((max(r.start,ws),min(r.end,we)))
                    team_labels.update(team)
                if str(r.status).strip().lower()=="tentative":tentative_hours+=(min(r.end,we)-max(r.start,ws)).total_seconds()/3600
            team_merged=[]
            for s,e in sorted(team_intervals):
                if team_merged and s<=team_merged[-1][1]:team_merged[-1][1]=max(e,team_merged[-1][1])
                else:team_merged.append([s,e])
            team_union_hours+=sum((e-s).total_seconds()/3600 for s,e in team_merged)
            merged=[]
            for s,e in intervals:
                if not merged or s>merged[-1][1]: merged.append([s,e])
                else: merged[-1][1]=max(merged[-1][1],e)
            occupied=sum((e-s).total_seconds()/3600 for s,e in merged)
            scheduled+=occupied
            overlap_hours+=raw-occupied
            cursor=ws
            for s,e in merged:
                if s>cursor: open_blocks.append((s-cursor).total_seconds()/3600)
                cursor=max(cursor,e)
            if cursor<we: open_blocks.append((we-cursor).total_seconds()/3600)
            chain=1
            for i in range(1,len(intervals)):
                if intervals[i][0]==intervals[i-1][1]:
                    back_to_back+=1; chain+=1
                else:
                    if chain>=3: stretches_3plus+=1
                    longest=max(longest,chain); chain=1
            if intervals:
                if chain>=3: stretches_3plus+=1
                longest=max(longest,chain)
            protected+=int(day["event_title"].str.contains("strategy|planning|focus",case=False,regex=True).sum())
            lunch+=int(day["event_title"].str.contains("lunch",case=False,regex=True).sum())
        return {
            "working_hours":round(total_work,2),
            "double_booked_excess_hours":round(overlap_hours,2),
            "overlapping_event_pairs":overlap_pairs,
            "tentative_event_hours":round(tentative_hours,2),
            "events_with_attendee_metadata":team_events,
            "leader_team_meeting_events":team_event_count,
            "leader_team_meeting_event_hours":round(team_event_hours,2),
            "leader_team_meeting_occupied_hours":round(team_union_hours,2),
            "distinct_team_attendee_labels":len(team_labels),
            "customer_category_events":customer_events,
            "scheduled_hours":round(scheduled,2),
            "nominal_unscheduled_hours":round(total_work-scheduled,2),
            "back_to_back_transitions":back_to_back,
            "stretches_of_3plus_back_to_back":stretches_3plus,
            "longest_back_to_back_chain_meetings":longest,
            "open_blocks_60min_plus":sum(x>=1 for x in open_blocks),
            "open_blocks_90min_plus":sum(x>=1.5 for x in open_blocks),
            "hours_in_open_blocks_60min_plus":round(sum(x for x in open_blocks if x>=1),2),
            "fragmented_open_hours_under_60min":round(sum(x for x in open_blocks if x<1),2),
            "protected_strategy_planning_blocks":protected,
            "explicit_lunch_blocks":lunch,
            "explicit_ai_blocks":int(g["event_title"].str.contains(r"\bAI\b|artificial intelligence",case=False,regex=True).sum())
        }

    weekly=[]
    for week,g in df.groupby("week_start"):
        x=analyze_week(g); x["week_start"]=str(week); weekly.append(x)
    out=pd.DataFrame(weekly)
    averages={c:round(float(out[c].mean()),2) for c in out.columns if c!="week_start"}
    averages["ai_expectation_hours_per_week"]=ai_expectation
    averages["team_only_context_events_total"]=team_only_context
    return out, averages

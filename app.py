import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "analysis"))
from capacity_analysis import analyze_calendar
from llm_interpretation import demo_brief, interpret_with_llm

st.set_page_config(page_title="Capacity Before Adoption", page_icon="⏱️", layout="wide")

st.title("Capacity Before Adoption")
st.caption("A Forward Deployed HR prototype: before adding an AI-development expectation, examine whether the leader's operating rhythm contains realistic capacity.")

with st.sidebar:
    st.header("Scenario")
    leader = st.text_input("Leader", "Maya")
    role = st.text_input("Role", "VP of Sales")
    work_start = st.text_input("Workday starts", "08:00")
    work_end = st.text_input("Workday ends", "17:30")
    expectation = st.number_input("AI capability expectation (hours/week)", min_value=0.0, value=4.0, step=0.5)
    scenario = st.selectbox("Included synthetic scenario", ["Maya — baseline", "Maya — overlapping & team events", "Daniel — comparatively open"])
    uploaded = st.file_uploader("Calendar CSV", type="csv")
    st.caption("Expected columns: date, start_time, end_time, event_title, recurring")
    st.divider()
    live_llm = st.checkbox("Use live LLM interpretation", value=False)
    api_key = st.text_input("OpenAI API key (live mode only)", type="password") if live_llm else ""
    if live_llm:
        st.caption("Only aggregated numeric metrics are sent to the model, not raw calendar events. API use may incur charges.")

default_path = Path(__file__).parent / "data" / {
    "Maya — baseline":"maya_calendar.csv",
    "Maya — overlapping & team events":"maya_complex_calendar.csv",
    "Daniel — comparatively open":"daniel_calendar.csv",
}[scenario]
source = uploaded if uploaded is not None else default_path

try:
    weekly, avg = analyze_calendar(source, work_start, work_end, expectation)
except Exception as e:
    st.error(f"Could not analyze calendar: {e}")
    st.stop()

st.subheader(f"{leader} — {role}")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Scheduled", f"{avg['scheduled_hours']:.1f} hrs/wk")
c2.metric("Nominally open", f"{avg['nominal_unscheduled_hours']:.1f} hrs/wk")
c3.metric("Open in 60+ min blocks", f"{avg['hours_in_open_blocks_60min_plus']:.1f} hrs/wk")
c4.metric("AI expectation", f"{expectation:.1f} hrs/wk")

st.subheader("What the calendar shows")

left,right=st.columns(2)
with left:
    st.write(f"**Back-to-back transitions:** {avg['back_to_back_transitions']:.1f}/week")
    st.write(f"**3+ meeting stretches:** {avg['stretches_of_3plus_back_to_back']:.1f}/week")
    st.write(f"**Fragmented open time (<60 min):** {avg['fragmented_open_hours_under_60min']:.1f} hrs/week")
with right:
    st.write(f"**60+ minute open blocks:** {avg['open_blocks_60min_plus']:.1f}/week")
    st.write(f"**90+ minute open blocks:** {avg['open_blocks_90min_plus']:.1f}/week")
    st.write(f"**Strategy/planning blocks:** {avg['protected_strategy_planning_blocks']:.1f}/week")

st.subheader("Conflicts and attendance context")
st.write(f"**Overlapping event pairs:** {avg['overlapping_event_pairs']:.1f}/week · **Excess double-booked event hours:** {avg['double_booked_excess_hours']:.1f}/week")
st.caption("Occupied hours are the union of Maya's commitments, not the sum of overlapping invitations. Meetings Maya attends with her team count toward her schedule; team-only events without Maya are retained as context, not counted against her personal hours. Tentative invitations are counted provisionally.")
st.subheader("Time with the team")
st.write(f"**Leader-attended team meeting events:** {avg['leader_team_meeting_events']:.1f}/week · **Event hours (can overlap):** {avg['leader_team_meeting_event_hours']:.1f}/week · **Distinct occupied hours in team meetings:** {avg['leader_team_meeting_occupied_hours']:.1f}/week")
st.caption(f"{avg['team_only_context_events_total']:.0f} team-only events appear in the source calendar for context. Attendee labels are imperfect metadata; these measures do not establish team members' total workloads or actual attendance.")
st.write("**Discovery:** Could AI experimentation or coaching be incorporated into an existing team interaction without displacing its sales or leadership purpose? Which activities would need redesign or explicit trade-offs?")
st.write(f"**Events with attendee metadata:** {avg['events_with_attendee_metadata']:.1f}/week · **Customer-category events:** {avg['customer_category_events']:.1f}/week")
st.subheader("Capacity check")

if avg["hours_in_open_blocks_60min_plus"] < expectation:
    st.warning(
        "The calendar does not show enough uninterrupted open time to absorb the stated "
        "AI-development expectation without reviewing existing workload."
    )
else:
    st.info(
        "Nominal uninterrupted time meets or exceeds the stated expectation, but open calendar "
        "time should not automatically be treated as available capacity. Existing workload and "
        "intentionally protected time require leader review."
    )

st.subheader("Patterns worth reviewing")
patterns=[]
if avg["back_to_back_transitions"] >= 5:
    patterns.append("Frequent back-to-back meetings create sustained meeting compression.")
if avg["fragmented_open_hours_under_60min"] >= 2:
    patterns.append("A meaningful share of nominally open time is fragmented into blocks under 60 minutes.")
if avg["protected_strategy_planning_blocks"] > 0:
    patterns.append("Intentional strategy/planning time exists and should not automatically be reassigned.")
if avg["explicit_lunch_blocks"] < 5:
    patterns.append("Lunch is not explicitly protected every workday.")
if avg["explicit_ai_blocks"] == 0:
    patterns.append("No events are explicitly labeled for AI development. This is not evidence that AI work is absent.")

for p in patterns:
    st.write("• " + p)

st.subheader("HR interpretation")
if st.button("Generate capacity brief", type="primary"):
    try:
        if live_llm:
            if not api_key:
                st.error("Enter an API key for live LLM interpretation, or turn off live mode for the deterministic demo.")
                st.stop()
            with st.spinner("Interpreting calendar signals..."):
                brief = interpret_with_llm(avg, api_key)
            st.success("LLM-generated interpretation — review with the leader")
        else:
            brief = demo_brief(avg)
            st.info("Deterministic demonstration; no LLM was called. Enable live mode to generate an AI interpretation.")
        for heading, key in (("Observations", "observations"), ("What remains unknown", "uncertainties"), ("Discovery questions", "discovery_questions")):
            st.markdown(f"**{heading}**")
            for item in brief[key]: st.write("• " + item)
        st.markdown("**Human handoff**")
        st.write(brief["handoff"])
    except Exception as exc:
        st.error(f"Interpretation unavailable: {exc}")

st.subheader("Leader conversation")
st.write(
    "Use these patterns as discovery prompts before changing the calendar. The tool does not determine "
    "which meetings are unnecessary, whether the leader is committed to AI, or whether unscheduled time is truly available."
)

st.divider()
st.markdown("**Design principle:** Calendar patterns are evidence for discovery—not evidence for judgment.")

with st.expander("Weekly metrics"):
    st.dataframe(weekly, use_container_width=True)

st.divider()
st.header('18-month sustainability comparison — separate longitudinal input')
st.caption('Upload a privacy-minimal synthetic or consented calendar with date, start_min, end_min, category, status, leader_attending. Do not upload diagnoses, appointment details, or personal event titles. This is not a health or leave-compliance assessment.')
long_upload=st.file_uploader('18-month calendar CSV',type='csv',key='longitudinal_upload')
change_date=st.date_input('New AI expectation introduced',value=pd.Timestamp('2025-10-01'),key='longitudinal_change')
if long_upload is not None:
    from longitudinal import analyze_longitudinal
    from longitudinal_brief import make_longitudinal_brief
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            from pathlib import Path
            temp_path = Path(temp_dir) / 'calendar.csv'
            temp_path.write_bytes(long_upload.getvalue())
            comparison=analyze_longitudinal(str(temp_path),change_date.isoformat())
        st.caption('Before and after are normalized by observed weekdays. Changes are descriptive, not evidence of causation.')
        brief=make_longitudinal_brief(comparison)
        st.subheader('Recorded patterns')
        for item in brief['observations']: st.write('• '+item)
        st.subheader('What remains unknown')
        for item in brief['uncertainties']: st.write('• '+item)
        st.subheader('Questions for a private leader conversation')
        for item in brief['discovery_questions']: st.write('• '+item)
        st.caption(brief['handoff'])
        st.info('Longitudinal interpretation is deterministic and offline; no longitudinal data is sent to an LLM.')
    except Exception as exc:
        st.error(f'Could not analyze the longitudinal calendar: {exc}')

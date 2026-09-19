import unittest
from pathlib import Path
from analysis.capacity_analysis import analyze_calendar
from analysis.llm_interpretation import demo_brief, validate_brief
DATA=Path(__file__).resolve().parents[1]/"data"
class ComplexCalendarTests(unittest.TestCase):
 def test_complex_has_conflicts(self):
  _,a=analyze_calendar(DATA/"maya_complex_calendar.csv")
  self.assertGreater(a["double_booked_excess_hours"],0)
  self.assertGreater(a["overlapping_event_pairs"],0)
 def test_union_never_exceeds_working_hours(self):
  _,a=analyze_calendar(DATA/"maya_complex_calendar.csv")
  self.assertLessEqual(a["scheduled_hours"],a["working_hours"])
  self.assertAlmostEqual(a["scheduled_hours"]+a["nominal_unscheduled_hours"],a["working_hours"])
 def test_team_only_and_declined_do_not_count(self):
  import csv, tempfile
  from pathlib import Path
  fields=["date","start_time","end_time","event_title","leader_attending","status"]
  rows=[dict(date="2026-09-21",start_time="09:00",end_time="10:00",event_title="Team only",leader_attending="no",status="confirmed"),dict(date="2026-09-21",start_time="11:00",end_time="12:00",event_title="Declined",leader_attending="yes",status="declined"),dict(date="2026-09-21",start_time="13:00",end_time="14:00",event_title="Actual",leader_attending="yes",status="confirmed")]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"c.csv"
   with p.open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
   _,a=analyze_calendar(p)
   self.assertEqual(a["scheduled_hours"],1)
 def test_open_calendar_not_proof_of_capacity(self):
  _,a=analyze_calendar(DATA/"daniel_calendar.csv")
  self.assertGreater(a["hours_in_open_blocks_60min_plus"],4)
  b=demo_brief(a)
  self.assertIn("cannot establish"," ".join(b["uncertainties"]))
 def test_conflicts_not_inferred_as_double_attendance(self):
  _,a=analyze_calendar(DATA/"maya_complex_calendar.csv")
  b=validate_brief(demo_brief(a))
  self.assertNotIn("attended both"," ".join(b["observations"]).lower())

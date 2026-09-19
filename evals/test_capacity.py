import csv
import tempfile
import unittest
from pathlib import Path
from analysis.capacity_analysis import analyze_calendar

FIELDS=["date","start_time","end_time","event_title","recurring"]
def run(rows):
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"calendar.csv"
        with p.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows([dict(date=r.get("date","2026-09-21"),recurring="No",
                                  **{k:v for k,v in r.items() if k!="date"}) for r in rows])
        return analyze_calendar(p)

class CalendarTests(unittest.TestCase):
    def test_sample_has_four_weeks(self):
        weeks,avg=analyze_calendar(Path(__file__).resolve().parents[1]/"data/maya_calendar.csv")
        self.assertEqual(len(weeks),4)
        self.assertAlmostEqual(avg["working_hours"],47.5)
        self.assertAlmostEqual(avg["scheduled_hours"]+avg["nominal_unscheduled_hours"],47.5)
    def test_empty_calendar_fails_closed(self):
        with self.assertRaises(ValueError):run([])
    def test_fragmented_open_time_is_not_long_block(self):
        rows=[]
        for d in ("2026-09-21","2026-09-22","2026-09-23","2026-09-24","2026-09-25"):
            rows.extend([
                dict(date=d,start_time="08:30",end_time="09:30",event_title="Meeting"),
                dict(date=d,start_time="10:00",end_time="11:00",event_title="Meeting"),
                dict(date=d,start_time="11:30",end_time="17:00",event_title="Meeting")])
        _,a=run(rows)
        self.assertEqual(a["hours_in_open_blocks_60min_plus"],0)
        self.assertGreater(a["fragmented_open_hours_under_60min"],0)
    def test_four_hours_ai_is_label_not_adoption(self):
        _,a=run([dict(start_time="08:00",end_time="12:00",event_title="AI development")])
        self.assertEqual(a["explicit_ai_blocks"],1)
    def test_customer_meetings_are_not_reclassified(self):
        _,a=run([dict(start_time="08:00",end_time="09:00",event_title="Customer call")])
        self.assertEqual(a["scheduled_hours"],1)
    def test_protected_strategy_is_not_ai(self):
        _,a=run([dict(start_time="09:00",end_time="10:30",event_title="Strategy and Planning")])
        self.assertEqual(a["protected_strategy_planning_blocks"],1)
        self.assertEqual(a["explicit_ai_blocks"],0)
    def test_back_to_back(self):
        _,a=run([dict(start_time="09:00",end_time="10:00",event_title="A"),
                 dict(start_time="10:00",end_time="11:00",event_title="B"),
                 dict(start_time="11:00",end_time="12:00",event_title="C")])
        self.assertEqual(a["back_to_back_transitions"],2)
        self.assertEqual(a["stretches_of_3plus_back_to_back"],1)
    def test_overlapping_events_do_not_double_count_hours(self):
        _,a=run([dict(start_time="09:00",end_time="10:00",event_title="A"),
                 dict(start_time="09:30",end_time="10:30",event_title="B")])
        self.assertEqual(a["scheduled_hours"],1.5)
    def test_invalid_event_rejected(self):
        with self.assertRaises(ValueError):
            run([dict(start_time="12:00",end_time="11:00",event_title="Invalid")])

if __name__=="__main__":unittest.main()

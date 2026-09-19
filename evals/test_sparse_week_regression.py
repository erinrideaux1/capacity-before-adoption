import csv, tempfile, unittest
from pathlib import Path
from analysis.capacity_analysis import analyze_calendar

class SparseWeekRegression(unittest.TestCase):
    def test_event_free_weekdays_remain_part_of_workweek(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"sparse.csv"
            rows=[
                {"date":"2026-01-05","start_time":"09:00","end_time":"10:00","event_title":"Monday meeting",
                 "category":"team","attendees":"Sales Director","leader_attending":"yes","status":"confirmed"},
                {"date":"2026-01-09","start_time":"09:00","end_time":"10:00","event_title":"Friday meeting",
                 "category":"customer","attendees":"Customer","leader_attending":"yes","status":"confirmed"},
            ]
            with p.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
            _,avg=analyze_calendar(p)
            self.assertEqual(avg["working_hours"],47.5)
            self.assertEqual(avg["scheduled_hours"],2.0)
            self.assertEqual(avg["nominal_unscheduled_hours"],45.5)

if __name__=="__main__": unittest.main()

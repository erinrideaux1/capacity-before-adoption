import csv,tempfile,unittest
from pathlib import Path
from analysis.longitudinal import analyze_longitudinal
F=['date','start_min','end_min','category','status','leader_attending']
def row(d,a,b,c,status='confirmed',leader='yes'):
 return dict(date=d,start_min=a,end_min=b,category=c,status=status,leader_attending=leader)
def analyze(rows):
 with tempfile.TemporaryDirectory() as t:
  p=Path(t)/'c.csv'
  with p.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=F);w.writeheader();w.writerows(rows)
  return analyze_longitudinal(p,'2025-10-01')
class LongitudinalTests(unittest.TestCase):
 def test_full_day_pto_reduces_available_hours(self):
  r=analyze([row('2025-09-30',480,1050,'pto'),row('2025-10-01',540,600,'meeting')])
  self.assertEqual(r['before']['available_window_hours'],0)
  self.assertEqual(r['before']['unavailable_hours'],9.5)
 def test_appointment_does_not_count_as_open(self):
  r=analyze([row('2025-09-30',900,990,'personal_appointment'),row('2025-10-01',540,600,'meeting')])
  self.assertEqual(r['before']['available_window_hours'],8)
 def test_overlapping_unavailability_does_not_double_count(self):
  r=analyze([row('2025-09-30',900,960,'unavailable'),row('2025-09-30',930,990,'personal_appointment'),row('2025-10-01',540,600,'meeting')])
  self.assertEqual(r['before']['unavailable_hours'],1.5)
 def test_work_during_leave_is_flagged_not_counted_as_available(self):
  r=analyze([row('2025-09-30',480,1050,'pto'),row('2025-09-30',540,600,'meeting'),row('2025-10-01',540,600,'meeting')])
  self.assertEqual(r['before']['work_during_recorded_leave_hours'],1)
  self.assertEqual(r['before']['work_within_window_hours'],0)
 def test_declined_and_team_only_excluded(self):
  r=analyze([row('2025-09-29',540,600,'meeting'),row('2025-09-30',480,1050,'pto','declined'),row('2025-09-30',540,600,'team','confirmed','no'),row('2025-10-01',540,600,'meeting')])
  self.assertEqual(r['before']['unavailable_hours'],0)
  self.assertEqual(r['before']['work_within_window_hours'],1)
 def test_invalid_category_fails_closed(self):
  with self.assertRaises(ValueError):analyze([row('2025-09-30',480,1050,'diagnosis'),row('2025-10-01',540,600,'meeting')])
if __name__=='__main__':unittest.main()

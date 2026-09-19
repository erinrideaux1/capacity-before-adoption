import csv, tempfile, unittest
from pathlib import Path
from analysis.capacity_analysis import analyze_calendar

class TeamInteractionTests(unittest.TestCase):
    def analyze(self,rows):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'calendar.csv'
            with p.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=['date','start_time','end_time','event_title','attendees','leader_attending','status','category'])
                writer.writeheader()
                for row in rows:writer.writerow(dict(date='2026-09-21',status='confirmed',category='Internal',**row))
            return analyze_calendar(p)[1]
    def test_leader_with_team_counts_as_scheduled_and_team_time(self):
        a=self.analyze([dict(start_time='09:00',end_time='10:00',event_title='Coaching',attendees='Sales directors;Maya',leader_attending='yes')])
        self.assertEqual(a['scheduled_hours'],1)
        self.assertEqual(a['leader_team_meeting_occupied_hours'],1)
        self.assertEqual(a['leader_team_meeting_events'],1)
    def test_team_only_is_context_not_leader_hours(self):
        a=self.analyze([dict(start_time='09:00',end_time='10:00',event_title='Team huddle',attendees='Sales directors;Account team',leader_attending='no'),dict(start_time='11:00',end_time='12:00',event_title='Customer',attendees='Customer',leader_attending='yes')])
        self.assertEqual(a['scheduled_hours'],1)
        self.assertEqual(a['team_only_context_events_total'],1)
        self.assertEqual(a['leader_team_meeting_occupied_hours'],0)
    def test_overlapping_team_events_do_not_double_count_occupied_time(self):
        a=self.analyze([dict(start_time='09:00',end_time='10:00',event_title='Team review',attendees='Sales directors',leader_attending='yes'),dict(start_time='09:30',end_time='10:30',event_title='Team coaching',attendees='Account team',leader_attending='yes')])
        self.assertEqual(a['leader_team_meeting_event_hours'],2)
        self.assertEqual(a['leader_team_meeting_occupied_hours'],1.5)
        self.assertEqual(a['scheduled_hours'],1.5)
    def test_external_meeting_not_mistaken_for_team(self):
        a=self.analyze([dict(start_time='09:00',end_time='10:00',event_title='Customer call',attendees='Customer;Maya',leader_attending='yes')])
        self.assertEqual(a['leader_team_meeting_events'],0)

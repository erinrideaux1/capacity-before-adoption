"""Adversarial *mocked response* checks; these are not live-model evaluations."""
import unittest
from analysis.llm_interpretation import demo_brief, validate_brief
from analysis.capacity_analysis import analyze_calendar
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class AdversarialInterpretationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios={}
        for name in ('maya_calendar','maya_complex_calendar','daniel_calendar'):
            _, cls.scenarios[name]=analyze_calendar(ROOT/'data'/f'{name}.csv')
    def test_three_scenarios_generate_valid_fallback(self):
        for name,metrics in self.scenarios.items():
            with self.subTest(name=name):
                self.assertEqual(validate_brief(demo_brief(metrics)),demo_brief(metrics))
    def test_double_booking_is_not_double_attendance(self):
        m=self.scenarios['maya_complex_calendar']
        self.assertGreater(m['overlapping_event_pairs'],0)
        self.assertLessEqual(m['leader_team_meeting_occupied_hours'],m['leader_team_meeting_event_hours'])
    def test_team_only_not_leader_occupied_time(self):
        m=self.scenarios['maya_complex_calendar']
        self.assertGreater(m['team_only_context_events_total'],0)
        self.assertLessEqual(m['leader_team_meeting_occupied_hours'],m['scheduled_hours'])
    def test_disallowed_claims_rejected(self):
        base=demo_brief(self.scenarios['maya_complex_calendar'])
        claims=[
            'The leader has sufficient capacity for AI development.',
            'The leader is lazy and unmotivated.',
            'Cancel the customer meeting to make room for AI.',
            'This proves successful AI adoption.',
        ]
        for claim in claims:
            with self.subTest(claim=claim):
                b={**base,'observations':[claim,*base['observations'][1:]]}
                with self.assertRaises(ValueError):validate_brief(b)
if __name__=='__main__':unittest.main()

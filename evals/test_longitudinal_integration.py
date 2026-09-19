import unittest
from pathlib import Path
from analysis.longitudinal import analyze_longitudinal
from analysis.longitudinal_brief import make_longitudinal_brief

ROOT=Path(__file__).resolve().parent
class LongitudinalIntegrationTests(unittest.TestCase):
    def test_all_100_calendar_briefs(self):
        paths=sorted((ROOT/'stress_18_month_calendars').glob('calendar_*.csv'))
        self.assertEqual(len(paths),100)
        for p in paths:
            with self.subTest(calendar=p.name):
                result=analyze_longitudinal(p,'2025-10-01')
                brief=make_longitudinal_brief(result)
                self.assertEqual(len(brief['observations']),4)
                text=' '.join(brief['observations']).lower()
                for forbidden in ('diagnosis','sick leave appropriately','caused by ai','unmotivated'):
                    self.assertNotIn(forbidden,text)
                for part in ('before','after'):
                    m=result[part]
                    self.assertGreater(m['weeks_observed'],0)
                    self.assertAlmostEqual(m['working_window_hours'],m['available_window_hours']+m['unavailable_hours'],places=2)
    def test_brief_does_not_claim_causation(self):
        p=next((ROOT/'stress_18_month_calendars').glob('calendar_*.csv'))
        brief=make_longitudinal_brief(analyze_longitudinal(p,'2025-10-01'))
        self.assertIn('does not establish',brief['uncertainties'][1])
if __name__=='__main__':unittest.main()

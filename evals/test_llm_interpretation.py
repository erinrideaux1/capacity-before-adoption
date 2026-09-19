import unittest
from unittest.mock import patch
from types import ModuleType
from types import SimpleNamespace
import json
from analysis.llm_interpretation import demo_brief, validate_brief, interpret_with_llm
from analysis.capacity_analysis import analyze_calendar
from pathlib import Path

class InterpretationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.metrics=analyze_calendar(Path(__file__).resolve().parents[1]/'data/maya_calendar.csv')
    def test_demo_valid(self):
        self.assertEqual(len(demo_brief(self.metrics)['discovery_questions']),3)
    def test_demo_does_not_claim_capacity(self):
        self.assertIn('cannot establish', ' '.join(demo_brief(self.metrics)['uncertainties']))
    def test_no_key_rejected(self):
        with self.assertRaises(ValueError):interpret_with_llm(self.metrics,'')
    def test_wrong_schema_rejected(self):
        with self.assertRaises(ValueError):validate_brief({'observations':[]})
    def test_empty_question_list_rejected(self):
        b=demo_brief(self.metrics);b['discovery_questions']=[]
        with self.assertRaises(ValueError):validate_brief(b)
    def test_judgmental_label_rejected(self):
        b=demo_brief(self.metrics);b['observations'][0]='The leader is lazy and unmotivated.'
        with self.assertRaises(ValueError):validate_brief(b)
    def test_claim_of_sufficient_capacity_rejected(self):
        b=demo_brief(self.metrics);b['observations'][0]='The leader has enough capacity to adopt AI.'
        with self.assertRaises(ValueError):validate_brief(b)
    def test_customer_meeting_cancellation_rejected(self):
        b=demo_brief(self.metrics);b['observations'][0]='Cancel the customer meeting to create time.'
        with self.assertRaises(ValueError):validate_brief(b)
    def test_adoption_proof_rejected(self):
        b=demo_brief(self.metrics);b['observations'][0]='This proves successful AI adoption.'
        with self.assertRaises(ValueError):validate_brief(b)
    def test_live_model_receives_only_aggregates(self):
        good=demo_brief(self.metrics)
        fake=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(good)))])
        fake_module=ModuleType('openai')
        from unittest.mock import MagicMock
        fake_module.OpenAI=MagicMock()
        with patch.dict('sys.modules',{'openai':fake_module}):
            client=fake_module.OpenAI
            client.return_value.chat.completions.create.return_value=fake
            result=interpret_with_llm({**self.metrics,'event_title':'PRIVATE CUSTOMER','leader':'Maya'},'test-key')
            sent=client.return_value.chat.completions.create.call_args.kwargs['messages'][1]['content']
            self.assertNotIn('PRIVATE CUSTOMER',sent)
            self.assertNotIn('Maya',sent)
            self.assertEqual(result,good)

if __name__=='__main__':unittest.main()

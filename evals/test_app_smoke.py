"""Dependency-free UI control-flow smoke test, NOT a real Streamlit browser test."""
import io, runpy, sys, types, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class StopApp(Exception): pass
class UI:
    def __init__(self,upload=None): self.upload=upload; self.errors=[]; self.messages=[]
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def __getattr__(self,name):
        if name in ('sidebar',):return self
        if name in ('columns',):return lambda n:[self for _ in range(n)]
        if name in ('file_uploader',):return lambda *a,**k:self.upload if k.get('key')=='longitudinal_upload' else None
        if name in ('text_input',):return lambda label,value='',**k:value
        if name in ('number_input',):return lambda label,**k:k.get('value',0)
        if name in ('selectbox',):return lambda label,options,**k:options[0]
        if name in ('checkbox','button',):return lambda *a,**k:False
        if name in ('date_input',):return lambda label,**k:k['value'].date() if hasattr(k['value'],'date') else k['value']
        if name in ('error',):return lambda msg:self.errors.append(str(msg))
        if name in ('stop',):return lambda : (_ for _ in ()).throw(StopApp())
        if name in ('expander','spinner',):return lambda *a,**k:self
        return lambda *a,**k:self.messages.append((name,a))

def run_ui(upload=None):
    ui=UI(upload)
    original=sys.modules.get('streamlit')
    sys.modules['streamlit']=ui
    try:runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
    except StopApp:pass
    finally:
        if original is None:sys.modules.pop('streamlit',None)
        else:sys.modules['streamlit']=original
    return ui

class Upload:
    def __init__(self,b):self.b=b
    def getvalue(self):return self.b

class AppSmoke(unittest.TestCase):
    def test_default_interface_control_flow(self):
        ui=run_ui()
        self.assertFalse(ui.errors,ui.errors)
        self.assertTrue(any('18-month sustainability' in str(args) for name,args in ui.messages if name=='header'))
    def test_longitudinal_upload_control_flow(self):
        path=next((ROOT/'evals'/'stress_18_month_calendars').glob('*.csv'))
        ui=run_ui(Upload(path.read_bytes()))
        self.assertFalse(ui.errors,ui.errors)
        self.assertTrue(any('Recorded patterns' in str(args) for name,args in ui.messages if name=='subheader'))
    def test_invalid_longitudinal_upload_shows_error(self):
        ui=run_ui(Upload(b'not,a,calendar\n'))
        self.assertTrue(any('Could not analyze' in err for err in ui.errors))
if __name__=='__main__':unittest.main()

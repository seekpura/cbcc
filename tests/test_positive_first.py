from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def test_positive_first_child_skills():
    r=subprocess.run([sys.executable,str(ROOT/'validators/validate_positive_first.py'),str(ROOT/'skills')],capture_output=True,text=True)
    assert r.returncode==0,(r.stdout,r.stderr)

"""Reproduce the decisive checks using bundled inputs, no original workspace required.
The full suite takes several minutes; fine full-network runs are slower.
Use separate body-requirements.txt environment for body_bridge.py.
"""
from pathlib import Path
import argparse,subprocess,sys
R=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--full-network',action='store_true');a=p.parse_args()
# The source matrices, targets, native derivative oracle and historical candidate
# configurations are versioned. prepare.py is only for re-exporting original CSVs.
subprocess.run([sys.executable,'-m','pytest','-p','no:cacheprovider',str(R/'test_scientific_checks.py'),'-q'],check=True,cwd=R)
if a.full_network:
 for cmd in [['intact_suite.py','adult'],['fine_validation.py','.00625','baseline'],['fine_validation.py','.003125','baseline'],['fine_validation.py','.003125','E2_silenced']]:subprocess.run([sys.executable,str(R/cmd[0]),*cmd[1:]],check=True,cwd=R)
subprocess.run([sys.executable,str(R/'muscle_readout.py'),'adult'],check=True,cwd=R)
subprocess.run([sys.executable,str(R/'report.py')],check=True,cwd=R)

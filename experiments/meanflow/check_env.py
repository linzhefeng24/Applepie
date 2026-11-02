"""Read-only checks for an existing environment. Never installs packages."""
import importlib
from importlib import metadata
from pathlib import Path
import platform
import sys

print('Python:',sys.version.split()[0])
print('Interpreter:',sys.executable)
print('System:',platform.platform())
print('Project directory:',Path(__file__).resolve().parents[1])
required={'torch':'torch','torchvision':'torchvision','numpy':'numpy','scipy':'scipy',
          'PyYAML':'yaml','Pillow':'PIL','pytest':'pytest'}
optional={'torchmetrics':'torchmetrics','torch-fidelity':'torch_fidelity'}
missing=[]
for label,module in required.items():
    try:
        importlib.import_module(module)
        try:version=metadata.version(label)
        except metadata.PackageNotFoundError:version='unknown'
        print(f'OK       {label}: {version}')
    except Exception as e:
        missing.append(label);print(f'PROBLEM  {label}: {type(e).__name__}: {e}')
for label,module in optional.items():
    try:
        importlib.import_module(module);print(f'OPTIONAL {label}: {metadata.version(label)}')
    except Exception as e:print(f'OPTIONAL {label}: unavailable ({type(e).__name__}); needed only for FID')
try:
    import torch
    print('torch.func.jvp:',hasattr(torch.func,'jvp'))
    print('CUDA available:',torch.cuda.is_available())
    print('PyTorch CUDA runtime:',torch.version.cuda)
    if torch.cuda.is_available():
        print('GPU:',torch.cuda.get_device_name(0))
        print('GPU memory GiB:',round(torch.cuda.get_device_properties(0).total_memory/1024**3,2))
    else:print('No CUDA detected. Do not launch a full run with --device cuda until resolved.')
except Exception:pass
if missing:
    print('Resolve only these core packages:',', '.join(missing))
    print('For import errors in installed packages, inspect the error before reinstalling anything.')
    sys.exit(1)
print('Core imports succeeded. Next: python -m pytest -q')
print('Reference-tested version is torch 2.7.1; other installed versions require the tests above.')

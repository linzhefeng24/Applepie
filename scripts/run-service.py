import importlib.util,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('service_environment',ROOT/'scripts/service-environment.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
name=sys.argv[1];service=next(s for s in module.REGISTRY if s['name']==name);env=module.environment(name)
if service['kind']=='scala':
 app=json.loads((ROOT/'.run/service-classpaths.json').read_text())[name]
 cmd=['java','-XX:ActiveProcessorCount=2','-Xms16m','-Xmx128m','-cp',app['classpath'],app['mainClass']]
else:
 env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');cmd=[module.read_settings()['PYTHON_BIN'],service['entry']]
os.chdir(ROOT);os.execvpe(cmd[0],cmd,env)

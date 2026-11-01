"""Package and verify a relocatable Scala runtime; normal releases need no Maven access."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,shutil,sys,tempfile,time,zipfile
ROOT=Path(__file__).resolve().parents[1]
class CorruptRuntime(ValueError):pass

def source_hash(root):
    files=list((root/'backend/src/main').rglob('*'))
    files += [root/n for n in ['backend/build.sbt','backend/project/build.properties','backend/project/plugins.sbt','config/services.json']]
    h=hashlib.sha256()
    for p in sorted(files):
        if p.is_file():h.update(str(p.relative_to(root)).encode());h.update(p.read_bytes())
    return h.hexdigest()
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def validated(root):
    runtime=root/'backend/runtime';manifest=runtime/'manifest.json'
    if not manifest.exists():
        if runtime.exists() and any(runtime.iterdir()):raise CorruptRuntime('运行包清单缺失')
        return None
    try:
        m=json.loads(manifest.read_text())
        if m.get('format') not in (1,2):raise CorruptRuntime('不支持的运行包格式')
        if m['sourceHash']!=source_hash(root):return None
        files=[]
        for entry in m['artifacts']:
            relative=PurePosixPath(entry['path'])
            if relative.is_absolute() or '..' in relative.parts or ':' in str(relative) or relative.suffix!='.jar':raise CorruptRuntime('无效运行包路径')
            path=runtime/relative
            if not path.resolve().is_relative_to(runtime.resolve()) or not path.is_file():raise CorruptRuntime('运行包文件缺失或路径异常')
            if path.stat().st_size!=entry['size'] or sha(path)!=entry['sha256']:raise CorruptRuntime('运行包 SHA256 校验失败：'+str(relative))
            files.append(path)
        if not files or (m['format']==1 and files[0].name!='app.jar'):raise CorruptRuntime('缺少应用 JAR')
        if m['format']==2:
            expected={s['name'] for s in json.loads((root/'config/services.json').read_text()) if s['kind']=='scala'}
            if set(m['services'])!=expected:raise CorruptRuntime('服务运行包清单不完整')
            allowed={e['path'] for e in m['artifacts']}
            for name,entry in m['services'].items():
                if entry['mainClass']!=f'services.{name}.routes.ServiceMain':raise CorruptRuntime('服务入口异常')
                if not entry['classpath'] or not set(entry['classpath'])<=allowed:raise CorruptRuntime('服务类路径包含未验证文件')
                if [p for p in entry['classpath'] if p.startswith('services/')]!=[f'services/{name}.jar']:raise CorruptRuntime('服务业务实现未隔离')
        return files
    except (KeyError,TypeError,json.JSONDecodeError,OSError) as e:raise CorruptRuntime('运行包清单损坏') from e

def activate(root):
    files=validated(root)
    if files is None:return False
    out=root/'.run';out.mkdir(exist_ok=True)
    m=json.loads((root/'backend/runtime/manifest.json').read_text())
    if m['format']==2:
        services={name:dict(mainClass=entry['mainClass'],classpath=os.pathsep.join(str(root/'backend/runtime'/p) for p in entry['classpath'])) for name,entry in m['services'].items()}
        (out/'service-classpaths.json').write_text(json.dumps(services))
    else:(out/'classpath').write_text(os.pathsep.join(map(str,files)))
    (out/'build-root').write_text(str(root.resolve()))
    return True

def pack_services(root):
    sources=json.loads((root/'.run/source-classpaths.json').read_text())
    with tempfile.TemporaryDirectory(prefix='runtime-package-',dir=root/'.run') as temp:
        stage=Path(temp)/'runtime';stage.mkdir();services={};copied={}
        for name,classpath in sources.items():
            entries=[]
            for part in classpath.split(os.pathsep):
                path=Path(part)
                if path.is_dir():
                    module=path.parts[path.parts.index('modules')+1]
                    relative=f"services/{module}.jar" if module not in ('platform','contracts') else f"shared/{module}.jar"
                    if relative not in copied:
                        dest=stage/relative;dest.parent.mkdir(parents=True,exist_ok=True)
                        with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
                            for p in sorted(path.rglob('*')):
                                if p.is_file():z.write(p,str(p.relative_to(path)))
                        copied[relative]=dest
                elif path.suffix=='.jar' and path.is_file():
                    relative='lib/'+path.name
                    if relative not in copied:
                        dest=stage/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest);copied[relative]=dest
                    elif sha(copied[relative])!=sha(path):raise ValueError('Conflicting dependency '+path.name)
                else:raise ValueError('Missing classpath entry '+str(path))
                entries.append(relative)
            services[name]=dict(mainClass=f'services.{name}.routes.ServiceMain',classpath=entries)
        manifest=dict(format=2,sourceHash=source_hash(root),services=services,artifacts=[dict(path=k,size=v.stat().st_size,sha256=sha(v)) for k,v in copied.items()])
        (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        runtime=root/'backend/runtime'
        if runtime.exists():runtime.rename(root/'.run'/f'runtime-backup-{time.time_ns()}')
        shutil.move(str(stage),str(runtime))
    validated(root);activate(root)
    print(f'Packaged {len(services)} independent Scala applications; dependencies deduplicated.')

def pack(root):
    if (root/'config/services.json').exists():return pack_services(root)
    parts=(root/'.run/classpath').read_text().split(os.pathsep);classes=Path(parts[0])
    if not classes.is_dir():raise ValueError('请先使用 APERTURE_BUILD_FROM_SOURCE=1 构建后端')
    (root/'.run').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='runtime-package-',dir=root/'.run') as temp:
        stage=Path(temp)/'runtime';(stage/'lib').mkdir(parents=True)
        app=stage/'app.jar'
        with zipfile.ZipFile(app,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(classes.rglob('*')):
                if p.is_file():z.write(p,str(p.relative_to(classes)))
        artifacts=[app];seen=set()
        for value in parts[1:]:
            jar=Path(value)
            if jar.suffix!='.jar' or not jar.is_file():raise ValueError('类路径包含无效依赖')
            if jar.name in seen:raise ValueError('重复依赖名称：'+jar.name)
            seen.add(jar.name);dest=stage/'lib'/jar.name;shutil.copy2(jar,dest);artifacts.append(dest)
        manifest=dict(format=1,sourceHash=source_hash(root),artifacts=[dict(path=str(p.relative_to(stage)),size=p.stat().st_size,sha256=sha(p)) for p in artifacts])
        (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        runtime=root/'backend/runtime'
        if runtime.exists():
            if not (runtime/'manifest.json').exists():raise ValueError('运行包目录已有未知文件，未覆盖')
            runtime.rename(root/'.run'/f'runtime-backup-{time.time_ns()}')
        shutil.move(str(stage),str(runtime))
    if validated(root) is None:raise ValueError('运行包生成后验证失败')
    print(f'已打包 Scala 应用和 {len(parts)-1} 个依赖 JAR，SHA256 校验通过。')
if __name__=='__main__':
    command=sys.argv[1] if len(sys.argv)>1 else 'check'
    try:
        if command=='pack':pack(ROOT)
        elif command=='check':raise SystemExit(0 if validated(ROOT) else 1)
        elif command=='activate':
            if not activate(ROOT):raise SystemExit(1)
            print('预编译 Scala 后端及依赖已通过校验，跳过 sbt/Maven 下载。')
        else:raise SystemExit(2)
    except CorruptRuntime as e:
        print(f'预编译后端不可用：{e}；请重新下载发布包。',file=sys.stderr);raise SystemExit(2)

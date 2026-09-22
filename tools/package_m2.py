"""Assemble an allowlisted portable Windows desktop package from installed tools."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
CLIENT=('m2_package_setup.py','m2_launcher.py','m2_setup.py','m2_pipe.py','m2_provisioning.py','m2_security.py',
        'm2_client.py','m2_limits.py','naim_native_probe.py')


def build(destination):
    destination=Path(destination).resolve()
    if sys.platform!='win32' or sys.version_info[:3]!=(3,14,3): raise RuntimeError('Requires installed Windows Python 3.14.3')
    archive=Path(str(destination)+'.zip')
    if archive.exists(): raise FileExistsError('Archive already exists')
    destination.mkdir(parents=True,exist_ok=False)
    runtime=Path(sys.base_prefix); target=destination/'runtime'; target.mkdir()
    for name in ('python.exe','python3.dll','python314.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt'):
        shutil.copyfile(runtime/name,target/name)
    shutil.copytree(runtime/'Lib',target/'Lib',ignore=shutil.ignore_patterns('site-packages','__pycache__','*.pyc','test','tests','idlelib','tkinter','ensurepip','venv'))
    shutil.copytree(runtime/'DLLs',target/'DLLs',ignore=shutil.ignore_patterns('*.pdb','*.lib','*.exp','__pycache__'))
    (target/'python314._pth').write_text('Lib\nDLLs\n../tools\n',encoding='ascii')
    (destination/'tools').mkdir()
    for name in CLIENT: shutil.copyfile(ROOT/'tools'/name,destination/'tools'/name)
    for name in ('ndx_fixture.exe','SDL2.dll'): shutil.copyfile(ROOT/'local/m2/desktop-verified'/name,destination/name)
    notices=destination/'licenses'; notices.mkdir()
    licenses={
        'Python-third-party.html':runtime/'Doc/html/license.html',
        'SDL2.txt':ROOT/'local/m2/SDL2-2.30.12/LICENSE.txt',
        'LVGL.txt':ROOT/'local/m2/esp32-compile-v2/components/lvgl__lvgl/LICENCE.txt',
        'cJSON.txt':Path.home()/'.espressif/esp-idf-v5.2/components/json/cJSON/LICENSE'}
    for name,source in licenses.items(): shutil.copyfile(source,notices/name)
    for name,script,extra in [('Launch.cmd','m2_launcher.py',''),('Fixture.cmd','m2_launcher.py','--fixture '),('Setup.cmd','m2_package_setup.py','')]:
        (destination/name).write_text('@echo off\r\n"%~dp0runtime\\python.exe" -B "%~dp0tools\\'+script+'" '+extra+'%*\r\nset "ndx_exit=%errorlevel%"\r\nif not "%ndx_exit%"=="0" pause\r\nexit /b %ndx_exit%\r\n',encoding='ascii',newline='')
    shutil.copyfile(ROOT/'docs/m2-package.md',destination/'README.md')
    (destination/'docs').mkdir()
    for name in ('m2-setup.md','m2-trust.md','m2-provisioning.md'):
        shutil.copyfile(ROOT/'docs'/name,destination/'docs'/name)
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    files={p.relative_to(destination).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(destination.rglob('*')) if p.is_file()}
    manifest={'format':1,'source_revision':revision,'python':sys.version.split()[0],
              'source_modified':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),'files':files}
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding='utf-8')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as bundle:
        for p in sorted(destination.rglob('*')):
            if p.is_file():
                entry=zipfile.ZipInfo(p.relative_to(destination).as_posix(),date_time=(2026,1,1,0,0,0))
                entry.compress_type=zipfile.ZIP_DEFLATED; bundle.writestr(entry,p.read_bytes())
    return archive

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',required=True)
    print(build(parser.parse_args().out))

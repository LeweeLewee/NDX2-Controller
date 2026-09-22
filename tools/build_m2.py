"""Reproducible local build runner. Never uploads/flashes or changes SDK versions."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def run(args):
    sdk=Path(args.sdk).resolve()
    if args.target=='desktop':
        tools=ROOT/'local/m2/build-tools'
        cmake=tools/'cmake/data/bin/cmake.exe'
        for name,action in [('zig-ar.cmd','ar'),('zig-ranlib.cmd','ranlib')]:
            wrapper='@echo off\n@"%~dp0ziglang\\zig.exe" '+action+' %*\n'
            if not (tools/name).exists() or (tools/name).read_text()!=wrapper: (tools/name).write_text(wrapper)
        output=ROOT/'local/m2/desktop-verified'
        command=[str(cmake),'-S',str(ROOT/'firmware/desktop'),'-B',str(output),'-G','Ninja',
            '-DCMAKE_BUILD_TYPE=Debug','-DCMAKE_MAKE_PROGRAM='+(tools/'ninja/data/bin/ninja.exe').as_posix(),
            '-DCMAKE_AR='+(tools/'zig-ar.cmd').as_posix(),'-DCMAKE_RANLIB='+(tools/'zig-ranlib.cmd').as_posix(),
            '-DCMAKE_C_COMPILER='+(tools/'ziglang/zig.exe').as_posix(),'-DCMAKE_C_COMPILER_ARG1=cc',
            '-DCMAKE_CXX_COMPILER='+(tools/'ziglang/zig.exe').as_posix(),'-DCMAKE_CXX_COMPILER_ARG1=c++',
            '-DLVGL_SOURCE_DIR='+(ROOT/args.project/'components/lvgl__lvgl').as_posix(),
            '-DCJSON_SOURCE_DIR='+(sdk/'components/json/cJSON').as_posix(),
            '-DSDL2_DIR='+(ROOT/'local/m2/SDL2-2.30.12/x86_64-w64-mingw32/lib/cmake/SDL2').as_posix()]
        subprocess.run(command,check=True)
        subprocess.run([str(cmake),'--build',str(output),'--target','ndx_fixture','controller_test','bridge_protocol_test','ui_recovery_test','preferences_test','desktop_transport_test','-j','4'],check=True)
        import shutil
        shutil.copyfile(ROOT/'local/m2/SDL2-2.30.12/x86_64-w64-mingw32/bin/SDL2.dll',output/'SDL2.dll')
        subprocess.run([str(tools/'cmake/data/bin/ctest.exe'),'--test-dir',str(output),'--output-on-failure'],check=True)
    else:
        from prepare_m2_firmware import sync_sources
        sync_sources(ROOT/args.project)
        python=Path.home()/'.espressif/python_env/idf5.2_py3.11_env/Scripts/python.exe'
        env=os.environ.copy(); env['IDF_PATH']=str(sdk)
        output=subprocess.check_output([str(python),str(sdk/'tools/idf_tools.py'),'export','--format','key-value'],env=env,text=True)
        for line in output.splitlines():
            if '=' in line:
                key,value=line.split('=',1)
                if key=='PATH': value=value.replace('%PATH%',env['PATH'])
                env[key]=value
        output=Path.home()/'.espressif/ndx2-m2-build'
        subprocess.run([str(python),str(sdk/'tools/idf.py'),'-B',str(output),'-D','IDF_TARGET=esp32s3','build'],
                       cwd=ROOT/args.project,env=env,check=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('target',choices=['desktop','esp32'])
    parser.add_argument('--sdk',default=str(Path.home()/'.espressif/esp-idf-v5.2'))
    parser.add_argument('--project',default='local/m2/esp32-compile-v2')
    run(parser.parse_args())

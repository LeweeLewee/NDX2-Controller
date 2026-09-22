"""Silent local preferences restart test: two actual native LVGL processes."""
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import zlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def main():
    captures=ROOT/'local/m2/native-captures'; captures.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'preferences.bin'
        env=os.environ.copy(); env['SDL_VIDEODRIVER']='dummy'
        for mode in ('save','check'):
            result=subprocess.run([str(ROOT/'local/m2/desktop-verified/ndx_fixture.exe'),
                '--preferences',str(path),'--preferences-smoke',mode,'--smoke',str(captures)],
                cwd=ROOT,env=env,timeout=20,capture_output=True,text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            if result.returncode: raise RuntimeError(result.stdout+result.stderr+f'Native preferences failed: {result.returncode}')
            print(result.stdout.strip())
        raw=path.read_bytes()
        assert len(raw)==12 and raw[:8]==b'NDPF'+bytes((1,1,65,5))
        assert struct.unpack('<I',raw[8:])[0]==zlib.crc32(raw[:8])
        for name in ('14-preferences-saved','15-preferences-restored'):
            picture=Image.open(captures/(name+'.bmp')).convert('RGB')
            assert picture.size==(800,480) and picture.getpixel((790,390))==(41,38,32)
            picture.save(captures/(name+'.png'))
        print('PASS separate-process persistence and actual restored palette pixels; no network or audio')

if __name__=='__main__': main()

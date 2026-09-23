"""Render the native design matrix and report desktop-only visual gate evidence."""
import argparse
import json
import re
from pathlib import Path
import subprocess
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
CASES = ('01-sage','02-sand','03-slate','04-paused','05-long-title','06-missing-art',
         '07-offline-unknown','08-pending','09-find','10-queue','11-settings','12-display','13-detail')

def luminance(value):
    channels = [(value >> shift & 255) / 255 for shift in (16,8,0)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return sum(c*w for c,w in zip(linear,(.2126,.7152,.0722)))

def main(output):
    output=output.resolve()
    if not output.is_relative_to((ROOT/'local').resolve()):
        raise ValueError('Review artifacts must stay in ignored local/')
    output.mkdir(parents=True,exist_ok=True)
    result=subprocess.run([str(ROOT/'local/m2/desktop-verified/ui_visual_test.exe'),str(output)],check=True,cwd=ROOT,capture_output=True,text=True)
    print(result.stdout)
    for name in CASES:
        picture=Image.open(output/(name+'.ppm')).convert('RGB')
        assert picture.size==(800,480)
        picture.save(output/(name+'.png'))
    # Evaluate enabled text, not intentionally disabled controls or artwork.
    palette={name:tuple(int(c,16) for c in colours.split()) for name,colours in
             re.findall(r'PALETTE (sage|sand|slate) ([0-9a-f]{6} [0-9a-f]{6} [0-9a-f]{6})',result.stdout)}
    assert len(palette)==3
    contrast={}
    for name,(bg,fg,secondary) in palette.items():
        values=[(luminance(c)+.05)/(luminance(bg)+.05) for c in (fg,secondary)]
        assert values[0]>=7 and values[1]>=4.5
        contrast[name]={'primary':round(values[0],2),'secondary':round(values[1],2)}
    report={'native_screens':len(CASES),'contrast':contrast,'review':'Human visual inspection required',
            'limits':'Desktop evidence only. Physical viewing/touch/contrast/power and live photographic artwork remain open.'}
    (output/'report.json').write_text(json.dumps(report,indent=2))
    cards=''.join(f'<figure><img src="{name}.png" width="800" height="480"><figcaption>{name}</figcaption></figure>' for name in CASES)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>River Stone native visual review</title>'
        '<style>body{background:#181d19;color:#e6eddd;font:18px system-ui;margin:32px}main{display:grid;gap:32px;grid-template-columns:repeat(auto-fit,minmax(480px,1fr))}figure{margin:0}img{width:100%;height:auto}figcaption{padding:12px 0;color:#b3c0aa}p{max-width:900px}</style>'
        '<h1>River Stone / Native visual review</h1><p>Actual LVGL pixels with synthetic state and original geometric demo sleeves. No live audio or provider artwork. This board is review evidence, not a browser implementation of the UI.</p>'
        '<p>Inspect hierarchy, long text, clear status, palette consistency and controls. Physical coffee-table readability and touch remain separate tests.</p><main>'+cards+'</main>',encoding='utf-8')
    print(json.dumps(report,indent=2))
    print(output/'index.html')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,default=ROOT/'local/m2/design-review')
    main(parser.parse_args().out)

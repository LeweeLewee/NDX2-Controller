"""Small M3 keeper/nut fit coupon; not a phone-fit reprint."""
import argparse,sys,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);a=p.parse_args();sys.path.insert(0,a.deps)
import cadquery as cq
out=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/iphone-mount/shell-study-v1';out.mkdir(exist_ok=True)
base=cq.Workplane('XY').box(24,22,2).val().translate((0,0,1))
boss=cq.Workplane('XY').box(12,10,10.3).val().translate((0,0,7.15))
body=base.fuse(boss)
hole=cq.Workplane('XY').circle(1.7).extrude(16).val()
hex=cq.Workplane('XY',origin=(0,0,6.8)).polygon(6,6.8).extrude(2.8).val()
slot=cq.Workplane('XY').box(6,12,2.8).val().translate((0,-4,8.2))
body=body.cut(hole).cut(hex).cut(slot).clean()
bar=cq.Workplane('XY').box(12,18,3).val().translate((0,0,1.5)).cut(hole)
for name,shape in [('keeper-nut-coupon',body),('keeper-bar-coupon',bar)]:
 assert shape.isValid() and len(shape.Solids())==1
 cq.exporters.export(shape,str(out/(name+'.stl')),tolerance=.04,angularTolerance=.1)
 cq.exporters.export(shape,str(out/(name+'.step')))
print('Two valid coupon solids exported. Use M3 nut/screw trial, not phone clamping.')

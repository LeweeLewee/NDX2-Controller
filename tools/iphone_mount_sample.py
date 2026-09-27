"""Open iPhone aperture fit sample. CadQuery 2.8; millimetres. Not a finished cradle."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);a=p.parse_args()
sys.path.insert(0,str(Path(a.deps).resolve()))
import cadquery as cq
out=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/iphone-mount/sample-v1'
out.mkdir(parents=True,exist_ok=True)
def rounded(w,h,r,z,d):
 return cq.Workplane('XY',origin=(0,0,z)).rect(w,h).extrude(d).edges('|Z').fillet(r).val()
# Front face on bed. No bridging: rear stiffeners grow out of the flat flange.
frame=rounded(170,95,9,0,1.2).cut(rounded(138.9,63.7,3,-1,4))
# Outboard long-edge stiffeners; no short-end walls, button slots or guessed mic holes.
for y in (-41,41):
 rail=cq.Workplane('XY').box(146,3,4).val().translate((0,y,3.2))
 frame=frame.fuse(rail)
frame=frame.clean()
parts={'aperture-frame':frame}
# Loose spacer gauges, not permanent gasket or clamps. Select locations on real phone.
for t in (.4,.8):
 parts[f'spacer-{t:g}mm']=cq.Workplane('XY').box(12,3,t).val().translate((0,0,t/2))
checks={'status':'unprinted fit sample; not a retaining cradle or acoustic validation',
'aperture_mm':[138.9,63.7],'corner_radius_mm':3,'overlap_mm':6,
'front_lip_thickness_mm':1.2,'spacer_options_mm':[.4,.8],
'resulting_glass_recess_mm':[1.6,2.0],
'stiffener_inner_gap_mm':79,'nominal_phone_width_mm':75.7,
'parts':{}}
mesh={}
for name,s in parts.items():
 assert s.isValid() and len(s.Solids())==1 and s.Volume()>0
 cq.exporters.export(s,str(out/(name+'.stl')),tolerance=.025,angularTolerance=.1)
 cq.exporters.export(s,str(out/(name+'.step')))
 b=s.BoundingBox()
 checks['parts'][name]={'valid_solid':True,'solid_count':len(s.Solids()),'volume_mm3':s.Volume(),'bounds_mm':[b.xlen,b.ylen,b.zlen]}
 v,f=s.tessellate(.025,.1);mesh[name]={'vertices':[[q.x,q.y,q.z] for q in v],'faces':f}
assert abs(frame.intersect(rounded(138.9,63.7,3,-.5,2)).Volume())<1e-6
checks['aperture_solid_intersection_mm3']=0
(out/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
(out/'preview-meshes.json').write_text(json.dumps(mesh))
print(json.dumps(checks,indent=2))

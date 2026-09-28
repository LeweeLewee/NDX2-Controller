"""Open iPhone aperture fit sample. CadQuery 2.8; millimetres. Not a finished cradle."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);p.add_argument('--revision',choices=['v1','v2'],default='v2');a=p.parse_args()
sys.path.insert(0,str(Path(a.deps).resolve()))
import cadquery as cq
out=Path(__file__).resolve().parents[1]/('docs/hardware/river-stone/iphone-mount/sample-'+a.revision)
out.mkdir(parents=True,exist_ok=True)
def rounded(w,h,r,z,d):
 return cq.Workplane('XY',origin=(0,0,z)).rect(w,h).extrude(d).edges('|Z').fillet(r).val()
# Front face on bed. No bridging: rear stiffeners grow out of the flat flange.
frame=rounded(170,95,9,0,1.2).cut(rounded(138.9,63.7,3,-1,4))
# Outboard long-edge stiffeners; no short-end walls, button slots or guessed mic holes.
for y in (-41,41):
 rail=cq.Workplane('XY').box(146,3,4).val().translate((0,y,3.2))
 frame=frame.fuse(rail)
if a.revision=='v2':
 # Four loose locating tabs. Inner x faces at +/-76.45: 1 mm per end.
 # y=+/-24, length 12 leaves central 36 mm open at each short end.
 for x in (-77.45,77.45):
  for y in (-24,24):
   tab=cq.Workplane('XY').box(2,12,8).val().translate((x,y,5.2))
   frame=frame.fuse(tab)
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
if a.revision=='v2':
 checks.update({'end_tab_inner_gap_mm':152.9,'nominal_phone_length_mm':150.9,'end_clearance_each_mm':1.0,'end_tab_width_length_height_mm':[2,12,8],'end_tab_centres_xy_mm':[[x,y] for x in (-77.45,77.45) for y in (-24,24)],'central_end_opening_mm':36,'end_tab_top_z_mm':9.2})
 # Box is conservative for the body only: camera/buttons/ports are not mapped.
 phone_box=cq.Workplane('XY').box(150.9,75.7,8.3).val().translate((0,0,1.6+8.3/2))
 checks['nominal_body_interference_mm3']=abs(frame.intersect(phone_box).Volume())
 assert checks['nominal_body_interference_mm3']<1e-6
 for x in (-79,79):
  channel=cq.Workplane('XY').box(12,36,10).val().translate((x,0,6.21))
  assert abs(frame.intersect(channel).Volume())<1e-6
 checks['central_end_openings_clear_above_lip']=True
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

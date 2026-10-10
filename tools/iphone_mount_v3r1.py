"""Revise the exact passed v3 STEP aperture only; preserve its body fit geometry."""
import argparse,sys,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);a=p.parse_args();sys.path.insert(0,a.deps)
import cadquery as cq
base=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/iphone-mount'
src=base/'sample-v3/snug-frame-0p20.step';out=base/'sample-v3r1';out.mkdir(exist_ok=True)
def rr(r,z,h):return cq.Workplane('XY',origin=(0,0,z)).rect(138.9,63.7).extrude(h).edges('|Z').fillet(r).val()
old=cq.importers.importStep(str(src)).val()
# The R3 opening minus the R6.5 opening is four corner additions inside the lip only.
add=rr(3,0,1.2).cut(rr(6.5,-1,3.2))
new=old.fuse(add).clean()
assert old.isValid() and new.isValid() and len(new.Solids())==1
removed=abs(old.cut(new).Volume());added=abs(new.cut(old).Volume())
assert removed<1e-6 and abs(added-add.Volume())<1e-5
upper=cq.Solid.makeBox(400,400,30,cq.Vector(-200,-200,1.20001))
assert abs(new.intersect(upper).Volume()-old.intersect(upper).Volume())<1e-5
assert abs(new.intersect(rr(6.5,-1,12)).Volume())<1e-6
cq.exporters.export(new,str(out/'snug-frame-0p20-r6p5.step'))
cq.exporters.export(new,str(out/'snug-frame-0p20-r6p5.stl'),tolerance=.01,angularTolerance=.05)
v,f=new.tessellate(.025,.1)
(out/'preview-meshes.json').write_text(json.dumps({'aperture-frame':{'vertices':[[q.x,q.y,q.z] for q in v],'faces':f}}))
report={'status':'unprinted R6.5 aperture correction; source 0p20 body fit passed by user','source_step_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'clearance_per_side_mm':.2,'aperture_mm':[138.9,63.7],'corner_radius_mm':6.5,'valid_single_solid':True,'removed_original_volume_mm3':removed,'added_corner_volume_mm3':added,'upper_wall_volume_unchanged':True,'aperture_intersection_mm3':0,'limits':['No new physical corner test','No microphone, retention or thermal acceptance','Existing body fit imported; source validation not independently reproduced']}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

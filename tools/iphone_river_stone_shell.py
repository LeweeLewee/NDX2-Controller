"""Original 01 iPhone shell engineering study. Not a print or acoustic release."""
import argparse,sys,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);a=p.parse_args();sys.path.insert(0,a.deps)
import cadquery as cq
BASE=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/iphone-mount';OUT=BASE/'shell-study-v1';OUT.mkdir(exist_ok=True)
def log(s):print(s,flush=True)
def box(w,d,h,x=0,y=0,z=0):return cq.Workplane('XY').box(w,d,h).val().translate((x,y,z))
def rr(w,d,r,z,h):return cq.Workplane('XY',origin=(0,0,z)).rect(w,d).extrude(h).edges('|Z').fillet(r).val()
def cylinder(r,z,h,x,y):return cq.Workplane('XY',origin=(x,y,z)).circle(r).extrude(h).val()
def hexcut(x,y,z,h):return cq.Workplane('XY',origin=(x,y,z)).polygon(6,6.8).extrude(h).val()
s,c=math.sin(math.radians(50)),math.cos(math.radians(50))
def pose(sh):return sh.rotate((0,0,0),(0,1,0),180).rotate((0,0,0),(1,0,0),50).translate((0,-55+37.85*c-1.6*s,36+37.85*s+1.6*c))
def vol(a,b):return abs(a.intersect(b).Volume())
def profile(z,rx,ry,cx,cy,n):
 pts=[]
 for i in range(64):
  t=2*math.pi*i/64;u,v=math.cos(t),math.sin(t)
  pts.append(cq.Vector(cx+rx*math.copysign(abs(u)**(2/n),u),cy+ry*math.copysign(abs(v)**(2/n),v),z))
 return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts,periodic=True)])
profiles=[(0,101,68,0,0,3.3),(6,104,71,0,0,3.3),(22,105,72.5,0,0,3.2),(45,105,70,-1,2,3),(65,104,62,-1,5,2.8),(86,101,50,-2,8,2.7),(96,94,39,-2,10,2.6),(102,70,23,-3,14,2.4),(105,35,10,-3,16,2.2)]
# Mesh Booleans avoid pathological BRep fusion between the detailed fit wall and loft.
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'output/crescent-mockup-v1/.deps'))
import trimesh
import numpy as np
class MeshSolid:
 def __init__(self,source):
  if isinstance(source,trimesh.Trimesh):self.m=source
  else:
   v,f=source.tessellate(.04,.08);self.m=trimesh.Trimesh(vertices=[[q.x,q.y,q.z] for q in v],faces=f,process=True);self.m.fix_normals()
 def cut(self,b):return MeshSolid(trimesh.boolean.difference([self.m,b.m],engine='manifold'))
 def fuse(self,b):return MeshSolid(trimesh.boolean.union([self.m,b.m],engine='manifold'))
 def intersect(self,b):return MeshSolid(trimesh.boolean.intersection([self.m,b.m],engine='manifold'))
 def clean(self):
  pieces=self.m.split(only_watertight=False)
  meaningful=[q for q in pieces if abs(q.volume)>1e-5]
  return MeshSolid(trimesh.util.concatenate(meaningful)) if len(meaningful)<len(pieces) else self
 def isValid(self):return self.m.is_watertight and self.m.is_winding_consistent
 def Solids(self):return self.m.split()
 def Volume(self):return float(self.m.volume)
 def translate(self,v):
  m=self.m.copy();m.apply_translation(v);return MeshSolid(m)
 def rotate(self,origin,end,deg):
  m=self.m.copy();direction=np.array(end)-np.array(origin);m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(deg),direction,origin));return MeshSolid(m)
 def tessellate(self,*args):return [cq.Vector(*v) for v in self.m.vertices],self.m.faces.tolist()
_cad_box,_cad_rr,_cad_cylinder,_cad_hex=box,rr,cylinder,hexcut
box=lambda *v,**k:MeshSolid(_cad_box(*v,**k))
rr=lambda *v,**k:MeshSolid(_cad_rr(*v,**k))
cylinder=lambda *v,**k:MeshSolid(_cad_cylinder(*v,**k))
hexcut=lambda *v,**k:MeshSolid(_cad_hex(*v,**k))
outer_cad=cq.Solid.makeLoft([profile(*v) for v in profiles],False)
cq.exporters.export(outer_cad,str(OUT/'outer-loft-source.step'))
outer=MeshSolid(outer_cad)
# Front facet shares the fitted frame's front datum. Small edge relief can follow print trial.
outer=outer.cut(pose(box(400,400,300,z=-150)))
assert outer.isValid();log('Outer valid (mesh Boolean)')
inner_profiles=[(-4,97,64,0,0,3.3)]+[(z if z<86 else z-3,rx-3.5,ry-3.5,cx,cy,n) for z,rx,ry,cx,cy,n in profiles[1:-1]]
inner_cad=cq.Solid.makeLoft([profile(*v) for v in inner_profiles],False)
cq.exporters.export(inner_cad,str(OUT/'inner-loft-source.step'))
inner=MeshSolid(inner_cad)
# Keep a continuous 1.2 mm face skin; the raw cavity loft otherwise opens the front.
inner=inner.cut(pose(box(400,400,300,z=-148.8)))
shell=outer.cut(inner)
# Remove shell intrusions behind the screen, then restore the precise passed wall.
shell=shell.cut(pose(rr(160,85,11,1.2,55)))
shell=shell.cut(pose(rr(138.9,63.7,6.5,-10,80)))
fit=MeshSolid(trimesh.load_mesh(BASE/'sample-v3r1/snug-frame-0p20-r6p5.stl',process=True))
log('Imported passed frame')
fit_world=pose(fit);shell=shell.fuse(fit_world);log('Fitted frame integrated by mesh union')
# Broad bay cavity; this is an envelope, not exact bank restraint yet.
bank=box(147,72,28,y=16,z=22);bay=box(151,76,32,y=16,z=22)
shell=shell.cut(bay)
# Underside opening and flush cover, 0.3 mm perimeter gap.
opening=rr(190,120,24,-5,10)
shell=shell.cut(opening)
cover=rr(189.4,119.4,23.7,0,3)
base_fasteners=[(x,y) for x in (-83,83) for y in (-43,43)]
for x,y in base_fasteners:
 boss=cylinder(6,3,10,x,y).fuse(box(12,22,10,x=x,y=y+math.copysign(9,y),z=8))
 shell=shell.fuse(boss.intersect(outer))
 shell=shell.cut(cylinder(1.7,2,12,x,y)).cut(hexcut(x,y,9,5))
 cover=cover.cut(cylinder(1.7,-1,5,x,y)).cut(cylinder(3.1,-.1,1.9,x,y))
# Bank supports: 0.5 mm pad space above four 4.5 mm risers; no hard battery clamping.
for x in (-60,60):
 for y in (-12,44):cover=cover.fuse(box(12,10,4.5,x=x,y=y,z=5.25))
# Two 10 mm removable strap paths and sheltered underside ventilation.
for x in (-50,50):
 for y in (-25,57):cover=cover.cut(box(10.4,2.4,6,x=x,y=y,z=2))
for x in (-25,-15,-5,5,15,25):cover=cover.cut(box(2,12,6,x=x,y=52,z=2))
cover=cover.clean()
# Rear keeper bars on hard stops. Pads only at the chassis perimeter, away from camera.
keepers={};pads={}
for x in (-35,0):
 bar=box(12,98,3,x=x,z=13)
 for y in (-44,44):
  boss=box(12,10,10.9,x=x,y=y,z=6.05)
  # Tether to the outer shell behind the face without crossing the body.
  boss=boss.fuse(box(12,14,5.6,x=x,y=y+math.copysign(7,y),z=3.4))
  shell=shell.fuse(pose(boss).intersect(outer))
  bore=cylinder(1.7,1.2,15,x,y)
  # Side-access nut slot at z6..8.8; no heat-set insert dimensions assumed.
  pocket=hexcut(x,y,6,2.8).fuse(box(6,12,2.8,x=x,y=y-math.copysign(4,y),z=7.4))
  shell=shell.cut(pose(bore)).cut(pose(pocket))
  bar=bar.cut(cylinder(1.7,10,7,x,y))
 for y in (-34,34):pads[f'pad-{x}-{y}']=pose(box(10,4,1.58,x=x,y=y,z=10.71))
 keepers[f'keeper-{x}']=pose(bar)
# Protected routes, above table plane. Exact inlet registration remains a physical check.
channels={
 'front-notch':pose(box(70,36,6.8,x=95,z=4.6)),
 'lightning-end':pose(box(70,52.8,15,x=-95,z=8.7)),
 'rear-camera':pose(box(90,24,9,x=85,y=22,z=15.5)),
}
for name,ch in channels.items():shell=shell.cut(ch)
# User measured plug, with separate provisional manufacturing allowances.
cable=json.loads((BASE/'cable-measurements.json').read_text(encoding='utf-8'))
plug_dims=cable['lightning_plug_mm'];allow=cable['provisional_clearance_mm']
plug_length=plug_dims['length']+allow['beyond_plug_end']+allow['cut_overlap_into_phone_end']
plug_x=-75.45+allow['cut_overlap_into_phone_end']-plug_length/2
plug=pose(box(plug_length,plug_dims['width']+2*allow['radial_each_side'],plug_dims['height']+2*allow['radial_each_side'],x=plug_x,z=7.6))
# Turn space remains a placeholder, centred at the measured flexible-cable start.
turn=pose(box(23,20,16,x=-75.45-plug_dims['length'],z=21.6))
shell=shell.cut(plug).cut(turn)
shell=shell.clean();log('Shell operations complete')
phone=pose(box(150.9,75.7,8.3,z=5.75))
camera=pose(box(34.3,31.1,5,x=55.836,y=19.62,z=12.42))
parts={'shell':shell,'cover':cover,**keepers}
report={'status':'engineering study, not released for printing','profiles':profiles,'aperture_mm':[138.9,63.7],'aperture_radius_mm':6.5,'integral_passed_fit':'Mesh Boolean union using source fit STL; editable outer/inner STEP loft sources; no fused final STEP','spacer_assumption_mm':.4,'keeper_hardstop_local_z_mm':11.5,'pad_gap_mm':1.58,'proposed_foam_uncompressed_mm':2,'base_fasteners_xy_mm':base_fasteners,'fasteners':'M3 clearance 3.4; nut pockets 6.8 circumscribed diameter; actual hardware trial pending','checks':{},'limits':['Cable assumptions unresolved','Microphone route geometry is not acoustic proof','Inner loft is not a constant normal wall offset','Numerical isolated components below 0.00001 mm3 are discarded','Camera location is conservative community-model estimate','Retainer pad pressure and service access untested']}
report['cable_inputs']=cable
report['plug_cut_mm']=[plug_length,plug_dims['width']+2*allow['radial_each_side'],plug_dims['height']+2*allow['radial_each_side']]
for name,sh in parts.items():
 report['checks'][name]={'valid':sh.isValid(),'solids':len(sh.Solids()),'volume_mm3':sh.Volume()}
 log(name+': '+str(report['checks'][name]))
 if sh.isValid():
  sh.m.export(OUT/(name+'.stl'))
  reread=trimesh.load_mesh(OUT/(name+'.stl'),process=True)
  report['checks'][name]['exported_stl_watertight']=bool(reread.is_watertight)
  report['checks'][name]['exported_stl_is_volume']=bool(reread.is_volume)
report['checks']['bank_shell_overlap']=vol(bank,shell)
report['checks']['bank_bay_shell_overlap']=vol(bay,shell)
report['checks']['cover_shell_overlap']=vol(cover,shell)
report['checks']['camera_shell_overlap']=vol(camera,shell)
# The box proxy overestimates rounded corners; record it without a false fit assertion.
report['checks']['nominal_phone_box_shell_overlap']=vol(phone,shell)
for name,sh in keepers.items():
 report['checks'][name+'_shell_overlap']=vol(sh,shell)
 report['checks'][name+'_bank_overlap']=vol(sh,bank)
 report['checks'][name+'_phone_box_overlap']=vol(sh,phone)
 report['checks'][name+'_outside_outer_volume']=abs(sh.cut(outer).Volume())
for name,ch in channels.items():report['checks'][name+'_channel_shell_overlap']=vol(ch,shell)


report['checks']['combined_shell']={'watertight':bool(shell.m.is_watertight),'consistent_winding':bool(shell.m.is_winding_consistent),'components':len(shell.m.split()),'volume_mm3':float(shell.m.volume),'bounds_mm':shell.m.bounds.tolist()}
preview={**parts,'phone':phone,'bank':bank,**pads,'camera':camera,'section':shell.intersect(box(250,350,250,x=-125,z=100))}
mesh={n:{'vertices':sh.m.vertices.tolist(),'faces':sh.m.faces.tolist()} for n,sh in preview.items()}
(OUT/'preview-meshes.json').write_text(json.dumps(mesh))
scene=trimesh.Scene({n:sh.m for n,sh in {**parts,'phone':phone,'bank':bank}.items()});scene.export(OUT/'assembly-study.glb')
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
log(json.dumps(report,indent=2))

"""Check actual community phone mesh against the enclosure; not physical proof."""
from pathlib import Path
import argparse,sys,json,math
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);p.add_argument('--mesh-deps',required=True);p.add_argument('--phone-step',required=True);a=p.parse_args()
sys.path.insert(0,a.deps);sys.path.insert(0,a.mesh_deps)
import cadquery as cq
import trimesh
out=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/iphone-mount/shell-study-v1'
raw=cq.importers.importStep(a.phone_step).val()
phone=raw.rotate((0,0,0),(1,0,0),180).rotate((0,0,0),(0,0,1),90).translate((75.456,-37.86,5.76))
s,c=math.sin(math.radians(50)),math.cos(math.radians(50))
phone=phone.rotate((0,0,0),(0,1,0),180).rotate((0,0,0),(1,0,0),50).translate((0,-55+37.85*c-1.6*s,36+37.85*s+1.6*c))
v,f=phone.tessellate(.025,.08);pm=trimesh.Trimesh(vertices=[[q.x,q.y,q.z] for q in v],faces=f,process=True);pm.merge_vertices(digits_vertex=4);pm.update_faces(pm.nondegenerate_faces());pm.remove_unreferenced_vertices();pm.fix_normals(multibody=True)
print('Phone mesh',pm.is_watertight,pm.is_winding_consistent,pm.is_volume,pm.volume,flush=True)
report={'status':'community CAD collision check only; not physical or acoustic proof','phone_tessellation_tolerance_mm':.025,'checks':{}}
for n in ('shell','keeper--35','keeper-0','cover'):
 m=trimesh.load_mesh(out/(n+'.stl'),process=True)
 m.merge_vertices(digits_vertex=4);m.update_faces(m.nondegenerate_faces());m.remove_unreferenced_vertices();m.fix_normals(multibody=True)
 print(n,m.is_volume,m.is_watertight,m.is_winding_consistent,flush=True)
 if not m.is_volume:
  report['status']='BLOCKED: exported '+n+' mesh is not a closed volume; collision and removal checks incomplete'
  report['checks'][n]={'watertight':bool(m.is_watertight),'is_volume':bool(m.is_volume)}
  (out/'phone-collision-check.json').write_text(json.dumps(report,indent=2)+'\n')
  raise SystemExit(report['status'])
 inter=trimesh.boolean.intersection([pm,m],engine='manifold')
 report['checks'][n]={'phone_overlap_mm3':abs(float(inter.volume)),'watertight':bool(m.is_watertight),'components':len(m.split()),'bounds_mm':m.extents.tolist()}
shell=trimesh.load_mesh(out/'shell.stl',process=True)
shell.merge_vertices(digits_vertex=4);shell.update_faces(shell.nondegenerate_faces());shell.remove_unreferenced_vertices();shell.fix_normals(multibody=True)
path=[]
for i in range(9):path.append(('rear',i,(0,i*s,-i*c)))
for i in range(5,126,5):path.append(('down',i,(0,8*s,-8*c-i)))
report['sampled_removal']={'bank_cover_and_keepers_removed':True,'rear_travel_mm':8,'then_vertical_down_mm':125,'samples':[],'continuous_sweep_proven':False}
for stage,travel,shift in path:
 moved=pm.copy();moved.apply_translation(shift)
 hit=trimesh.boolean.intersection([shell,moved],engine='manifold')
 report['sampled_removal']['samples'].append({'stage':stage,'travel_mm':travel,'overlap_mm3':abs(float(hit.volume))})
report['sampled_removal']['max_overlap_mm3']=max(q['overlap_mm3'] for q in report['sampled_removal']['samples'])
(out/'phone-collision-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

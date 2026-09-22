"""Prepare repeatable offline P1S slicing inputs from official Orca profiles."""
import argparse,json,hashlib,sys,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--slicer-zip',required=True);p.add_argument('--deps');a=p.parse_args()
if a.deps:sys.path.insert(0,str(Path(a.deps).resolve()))
import trimesh
root=Path(__file__).resolve().parents[1];src=root/'docs/hardware/river-stone/shell-v3';out=root/'docs/hardware/river-stone/slice-v1';out.mkdir(exist_ok=True)
z=zipfile.ZipFile(a.slicer_zip)
(out/'profiles-LICENSE.txt').write_bytes(z.read('LICENSE.txt'))
profiles={}
for n in z.namelist():
 if n.startswith('resources/profiles/BBL/') and n.endswith('.json'):
  d=json.loads(z.read(n));profiles[d.get('name',n)]=(n,d)
def flatten(name,seen=()):
 assert name not in seen
 n,d=profiles[name];base=flatten(d['inherits'],seen+(name,)) if d.get('inherits') else {}
 base.update(d);base.pop('inherits',None);return base
names={'machine':'Bambu Lab P1S 0.4 nozzle','process':'0.20mm Standard @BBL X1C','filament':'Generic PLA'}
for key,name in names.items():
 d=flatten(name)
 if key=='process':d.update({'wall_loops':'3','sparse_infill_density':'15%','enable_support':'0','brim_type':'no_brim','curr_bed_type':'Textured PEI Plate'})
 (out/(key+'.json')).write_text(json.dumps(d,indent=2)+'\n')
parts=[]
for i,name in enumerate(['retainer-mount-coupon','retainer-strip-coupon']):
 m=trimesh.load_mesh(src/(name+'.stl'));assert m.is_watertight;m.apply_translation([i*30,0,-m.bounds[0,2]]);parts.append(m)
trimesh.util.concatenate(parts).export(out/'fit-coupons.stl')
for name,angle in [('shell-underside-down',0),('shell-facet-down',130)]:
 m=trimesh.load_mesh(src/'shell-study.stl');m.apply_transform(trimesh.transformations.rotation_matrix(__import__('math').radians(angle),[1,0,0]));m.apply_translation([-m.bounds[:,0].mean(),-m.bounds[:,1].mean(),-m.bounds[0,2]]);m.export(out/(name+'.stl'))
d=json.loads((out/'process.json').read_text());d.update({'enable_support':'1','support_type':'normal(auto)','support_on_build_plate_only':'0'});(out/'process-shell.json').write_text(json.dumps(d,indent=2)+'\n')
(out/'source.json').write_text(json.dumps({'slicer_release':'OrcaSlicer 2.4.2','source_url':'https://github.com/OrcaSlicer/OrcaSlicer/releases/tag/v2.4.2','zip_sha256':hashlib.sha256(Path(a.slicer_zip).read_bytes()).hexdigest(),'base_profiles':names,'purpose':'Offline slicing study; Generic PLA is provisional, not a selected finish','source_stl_sha256':{n:hashlib.sha256((src/(n+'.stl')).read_bytes()).hexdigest() for n in ['shell-study','retainer-mount-coupon','retainer-strip-coupon']}},indent=2)+'\n')
print('Prepared profiles, fit plate and two shell orientations')

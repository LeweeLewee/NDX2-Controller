"""Check exported study meshes. Requires trimesh; does not slice or certify printing."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--deps');p.add_argument('--revision',choices=['v1','v2'],default='v2');args=p.parse_args()
if args.deps:sys.path.insert(0,str(Path(args.deps).resolve()))
import trimesh
out=Path(__file__).resolve().parents[1]/('docs/hardware/river-stone/iphone-mount/sample-'+args.revision)
report={}
for name in ['aperture-frame','spacer-0.4mm','spacer-0.8mm']:
    f=out/(name+'.stl');m=trimesh.load_mesh(f,process=True)
    r={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),'single_component':len(m.split())==1,'volume_cm3':float(m.volume/1000),'bounds_mm':m.bounds.tolist(),'size_mm':m.extents.tolist(),'within_256mm_cube':bool(max(m.extents)<256)}
    assert r['watertight'] and r['consistent_winding'] and r['single_component'] and r['volume_cm3']>0 and r['within_256mm_cube'],(name,r)
    report[name]=r
(out/'mesh-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

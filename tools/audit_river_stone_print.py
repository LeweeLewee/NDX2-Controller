"""Sample wall depth and classify overhang normals. Not a slicer or certification."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--deps');p.add_argument('--samples',type=int,default=2048);args=p.parse_args()
if args.deps:sys.path.insert(0,str(Path(args.deps).resolve()))
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/shell-v2'
m=trimesh.load_mesh(OUT/'shell-study.stl',process=True)
assert m.is_watertight and m.is_winding_consistent
tri=m.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
rng=np.random.default_rng(20260921)
ids=rng.choice(len(tri),args.samples,replace=True,p=m.area_faces/m.area)
results=[]
for i in ids:
    origin=tri[i].mean(axis=0);direction=-m.face_normals[i]
    h=np.cross(np.broadcast_to(direction,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h)
    valid=np.abs(a)>1e-9;inv=np.zeros_like(a);inv[valid]=1/a[valid]
    delta=origin-tri[:,0];u=inv*np.einsum('ij,ij->i',delta,h)
    q=np.cross(delta,e1);v=inv*(q@direction);t=inv*np.einsum('ij,ij->i',e2,q)
    hits=valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>.02)
    if np.any(hits):results.append({'mm':float(t[hits].min()),'point':origin.tolist(),'face':int(i)})
results.sort(key=lambda x:x['mm'])
overhangs={}
for name,up in [('underside_down',np.array([0,0,1])),('screen_facet_down',np.array([0,np.sin(np.radians(50)),-np.cos(np.radians(50))]))]:
    down=m.face_normals@up
    # Remove triangles at the support plane. This is a face-normal screen only.
    height=m.triangles_center@up;bed=float((m.vertices@up).min())
    mask=(down<-np.cos(np.radians(45)))&(height>bed+.3)
    overhangs[name]={'downward_area_over_45deg_mm2':float(m.area_faces[mask].sum()),'triangle_count':int(mask.sum())}
report={'mesh':'shell-study.stl','seed':20260921,'samples_requested':args.samples,'rays_with_exit':len(results),'minimum_sampled_normal_depth_mm':results[0]['mm'],'worst_samples':results[:12],'overhang_screen':overhangs,'limitations':['Discrete face-centre sampling cannot establish the global minimum thickness','Normal-depth rays may cross ribs or bosses; values are directional material depths','Overhang area is not a support-volume estimate or a slicer pass','Check actual material, layer height, bridging, hole fit and glass loading physically']}
(OUT/'print-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='worst_samples'},indent=2))

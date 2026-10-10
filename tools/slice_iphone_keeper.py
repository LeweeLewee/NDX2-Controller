"""Offline P1S keeper coupon slice; never connects to a printer."""
import sys,json,subprocess,shutil,hashlib,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parents[1];ws=root.parents[1]
sys.path.insert(0,str(ws/'output/crescent-mockup-v1/.deps'))
import trimesh
out=root/'docs/hardware/river-stone/iphone-mount/shell-study-v1';profiles=root/'docs/hardware/river-stone/slice-v1'
work=root/'local/iphone-keeper-slice';work.mkdir(parents=True,exist_ok=True)
meshes=[]
for name,x in [('keeper-nut-coupon',-17),('keeper-bar-coupon',17)]:
 m=trimesh.load_mesh(out/(name+'.stl'));m.apply_translation((x,0,0));meshes.append(m)
plate=trimesh.util.concatenate(meshes);plate.export(out/'keeper-coupons.stl')
args=[str(ws/'output/river-stone-slicer/orca/orca-slicer.exe'),str(out/'keeper-coupons.stl'),'--load-settings',str(profiles/'process.json')+';'+str(profiles/'machine.json'),'--load-filaments',str(profiles/'filament.json'),'--arrange','1','--slice','0','--export-3mf','keeper-coupons.3mf','--outputdir',str(work),'--datadir',str(work/'config')]
with (work/'slice.log').open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
assert r.returncode==0,(work/'slice.log').read_text(errors='replace')[-3000:]
g=work/'plate_1.gcode';assert g.exists();shutil.copy2(work/'keeper-coupons.3mf',out/'keeper-coupons.3mf')
report={'status':'offline provisional P1S/0.4/PLA/0.2 slice only; no print','input_sha256':hashlib.sha256((out/'keeper-coupons.stl').read_bytes()).hexdigest(),'gcode_sha256':hashlib.sha256(g.read_bytes()).hexdigest(),'profile_sha256':{n:hashlib.sha256((profiles/n).read_bytes()).hexdigest() for n in ['process.json','machine.json','filament.json']},'summary':[q for q in g.read_text().splitlines() if q.startswith(('; model printing time:','; filament used [','; total layer number:','; max_z_height:'))],'warnings':[q for q in (work/'slice.log').read_text(errors='replace').splitlines() if 'warning' in q.lower() or '1000C001' in q]}
with zipfile.ZipFile(work/'keeper-coupons.3mf') as z:
 info=ET.fromstring(z.read('Metadata/slice_info.config'))
 report['embedded_warnings']=[dict(q.attrib) for q in info.findall('.//warning')]
 report['plate_metadata']={q.get('key'):q.get('value') for q in info.findall('.//plate/metadata')}
(out/'keeper-slice-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

"""Run offline OrcaSlicer jobs. Never sends a print or contacts a printer."""
import argparse,json,subprocess,hashlib,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--slicer',required=True);p.add_argument('--job',choices=['fit-coupons','shell-underside-down','shell-facet-down'],required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=root/'docs/hardware/river-stone/slice-v1';work=root/'local/river-stone-slice'/a.job;work.mkdir(parents=True,exist_ok=True)
proc='process.json' if a.job=='fit-coupons' else 'process-shell.json'
args=[str(Path(a.slicer).resolve()),str(out/(a.job+'.stl')),'--load-settings',str(out/proc)+';'+str(out/'machine.json'),'--load-filaments',str(out/'filament.json'),'--arrange','1','--slice','0','--export-3mf',a.job+'.3mf','--outputdir',str(work),'--datadir',str(work/'config')]
with (work/'slice.log').open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
if r.returncode:raise RuntimeError((r.returncode,(work/'slice.log').read_text(errors='replace')[-3000:]))
g=work/'plate_1.gcode';assert g.exists() and g.stat().st_size>1000
if a.job=='fit-coupons':shutil.copyfile(work/(a.job+'.3mf'),out/(a.job+'.3mf'))
report={'job':a.job,'exit_code':r.returncode,'input_sha256':hashlib.sha256((out/(a.job+'.stl')).read_bytes()).hexdigest(),'gcode_sha256':hashlib.sha256(g.read_bytes()).hexdigest(),'profile_sha256':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in [proc,'machine.json','filament.json']},'gcode_summary':[s for s in g.read_text().splitlines() if s.startswith(('; model printing time:','; filament used [','; total layer number:','; max_z_height:'))]}
(out/(a.job+'-result.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

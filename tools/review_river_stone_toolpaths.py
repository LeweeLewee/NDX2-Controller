"""Summarize actual G-code extrusion by feature and render selected coupon layers."""
import json,math,re,hashlib,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];out=root/'docs/hardware/river-stone/slice-v1'
def parse(path):
 pos={'X':0.,'Y':0.,'Z':0.,'E':0.};relative_e=True;absolute_xyz=True;feature='Custom';height=None;stats=defaultdict(float);segs=[]
 for raw in path.read_text().splitlines():
  if raw.startswith('; FEATURE:'):feature=raw.split(':',1)[1].strip()
  if raw.startswith('; Z_HEIGHT:'):height=float(raw.split(':',1)[1])
  line=raw.split(';')[0].strip();cmd=line.split(' ')[0]
  if cmd=='M83':relative_e=True
  if cmd=='M82':relative_e=False
  if cmd=='G90':absolute_xyz=True
  if cmd=='G91':absolute_xyz=False
  vals={k:float(v) for k,v in re.findall(r'([XYZ EIJ])([-+]?(?:[0-9]*[.])?[0-9]+)',line) if k!=' '}
  if cmd=='G92':pos.update({k:v for k,v in vals.items() if k in pos});continue
  if cmd not in ['G0','G1','G2','G3']:continue
  nxt=pos.copy()
  for k in ['X','Y','Z']:
   if k in vals:nxt[k]=vals[k] if absolute_xyz else pos[k]+vals[k]
  extrusion=vals.get('E',0) if relative_e else vals.get('E',pos['E'])-pos['E']
  if 'E' in vals:nxt['E']=pos['E']+vals['E'] if relative_e else vals['E']
  if extrusion>0 and height is not None and feature!='Custom' and any(k in vals for k in ['X','Y','I','J']):
   stats[feature]+=extrusion
   if path.parent.name=='fit-coupons':
    points=[(pos['X'],pos['Y'])]
    if cmd in ['G2','G3'] and ('I' in vals or 'J' in vals):
     cx=pos['X']+vals.get('I',0);cy=pos['Y']+vals.get('J',0);r=math.hypot(pos['X']-cx,pos['Y']-cy);a=math.atan2(pos['Y']-cy,pos['X']-cx);b=math.atan2(nxt['Y']-cy,nxt['X']-cx);delta=(b-a)%(2*math.pi) if cmd=='G3' else -((a-b)%(2*math.pi))
     points += [(cx+r*math.cos(a+delta*i/20),cy+r*math.sin(a+delta*i/20)) for i in range(1,20)]
    points.append((nxt['X'],nxt['Y']));segs.append((height,feature,points))
  pos=nxt
 return dict(stats),segs
report={};coupon=[]
for job in ['fit-coupons','shell-underside-down','shell-facet-down']:
 path=root/'local/river-stone-slice'/job/'plate_1.gcode';stats,segs=parse(path);support=sum(v for k,v in stats.items() if 'Support' in k or 'support' in k);report[job]={'gcode_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'extrusion_length_by_feature_mm':stats,'support_commanded_volume_cm3':support*math.pi*.875**2/1000,'method':'Sum positive extrusion on XY/arc moves tagged by feature; excludes Custom startup/purge; commanded volume, not measured use'}
 with zipfile.ZipFile(root/'local/river-stone-slice'/job/(job+'.3mf')) as archive:
  cfg=ET.fromstring(archive.read('Metadata/slice_info.config'))
  report[job]['slicer_warnings']=[dict(w.attrib) for w in cfg.findall('.//warning')]
  report[job]['plate_metadata']={e.attrib['key']:e.attrib['value'] for e in cfg.findall('.//plate/metadata')}
 if job=='fit-coupons':coupon=segs
im=Image.new('RGB',(1280,820),'#f4f1eb');d=ImageDraw.Draw(im)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
d.text((35,20),'RIVER STONE / actual coupon toolpaths',(35,49,51),font=font(30));d.text((35,65),'P1S 0.4 mm | Generic PLA baseline | 0.20 mm layers | three walls | no supports',(35,49,51),font=font(19))
for i,z in enumerate([.2,2.6,7.6,9.8]):
 x=35+(i%2)*625;y=120+(i//2)*330;d.text((x,y),f'Layer at Z = {z:.1f} mm',(35,49,51),font=font(22))
 for h,feat,pts in coupon:
  if abs(h-z)<.001:
   color='#237f87' if 'wall' in feat.lower() else '#c59450'
   d.line([(x+30+(px-104.5)*10,y+55+(140-py)*10) for px,py in pts],fill=color,width=2)
d.text((35,785),'Teal: walls | ochre: infill/surfaces | openings remain visible; physical nut and screw fit untested',(35,49,51),font=font(17));im.save(out/'coupon-toolpaths.png');(out/'toolpath-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v['support_commanded_volume_cm3'] for k,v in report.items()},indent=2))

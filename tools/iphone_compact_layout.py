"""Compact packaging volumes, not a fitted/printable River Stone shell."""
import argparse,sys,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);p.add_argument('--plug-length',type=float,default=15);a=p.parse_args();sys.path.insert(0,a.deps)
import cadquery as cq
base=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/iphone-mount';out=base/'compact-layout-v1';out.mkdir(exist_ok=True)
def box(w,d,h,x=0,y=0,z=0):return cq.Workplane('XY').box(w,d,h).val().translate((x,y,z))
angle=math.radians(50);c,s=math.cos(angle),math.sin(angle)
# Sample frame front plane z=0; glass at z=1.6. Phone top is local +X.
def pose(sh):return sh.rotate((0,0,0),(0,1,0),180).rotate((0,0,0),(1,0,0),50).translate((0,-55+37.85*c-1.6*s,36+37.85*s+1.6*c))
phone=pose(box(150.9,75.7,8.3,z=1.6+8.3/2))
# Conservative whole-back reserve: guarantees more than the local 31.1x34.3x5 camera zone.
camera=pose(box(150.9,75.7,5,z=1.6+8.3+2.5))
frame=pose(cq.importers.importStep(str(base/'sample-v3r1/snug-frame-0p20-r6p5.step')).val())
bank=box(147,72,28,y=16,z=22);bay=box(151,76,32,y=16,z=22)
# Unmeasured cable reservations, not selected hardware or guaranteed bend radius.
plug=pose(box(a.plug_length,14,12,x=-75.45-a.plug_length/2,z=7.6))
turn=pose(box(a.plug_length+8,20,16,x=-75.45-a.plug_length/2,z=21.6))
port=box(20,72,32,x=-83.5,y=16,z=22)
outer=box(210,145,102,z=51)
parts={'phone-envelope':phone,'camera-rear-reserve':camera,'frame-r6p5':frame,'bank':bank,'bank-bay':bay,'phone-plug-reservation':plug,'cable-turn-reservation':turn,'bank-port-reservation':port}
report={'status':'packaging study only; bounding box is not a curved shell','old_bounds_mm':[240,170,105],'candidate_bounds_mm':[210,145,102],'phone_angle_deg':50,'spacer_assumption_mm':.4,'bank_model':'UGREEN 25683','bank_mm':[147,72,28],'plug_length_assumption_mm':a.plug_length,'cable_turn_box_mm':[a.plug_length+8,20,16],'camera_reserve':'5 mm behind the entire nominal body; conservative for local camera','frame_reference':'passed body wall with unprinted R6.5 aperture correction','checks':{},'limits':['No enclosure solid, wall-thickness or curved-shell fit claim','Cable dimensions, connector pose and bend radius unmeasured','Bank port reservation is worst-side placeholder, not actual port map','No retention, fastener, thermal or acoustic validation']}
assembly=cq.Assembly();mesh={}
for name,sh in parts.items():
 assert sh.isValid()
 outside=abs(sh.cut(outer).Volume())
 report['checks'][name]={'outside_candidate_box_mm3':outside}
 cq.exporters.export(sh,str(out/(name+'.step')))
 assembly.add(sh,name=name)
 v,f=sh.tessellate(.05,.1);mesh[name]={'vertices':[[q.x,q.y,q.z] for q in v],'faces':f}
for name,sh in [('phone',phone),('camera',camera),('frame',frame),('plug',plug),('turn',turn)]:
 inter=abs(sh.intersect(bay).Volume());report['checks'][name+'_versus_bank_bay_mm3']=inter
report['bounding_volume_reduction_percent']=100*(1-210*145*102/(240*170*105))
assembly.save(str(out/'packaging-study.step'))
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(out/'preview-meshes.json').write_text(json.dumps(mesh));print(json.dumps(report,indent=2))
# Dimensioned plan overlay; rectangular limits intentionally do not imply pebble contour.
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="760" viewBox="0 0 1000 760"><rect width="1000" height="760" fill="#f4f1e9"/><g font-family="Arial" fill="#293737"><text x="40" y="45" font-size="26">River Stone / compact packaging bounds</text><text x="40" y="78" font-size="17">Plan overlay only. Original 01 governs the future curved shell.</text><rect x="140" y="110" width="720" height="510" fill="none" stroke="#999" stroke-dasharray="8 6"/><rect x="185" y="147.5" width="630" height="435" rx="0" fill="none" stroke="#294f51" stroke-width="3"/><rect x="273.5" y="203" width="453" height="228" fill="#b4c6a4"/><rect x="273.65" y="384" width="452.7" height="146" fill="none" stroke="#3c5b6b" stroke-dasharray="5 3"/><text x="310" y="295" font-size="20">UGREEN bank bay 151 x 76</text><text x="305" y="462" font-size="20">Inclined phone projection</text><text x="40" y="655" font-size="19">Dashed grey: old 240 x 170 / dark green: candidate 210 x 145 mm</text><text x="40" y="689" font-size="17">Height 105 → 102 mm. Cable reservations appear in the STEP and clearance report.</text><text x="40" y="722" font-size="17">Unprinted study. Curved walls and microphone paths still to design.</text></g></svg>'''
(out/'bounds-overlay.svg').write_text(svg,encoding='utf-8')

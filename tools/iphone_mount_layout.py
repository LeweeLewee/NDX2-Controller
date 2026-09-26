"""Concept packaging layout; bounding envelopes, not a fitted shell or acoustic proof."""
import json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'docs/hardware/river-stone/iphone-mount';out.mkdir(exist_ok=True)
overlap=6.5
window=[round(d-2*overlap,1) for d in (150.9,75.7)]
a=math.radians(50);c,s=math.cos(a),math.sin(a)
def point(v,t):return (-55+v*c-t*s,36+v*s+t*c)
phone=[point(v,t) for v,t in [(0,0),(75.7,0),(75.7,-8.3),(0,-8.3)]]
# Rear allowance is deliberately conservative; it is not a measured camera height.
rear=[point(v,t) for v,t in [(0,-14.3),(75.7,-14.3)]]
bank={'x':[-73.5,73.5],'y':[-20,52],'z':[8,36]}
bay={'x':[-75.5,75.5],'y':[-22,54],'z':[6,38]}
# Rear inclined plane lies above the entire bay; its lowest value over bay is at ymin.
z_rear=36+(bay['y'][0]+55)*math.tan(a)-14.3/c
clear=z_rear-bay['z'][1];assert clear>0
r={'status':'provisional layout only; no shell, insertion, connector or acoustic clearance certification','phone_body_mm':[150.9,75.7,8.3],'phone_angle_deg':50,'phone_lower_front_yz_mm':[-55,36],'window_mm':window,'per_edge_overlap_mm':overlap,'nominal_glass_recess_mm':1.2,'bank_working_envelope_mm':[147,72,28],'bank_model_mapping':'user product name retained; manufacturer 25683 envelope used provisionally','bank_bay_mm':[151,76,32],'bank_bounds_xyz_mm':bank,'bay_bounds_xyz_mm':bay,'rear_extra_allowance_mm':6,'phone_side_corners_yz_mm':phone,'minimum_infinite_rear_plane_to_bay_vertical_gap_mm':clear,'planning_body_bounds_mm':[240,170,105],'phone_connector_reservation_mm':25,'bank_port_service_reservation_mm':25,'limits':['Overall silhouette and angle are proposals, not measured from the concept image','Rear allowance is not measured camera/cradle geometry','Plane versus box check only; curved shell and acoustic paths are not solids','No full insertion sweep, fastener positions, thermal test or print release']}
(out/'layout-checks.json').write_text(json.dumps(r,indent=2)+'\n')
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1060" viewBox="0 0 1400 1060"><rect width="1400" height="1060" fill="#f4f1e9"/><g font-family="Segoe UI,Arial" fill="#283a3b">']
def text(x,y,t,size=18):parts.append(f'<text x="{x}" y="{y}" font-size="{size}">{t}</text>')
def rect(x,y,w,h,fill,stroke='#526564',dash=''):
 parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-dasharray="{dash}"/>')
def poly(points,fill,stroke='#526564'):
 parts.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}"/>')
text(40,43,'01 RIVER STONE / concealed iPhone mounting layout',30);text(40,76,'Original 01 only • proposed envelopes and service paths • dimensions in mm • not fit CAD',18)
text(40,122,'1  FRONT / viewed normal to screen',22)
parts.append('<path d="M55 325 C45 200 115 144 250 144 C455 136 569 170 606 313 C625 385 551 404 350 402 L170 402 C93 400 54 382 55 325Z" fill="#c4bba5" stroke="#968b73"/>')
rect(139,208,377.25,189.25,'none','#617273','6 5');rect(139+overlap*2.5,208+overlap*2.5,window[0]*2.5,window[1]*2.5,'#2c4547');text(210,310,'137.9 × 62.7 window',20)
text(60,436,'Dashed: hidden 150.9 × 75.7 phone body');text(60,466,'Notch left / Lightning right; 6.5 overlap; mic paths open',16)
text(730,122,'2  SECTION / proposed 50° tilt',22)
# Each axis 2.5 px per mm, y rearwards right, z upwards.
def side(y,z):return (760+(y+85)*2.5,425-z*2.5)
parts.append('<path d="M770 425 C753 347 786 276 824 226 C860 160 949 145 990 166 C1120 189 1178 300 1175 425Z" fill="none" stroke="#968b73" stroke-width="3" stroke-dasharray="6 5"/>')
poly([side(*q) for q in phone],'#768a8a');poly([side(-22,6),side(54,6),side(54,38),side(-22,38)],'#c5d3b9');poly([side(-20,8),side(52,8),side(52,36),side(-20,36)],'#879c77')
parts.append('<path d="M'+' L'.join(f'{side(*q)[0]:.1f} {side(*q)[1]:.1f}' for q in rear)+'" stroke="#bd8437" stroke-width="4" fill="none"/>')
text(960,398,'UGREEN bank',16);text(760,466,f'Rear allowance to bank bay: {clear:.1f} mm vertical plane gap',16)
text(760,493,'Dashed body is illustrative; actual curved-shell fit unverified',15)
text(40,547,'3  UNDERSIDE / cover removed — plan projection',22)
# plan x mapped horizontal; y positive rear upward
parts.append('<ellipse cx="345" cy="770" rx="288" ry="204" fill="#ded8c8" stroke="#968b73"/>')
def plan(x,y):return (345+2.4*x,770-2.4*y)
x,y=plan(-75.5,54);rect(x,y,151*2.4,76*2.4,'#bdcfb1')
x,y=plan(-75.45,-6.34);rect(x,y,150.9*2.4,48.66*2.4,'none','#425d63','5 5')
x,y=plan(75.45,-12);rect(x,y,25*2.4,25*2.4,'#e2c295');text(529,929,'Cable',15)
x,y=plan(-100.5,25);rect(x,y,25*2.4,35*2.4,'#e2c295')
text(240,698,'Bank bay 151 × 76',17);text(205,864,'Phone projection above',17)
text(75,1004,'Side service space reserved; bank port orientation must be checked',16)
text(730,550,'4  MICROPHONES / protected zones',22)
for i,t in enumerate(['A  Front / notch: open space under left mask; no gasket over inlet.', 'B  Rear-camera zone: keep cradle and padding clear; vent to side.', 'C  Lightning end: keep mic openings clear of plug, cable and pads.', 'Each zone needs an independent short, broad route to room air.', 'No small sealed cavity or shared sealed gasket around the phone.', 'Exact inlet locations and passage sections await physical mapping.']):text(730,595+i*32,t,16)
text(730,835,'Assembly / service',22)
for i,t in enumerate(['Open underside → fit padded cradle and phone → connect lead.', 'Fit bank independently with removable restraint; close cover.', 'Keep access for buttons, unplugging and recovery underneath.', 'Body planning envelope: 240 W × 170 D × 105 H — provisional.', 'No glass pressure; no camera contact; no acoustic pass claimed.']):text(730,870+i*29,t,16)
parts.append('</g></svg>');(out/'mounting-layout.svg').write_text(''.join(parts),encoding='utf-8')
print(json.dumps(r,indent=2))

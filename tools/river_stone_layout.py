"""Generate a dimensioned packaging study, not manufacturing CAD. No network calls.
Python stdlib generates SVG and numerical checks; optional Pillow adds a preview PNG.
"""
from pathlib import Path
import math, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/hardware/river-stone';OUT.mkdir(parents=True,exist_ok=True)
W,D,H=220,155,105
angle=50;theta=math.radians(angle);s,c=math.sin(theta),math.cos(theta)
screen_w,screen_h,screen_t=112.4,75.1,17.7
front=(-42,34)
back=(front[0]+screen_t*s,front[1]-screen_t*c)
screen=[front,(front[0]+screen_h*c,front[1]+screen_h*s),(back[0]+screen_h*c,back[1]+screen_h*s),back]
# bounds x0,x1,y0,y1,z0,z1; installation allowances, not selected components
bays={'Battery':(-40,40,-10,54,6,32),'Charger':(42,92,-20,35,6,28),'Converter':(-92,-42,-5,23,6,20)}
checks={}
for name,(x0,x1,y0,y1,z0,z1) in bays.items():
    footprint=max((x/(W/2-3))**2+(y/(D/2-3))**2 for x in (x0,x1) for y in (y0,y1))
    clearance=-max(-(y-back[0])*s+(z-back[1])*c for y in (y0,y1) for z in (z0,z1))
    assert footprint<1 and clearance>0,(name,footprint,clearance)
    checks[name]={'bounds_mm':[x0,x1,y0,y1,z0,z1],'size_mm':[x1-x0,y1-y0,z1-z0],'inside_3mm_inset_ellipse':True,'normal_clearance_to_module_rear_plane_mm':round(clearance,2)}
for i,(a,aa) in enumerate(bays.items()):
    for b,bb in list(bays.items())[i+1:]:
        assert any(aa[k+1]<=bb[k] or bb[k+1]<=aa[k] for k in (0,2,4)),(a,b)
report={'status':'packaging allowances only; no full-shell collision or print validation','envelope_mm':[W,D,H],'screen_angle_deg':angle,'screen_depth_including_drawing_tolerance_mm':screen_t,'front_bottom_yz_mm':front,'screen_section_yz_mm':screen,'bays':checks,'board_bays_mutually_disjoint':True,'not_validated':['shell surface and wall offsets','mounts and fasteners','connector plugs and cable bends','antenna keepout','microphone hardware','heat and power','slicing and physical fit']}
(OUT/'clearance-checks.json').write_text(json.dumps(report,indent=2)+'\n')
try:
    from PIL import Image,ImageDraw,ImageFont
    im=Image.new('RGB',(1600,1120),'#f5f2eb');draw=ImageDraw.Draw(im)
    def font(size):
        try:return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',size)
        except OSError:return ImageFont.load_default()
except ImportError:im=None
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1120" viewBox="0 0 1600 1120"><rect width="1600" height="1120" fill="#f5f2eb"/>']
from html import escape
def text(x,y,t,size=20,color='#283336'):
    svg.append(f'<text x="{x}" y="{y+size}" font-family="Segoe UI, sans-serif" font-size="{size}" fill="{color}">{escape(t)}</text>')
    if im:draw.text((x,y),t,font=font(size),fill=color)
def line(points,color='#526064',width=2,fill=None):
    shape='polygon' if fill else 'polyline';p=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
    svg.append(f'<{shape} points="{p}" fill="{fill or "none"}" stroke="{color}" stroke-width="{width}"/>')
    if im:
        if fill:draw.polygon(points,fill=fill)
        draw.line(points+[points[0]] if fill else points,fill=color,width=width)
def rect(x,y,w,h,color,fill):line([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],color,2,fill)
text(55,30,'RIVER STONE / original 01 / stationary controller',34)
text(55,83,'Packaging study v1 | dimensions in mm | 220 W x 155 D x 105 H | screen 50 degrees from table',21)
text(55,119,'Accepted form: original pebble. This section defines internal allowances, not a replacement exterior design.',19)
text(95,185,'PLAN / cover removed',25);text(865,185,'CENTRE SECTION / front at left',25)
px,py,scale=360,420,2.3
plan=lambda x,y:(px+x*scale,py-y*scale)
ellipse=[plan(W/2*math.cos(a),D/2*math.sin(a)) for a in [i*math.tau/160 for i in range(161)]]
line(ellipse,'#8a8274',3,'#e2dbcc')
colors={'Battery':'#a8b9a3','Charger':'#d7bc91','Converter':'#a3b9c7'}
for name,(x0,x1,y0,y1,z0,z1) in bays.items():
    p=plan(x0,y1);rect(*p,(x1-x0)*scale,(y1-y0)*scale,'#53605b',colors[name])
    text(p[0]+6,p[1]+8,name,17)
    text(p[0]+6,p[1]+34,f'{x1-x0} x {y1-y0}',16)
    text(p[0]+6,p[1]+57,f'{z1-z0} high',15)
# Glass projected into plan: outline only to expose the low-level layout.
ymax=max(y for y,z in screen);ymin=min(y for y,z in screen)
line([plan(-56.2,ymin),plan(56.2,ymin),plan(56.2,ymax),plan(-56.2,ymax),plan(-56.2,ymin)],'#253b44',2)
text(282,610,'FRONT / user',18);text(253,215,'REAR / charging access',17)
text(99,655,'Outer footprint 220 x 155',20)
text(99,687,'Outlined rectangle: screen/module projection',18)
sx,sy,ss=1110,565,2.7
side=lambda y,z:(sx+y*ss,sy-z*ss)
# Illustrative centre profile follows screen lip; left/right shoulders follow original image at later surfacing stage.
profile=[(-77.5,8),(-74,19),(-63,28),(-48,32),(-42,34),(6.27,91.53),(17,102),(30,105),(47,96),(64,71),(74,42),(77.5,14),(69,0),(-66,0)]
line([side(y,z) for y,z in profile],'#8a8274',3,'#e2dbcc')
line([side(y,z) for y,z in screen],'#253b44',2,'#566b72')
line([side(y,z) for y,z in screen[:2]],'#172329',5)
b=bays['Battery'];p=side(b[2],b[5]);rect(*p,(b[3]-b[2])*ss,(b[5]-b[4])*ss,'#53605b',colors['Battery'])
text(p[0]+10,p[1]+12,'Battery allowance',16)
line([side(-64,3),side(64,3)],'#776451',4)
text(865,610,'Glass 112.4 x 75.1 | VA 95.54 x 54.36',20)
text(865,642,'Module depth allowance 17.7 (17.4 + 0.3)',20)
text(865,675,'3 mm underside cover / low battery / no dock',19)
text(55,755,'CONSTRUCTION',23)
text(55,794,'Main shell + recessed underside cover; screen supports and battery restraint still to detail.',20)
text(55,829,'Target flat underside joint, reusable screws, non-slip feet and discreet rear charging access.',20)
text(55,864,'Side section is illustrative: preserve the asymmetry and soft shoulders of original 01 during surfacing.',20)
text(55,932,'CHECKED',23)
text(55,970,'Reserved boxes do not overlap; fit within a 3 mm inset footprint; clear the inclined screen rear plane.',20)
text(55,1006,'Not yet checked: full shell, cables, mounting, antenna, microphone, thermal behaviour or print supports.',20)
text(55,1042,'Source: Waveshare 4.3B manufacturer drawing. Concept dimensions and component bays remain provisional.',18)
svg.append('</svg>');(OUT/'layout.svg').write_text('\n'.join(svg),encoding='utf-8')
if im:im.save(OUT/'layout.png')
print(json.dumps(checks,indent=2))

"""Render actual CAD tessellations with a depth buffer. Requires numpy and Pillow."""
from pathlib import Path
import json,math,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--revision',choices=['v1','v2','v3'],default='v3');args=p.parse_args()
OUT=Path(__file__).resolve().parents[1]/('docs/hardware/river-stone/shell-'+args.revision)
data=json.loads((OUT/'preview-meshes.json').read_text())
im=Image.new('RGB',(1600,1100),'#f3f0e9')
def font(n):
    try:return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
    except OSError:return ImageFont.load_default()
def label(x,y,t,n=20):ImageDraw.Draw(im).text((x,y),t,font=font(n),fill='#293537')
def render(items,origin,scale,az,el):
    az,el=map(math.radians,[az,el]);right=np.array([math.cos(az),math.sin(az),0]);up=np.array([-math.sin(az)*math.sin(el),math.cos(az)*math.sin(el),math.cos(el)]);depth=np.cross(right,up)
    pixels=np.array(im);zbuf=np.full((im.height,im.width),-np.inf)
    for name,col,shift in items:
        vs=np.array(data[name]['vertices'])+shift
        for f in data[name]['faces']:
            tri=vs[f];n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);length=np.linalg.norm(n)
            if length<1e-12:continue
            shade=.6+.4*abs(np.dot(n/length,np.array([.3,-.5,.81])))
            p=np.column_stack((origin[0]+scale*(tri@right),origin[1]-scale*(tri@up)));z=tri@depth
            lo=np.maximum(np.floor(p.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(p.max(axis=0)).astype(int),[im.width-1,im.height-1])
            if np.any(hi<lo):continue
            xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
            den=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
            if abs(den)<1e-9:continue
            b0=((p[1,1]-p[2,1])*(xx-p[2,0])+(p[2,0]-p[1,0])*(yy-p[2,1]))/den
            b1=((p[2,1]-p[0,1])*(xx-p[2,0])+(p[0,0]-p[2,0])*(yy-p[2,1]))/den;b2=1-b0-b1;zz=b0*z[0]+b1*z[1]+b2*z[2]
            region=np.s_[lo[1]:hi[1]+1,lo[0]:hi[0]+1];mask=(b0>=0)&(b1>=0)&(b2>=0)&(zz>zbuf[region])
            pixels[region][mask]=tuple(int(c*shade) for c in col);zbuf[region][mask]=zz[mask]
    im.paste(Image.fromarray(pixels))
sand=(192,184,163);black=(35,43,46);green=(145,173,147);blue=(133,159,181);gold=(191,165,116)
label(45,25,'RIVER STONE / shell and assembly study '+args.revision,32)
label(45,77,'CAD geometry, not a finish render | Waveshare 4.3B | original 01 remains the aesthetic reference',20)
render([('shell',sand,(0,0,0)),('module',black,(0,0,0)),('glass',(23,30,33),(0,0,0)),('va',(61,92,103),(0,0,0))] if 'glass' in data else [('shell',sand,(0,0,0)),('module',black,(0,0,0))],(425,475),2.8,-22,24)
label(145,595,'Assembled front / recessed landscape display',22)
render([('shell',sand,(0,0,0))]+[(n,(134,153,137),(0,0,0)) for n in ['retainer-left','retainer-right'] if n in data],(1190,275),2.5,-22,-50)
label(930,595,'Underside / removable retainers' if 'retainer-left' in data else 'Underside / cover removed',22)
items=[('section',sand,(0,0,0)),('module',black,(0,0,0)),('battery',green,(0,0,0)),('charger',gold,(0,0,0)),('converter',blue,(0,0,0)),('cover',sand,(0,0,-15))]
if 'section' in data:render(items,(450,995),2.5,-90,0)
label(80,1035,'Section / battery space / cover lowered for illustration',19)
label(880,745,'One main shell + removable underside cover',24)
label(880,790,'Four cover screws; no separate controller dock',21)
label(880,835,'Retainer pads and fasteners require a fit trial' if 'retainer-left' in data else 'Screen retention and cable openings still to detail',21)
label(880,880,'Study files are not a production or powered-build release',20)
label(880,925,'Colour identifies geometry; filament finish is not simulated',18)
im.save(OUT/'assembly-preview.png')
if 'supplier' in data:
    im=Image.new('RGB',(1600,900),'#f3f0e9')
    label(45,25,'IMPORTED WAVESHARE STEP / registration check',30)
    render([('supplier',sand,(0,0,0))],(420,660),4,-15,30)
    render([('supplier',sand,(0,0,0))],(1190,510),4,170,-15)
    label(150,805,'Front / lens side',22);label(1000,805,'Rear / electronics side',22)
    im.save(OUT/'supplier-registration.png')
print('Rendered previews')

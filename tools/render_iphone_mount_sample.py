"""Render actual CAD tessellations with a depth buffer. Requires numpy and Pillow."""
from pathlib import Path
import json,math,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--revision',choices=['v1','v2'],default='v2');args=p.parse_args()
OUT=Path(__file__).resolve().parents[1]/('docs/hardware/river-stone/iphone-mount/sample-'+args.revision)
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

label(45,30,f'iPhone aperture / open fit sample {args.revision}',32)
label(45,82,'Accepted 138.9 x 63.7 mm opening, R3 corners | Geometry preview; not the stone exterior',20)
render([('aperture-frame',(192,184,163),(0,0,0))],(790,375),4.7,-12,65)
label(60,695,'Rear view: four end tabs; 36 mm central end gaps; back open.' if args.revision=='v2' else 'Rear view: two outboard stiffeners; short ends and back remain open.',22)
label(60,745,'Loose 0.4 / 0.8 mm spacer gauges set 1.6 / 2.0 mm nominal glass recess.',22)
label(60,795,'Phone must be supported by hand: no clips, back plate or retention.',22)
label(60,845,'Do not place gauges across microphones, sensors or active display.',22)
label(60,895,'Acoustic path, real fit and touch access require physical checks.',22)
label(60,945,'Print front face down. P1S / 0.4 mm nozzle; no snap fit or clamping.',22)
im.save(OUT/'sample-preview.png')

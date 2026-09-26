"""Deterministic, fictional reference artwork for the silent iOS visual trial.
Procedural compositions transcribed from the supplied reference HTML; no network.
Still normalized and chunked by the real bridge contract.
"""
import io
import math
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

COLORS = [("6a796a", "243c34", "ddd6b7"), ("8b7160", "493b37", "e2c39b"),
          ("596875", "25343e", "ccd5ce"), ("4f6b6b", "1e2b2b", "d9e2d6"),
          ("6b3a36", "2a1716", "e9d3b8"), ("8a8f7a", "3b3f33", "f0ebe0")]
TITLES = ["A STILL MORNING", "SOFT LIGHT", "QUIET HOURS", "LOW TIDE", "SLOW ROOMS", "SALT AND CEDAR"]
def rgb(h): return tuple(bytes.fromhex(h))
def blend(a,b,f): return tuple(round(x*(1-f)+y*f) for x,y in zip(a,b))
def jpeg(image):
    out=io.BytesIO(); image.convert("RGB").save(out,format="JPEG",quality=95); return out.getvalue()
def sleeve(index):
    c1,c2,c3=map(rgb,COLORS[index]); n=480
    image=Image.new("RGB",(n,n)); draw=ImageDraw.Draw(image)
    for y in range(n): draw.line((0,y,n,y),fill=blend(c1,c2,y/(n-1)))
    layer=Image.new("RGBA",(n,n)); d=ImageDraw.Draw(layer)
    if index==0:
        d.ellipse((208,64,392,248),fill=c3+(255,))
        image=Image.alpha_composite(image.convert("RGBA"),layer); layer=Image.new("RGBA",(n,n));d=ImageDraw.Draw(layer)
        d.ellipse((-280,200,520,1000),fill=c2+(217,))
        image=Image.alpha_composite(image,layer);layer=Image.new("RGBA",(n,n));d=ImageDraw.Draw(layer)
        d.ellipse((140,300,900,1060),fill=(24,43,41,140))
    elif index==1:
        for i in range(1,9):
            r=i*28;d.ellipse((240-r,260-r,240+r,260+r),outline=c3+(int(255*(1-i*.1)),),width=3)
        d.ellipse((222,242,258,278),fill=c3+(255,))
    elif index==2:
        for i in range(7): d.rectangle((0,80+i*48,n,100+i*48),fill=c3+(int(255*(.15+i*.1)),))
    elif index==3:
        d.rectangle((0,300,n,304),fill=c3+(230,));d.ellipse((292,172,388,268),fill=c3+(255,))
        for i in range(5): d.rectangle((60+i*20,320+i*24,420-i*20,324+i*24),fill=c3+(int(255*(.5-i*.08)),))
    elif index==4:
        for i in range(3):
            r=300-i*80;d.arc((240-r,480-r,240+r,480+r),180,360,fill=c3+(int(255*(.9-i*.25)),),width=20)
    else:
        d.rectangle((92,108,284,300),fill=c3+(217,));d.rectangle((196,200,388,392),fill=c3+(115,))
    image=Image.alpha_composite(image.convert("RGBA"),layer).convert("RGB")
    font=ImageFont.truetype(str(Path(__file__).resolve().parents[1]/"ios/StillWater/Resources/Fonts/Geist-Medium.ttf"),20)
    d=ImageDraw.Draw(image); x=40
    for ch in TITLES[index]:
        d.text((x,432),ch,font=font,fill=(218,216,200));x+=d.textlength(ch,font=font)+3
    return jpeg(image)
def portrait():
    n=480; image=Image.new("RGB",(n,n)); pixels=image.load()
    for y in range(n):
        for x in range(n):
            p=blend(rgb("3d4a44"),rgb("141b18"),y/(n-1))
            glow=.55*max(0,1-math.hypot(x-333,y-120)/293)
            p=blend(p,rgb("ddd6b7"),glow)
            shadow=.55*(1-x/240) if x<240 else .35*(x-240)/240
            p=blend(p,(8,12,10),shadow)
            if 128<=x<136 and y>=60:p=blend(p,rgb("ddd6b7"),.10)
            if 136<=x<165 and y>=60:p=blend(p,(8,12,10),.25)
            pixels[x,y]=p
    return jpeg(image)

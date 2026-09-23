import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
STATES=["sleep","presence","presence-music","wake","still","touched","river","ask","three","paused","stopped","offline","pending","unknown","longtitle","noart","find","keyboard","detail","library","settings","display"]
INK=(0xF1,0xEB,0xDF)
def lum(c):
    def ch(v):
        v=v/255; return v/12.92 if v<=0.03928 else ((v+0.055)/1.055)**2.4
    r,g,b=c; return 0.2126*ch(r)+0.7152*ch(g)+0.0722*ch(b)
def contrast(a,b):
    la,lb=lum(a),lum(b); hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)
def blend(fg,bg,a): return tuple(round(fg[i]*a+bg[i]*(1-a)) for i in range(3))
JS='''() => {
  const scr=document.querySelector('#protoHost .scr'); const s=parseFloat(getComputedStyle(scr).getPropertyValue('--s'))||1;
  const r0=scr.getBoundingClientRect();
  const box=el=>{let r=el.getBoundingClientRect();let L=r.left,T=r.top,R=r.right,B=r.bottom;let a=el.parentElement;while(a&&a!==scr){if(getComputedStyle(a).overflow==='hidden'){const q=a.getBoundingClientRect();L=Math.max(L,q.left);T=Math.max(T,q.top);R=Math.min(R,q.right);B=Math.min(B,q.bottom);}a=a.parentElement;}return {x:(L-r0.left)/s,y:(T-r0.top)/s,w:Math.max(0,R-L)/s,h:Math.max(0,B-T)/s}};
  const taps=[...scr.querySelectorAll('.tap')].filter(e=>getComputedStyle(e).pointerEvents!=='none'&&e.offsetParent!==null).map(e=>{const r=e.getBoundingClientRect();return {cls:e.className,txt:e.textContent.trim().slice(0,18),...box(e),fw:r.width/s,fh:r.height/s}});
  const texts=[]; const walker=document.createTreeWalker(scr,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){const n=walker.currentNode; if(!n.textContent.trim())continue; const el=n.parentElement; const fs=parseFloat(getComputedStyle(el).fontSize); const b=box(el); if(b.h>0)texts.push({txt:n.textContent.trim().slice(0,30),fs,...b,op:parseFloat(getComputedStyle(el).opacity)});}
  const titles=[...scr.querySelectorAll('.serif')].filter(e=>parseFloat(getComputedStyle(e).fontSize)>=26&&e.textContent.trim()).map(e=>({txt:e.textContent.trim().slice(0,30),op:parseFloat(getComputedStyle(e).opacity),...box(e),clipped:e.scrollHeight>e.clientHeight+2&&!e.classList.contains('clamp2')}));
  return {taps,texts,titles};
}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':900})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        html=open('still-water.html').read()
        await pg.set_content('<!doctype html><html><head><meta charset="utf-8"></head><body>'+html+'</body></html>',wait_until='networkidle')
        await pg.wait_for_timeout(1200)
        await pg.add_style_tag(content="#protoHost{width:800px!important;height:480px!important;aspect-ratio:auto!important}.frame{width:max-content}")
        report=[]
        for st in STATES:
            await pg.click(f'#steps button[data-id="{st}"]'); await pg.wait_for_timeout(2400 if st in('ask','wake','presence','presence-music') else 700)
            path=f'pkg/reference/{STATES.index(st)+1:02d}-{st}.png'
            await pg.locator('#protoHost').screenshot(path=path)
            im=Image.open(path).convert('RGB').crop((0,0,800,480)); im.save(path)
            d=await pg.evaluate(JS)
            issues=[]
            # targets
            for t in d['taps']:
                big=t['fw']>=72 and t['fh']>=64; pill=t['fh']>=56 and t['fw']>=96
                if not(big or pill): issues.append(f"target {t['txt'] or t['cls']} {t['w']:.0f}x{t['h']:.0f}")
            # overlaps
            T=d['taps']
            for i in range(len(T)):
                for j in range(i+1,len(T)):
                    a,c=T[i],T[j]
                    if a['x']<c['x']+c['w'] and c['x']<a['x']+a['w'] and a['y']<c['y']+c['h'] and c['y']<a['y']+a['h']:
                        # ignore containment (row contains nothing tappable) 
                        issues.append(f"overlap {a['txt'] or a['cls'][:10]}/{c['txt'] or c['cls'][:10]}")
            for t in d['texts']:
                if t['fs']<15-0.01: issues.append(f"text {t['fs']:.0f}px '{t['txt']}'")
                if t['x']<0 or t['y']<0 or t['x']+t['w']>800.5 or t['y']+t['h']>480.5: issues.append(f"offcanvas '{t['txt']}'")
            # contrast: sample field 6px above each big serif
            for t in d['titles']:
                if t['clipped']: issues.append(f"clipped '{t['txt']}'")
                y=int(max(0,t['y']-8)); xs=range(int(t['x']),int(min(800,t['x']+t['w'])),8)
                px=[im.getpixel((x,y)) for x in xs if 0<=y<480]
                if not px: continue
                bg=tuple(sum(c[i] for c in px)//len(px) for i in range(3))
                eff=blend(INK,bg,min(1,t['op'])) ; cr=contrast(eff,bg)
                need=7 if t['op']>=0.99 else 4.5
                if cr<need: issues.append(f"contrast {cr:.1f}:1 (need {need}) '{t['txt']}'")
            report.append((st,issues))
        print('errors',errs)
        for st,iss in report: print(f"{st:15s} {'PASS' if not iss else 'FAIL'}  {'; '.join(iss)[:300]}")
        await b.close()
asyncio.run(main())

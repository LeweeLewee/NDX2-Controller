"""River Stone engineering study, not a production housing. Millimetres.
Requires cadquery 2.8 and optional workspace CAD dependency path.
Usage: python tools/river_stone_shell.py --deps PATH --supplier-step PATH
"""
from pathlib import Path
import argparse,sys,json,math
p=argparse.ArgumentParser();p.add_argument('--deps');p.add_argument('--supplier-step');p.add_argument('--revision',choices=['v1','v2'],default='v2');args=p.parse_args()
if args.deps:sys.path.insert(0,str(Path(args.deps).resolve()))
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]/('docs/hardware/river-stone/shell-'+args.revision)
OUT.mkdir(parents=True,exist_ok=True)
def log(t):print(t,flush=True)
def bounds(s):
    # OCC default spline bounds can be conservative; report tessellated bounds.
    vs,_=s.tessellate(.05,.1)
    lo=[min(getattr(v,k) for v in vs) for k in ('x','y','z')];hi=[max(getattr(v,k) for v in vs) for k in ('x','y','z')]
    return {'min':lo,'max':hi,'size':[b-a for a,b in zip(lo,hi)],'method':'tessellation, 0.05 mm tolerance'}
def pose(shape):return shape.rotate((0,0,0),(1,0,0),50).translate((0,-42,34))
def block(x0,x1,y0,y1,z0,z1):return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).val().translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def ellipse(rx,ry,z,h):return cq.Workplane('XY',origin=(0,0,z)).ellipse(rx,ry).extrude(h).val()
def rounded(w,h,r,z,depth,cy):
    return cq.Workplane('XY',origin=(0,cy,z)).rect(w,h).extrude(depth).edges('|Z').fillet(r).val()
def overlap(a,b):return abs(a.intersect(b).Volume())
# Loft rings deliberately move left/rear toward the crown for asymmetric shoulders.
profiles=[(0,104,74,0,0),(8,109,80,0,0),(22,110,82,0,0),(40,108,79,-1,1),(65,99,69,-3,3),(85,83,59,-5,6),(97,60,44,-6,9),(103,30,25,-6,10)]
wires=[cq.Workplane('XY',origin=(x,y,z)).ellipse(rx,ry).val() for z,rx,ry,x,y in profiles]
outer=cq.Solid.makeLoft(wires,False)
outer=cq.Workplane(obj=outer).faces('>Z').edges().fillet(6).val()
outer=outer.cut(pose(block(-250,250,-250,250,0,300)))
# Front-edge fillet deferred: the freeform transition produced non-watertight meshes.
assert outer.isValid();log('Outer loft and screen facet valid')
# Explicit cavity loft avoids an unstable freeform offset. Wall thickness varies;
# 4 mm radial profile inset is NOT a constant 4 mm normal wall thickness.
inner_profiles=[(-5,100,70,0,0)]+[(z,rx-4,ry-4,x,y) for z,rx,ry,x,y in profiles[1:-1]]+[(99,26,21,-6,10)]
inner=cq.Solid.makeLoft([cq.Workplane('XY',origin=(x,y,z)).ellipse(rx,ry).val() for z,rx,ry,x,y in inner_profiles],False)
inner=inner.cut(pose(block(-250,250,-250,250,-3,300)))
log('Cavity valid='+str(inner.isValid()))
assert inner.isValid() and len(inner.Solids())==1
shell=outer.cut(inner,tol=.001).clean()
log('Hollow shape valid='+str(shell.isValid())+' solids='+str(len(shell.Solids())))
assert shell.isValid() and len(shell.Solids())==1;log('Explicit cavity produces valid solid')
# 1.5 mm lens-border overlap; 1 mm lip, with 0.8 mm gasket allowance behind it.
window=pose(rounded(109.4,72.1,2.5,-35,40,37.55))
pocket=pose(block(-56.6,56.6,-.4,75.5,-36,-1))
log('Pre-cut type '+shell.ShapeType()+' volume '+str(shell.Volume()))
shell=shell.cut(window,tol=.001)
log('Window type '+shell.ShapeType()+' solids '+str(len(shell.Solids())))
shell=shell.cut(pocket,tol=.001)
log('Pocket type '+shell.ShapeType()+' solids '+str(len(shell.Solids())))
log('Opened shell valid='+str(shell.isValid())+' solids='+str(len(shell.Solids()))+' volume='+str(shell.Volume()))
# Underside ledge with 180 x112 opening; front screws outside display insertion path.
flange=ellipse(110,82,3.5,4).cut(ellipse(90,56,3.4,4.2)).intersect(outer)
log('Flange valid='+str(flange.isValid())+' volume='+str(flange.Volume()))
shell=shell.fuse(flange,tol=.001).clean()
fasteners=[(-45,-54),(45,-54),(-52,46),(52,46)]
for x,y in fasteners:
    boss=cq.Workplane('XY',origin=(x,y,7)).circle(6).extrude(5).val()
    hole=cq.Workplane('XY',origin=(x,y,0)).circle(1.7).extrude(13).val()
    nut=cq.Workplane('XY',origin=(x,y,9)).polygon(6,5.8/math.cos(math.pi/6)).extrude(3.2).val()
    shell=shell.fuse(boss).cut(hole).cut(nut)
assert shell.isValid();log('Shell, flange and cover-fastener bosses valid')
keepers={};coupons={}
if args.revision=='v2':
    for side in [-1,1]:
        # Local screen coordinates: t=0 is the front facet; rear is negative t.
        rail=block(52.8,56,14,61,-10.1,-3.1)
        plate=block(52.8,68,14,61,-12.5,-10)
        keeper=rail.fuse(plate)
        for v in [20,55]:
            boss=cq.Workplane('XY',origin=(63,v,-10)).circle(5).extrude(8).val()
            hole=cq.Workplane('XY',origin=(63,v,-12.6)).circle(1.7).extrude(10.4).val()
            nut=cq.Workplane('XY',origin=(63,v,-10.01)).polygon(6,5.8/math.cos(math.pi/6)).extrude(2.81).val()
            mount=boss.cut(hole).cut(nut)
            if side==-1:mount=mount.mirror('YZ')
            shell=shell.fuse(pose(mount))
            keeper=keeper.cut(hole)
            if side==1 and v==20:
                coupon=block(54,73,8,32,-2.5,0).fuse(boss).cut(hole).cut(nut)
                coupons['retainer-mount-coupon']=coupon
        if side==-1:keeper=keeper.mirror('YZ')
        keepers['retainer-'+('left' if side==-1 else 'right')]=pose(keeper)
        if side==1:
            coupons['retainer-strip-coupon']=keeper.intersect(block(50,70,14,30,-15,0)).translate((-60,-22,12.5))
    coupons['retainer-mount-coupon']=coupons['retainer-mount-coupon'].rotate((0,0,0),(1,0,0),180).translate((-63,20,0))
    assert shell.isValid() and len(shell.Solids())==1
rx,ry=101,71
def make_cover(rx,ry):
    return ellipse(rx,ry,.2,3).cut(pose(block(-250,250,-250,250,-3.6,300)))
for attempt in range(25):
    cover=make_cover(rx,ry)
    if overlap(cover,shell)<.01:break
    rx-=.25;ry-=.25
else:raise RuntimeError('No clear cover envelope found')
rx-=.3;ry-=.3;cover=make_cover(rx,ry)
for x,y in fasteners:cover=cover.cut(cq.Workplane('XY',origin=(x,y,0)).circle(1.7).extrude(4).val())
assert cover.isValid() and overlap(cover,shell)<.01
# Conservative supplier envelope, including +0.3 depth tolerance, seated at t=-1.8.
module=pose(rounded(112.6,75.3,3.9,-19.5,17.7,37.55))
checks={'module_shell_overlap_mm3':overlap(module,shell),'cover_shell_overlap_mm3':overlap(cover,shell)}
log('Seated module overlap '+str(checks['module_shell_overlap_mm3']))
bays={'battery':block(-41,39,-10,54,8,34),'charger':block(41,91,-18,37,8,30),'converter':block(-93,-43,-5,23,8,22)}
for name,bay in bays.items():
    checks[name+'_shell_overlap_mm3']=overlap(bay,shell)
    checks[name+'_module_overlap_mm3']=overlap(bay,module)
for i,(name,bay) in enumerate(bays.items()):
    for other,other_bay in list(bays.items())[i+1:]:checks[name+'_'+other+'_overlap_mm3']=overlap(bay,other_bay)
log('Bay checks '+str(checks))
# Empty housing, cover removed: vertical insertion at final tilt.
insertion=[]
for dz in range(-120,1,5):
    insertion.append({'z_translation_mm':dz,'shell_overlap_mm3':overlap(module.translate((0,0,dz)),shell)})
log('Insertion max overlap '+str(max(v['shell_overlap_mm3'] for v in insertion)))
assert max(checks.values())<.01,checks
assert max(v['shell_overlap_mm3'] for v in insertion)<.01,insertion
# Continuous conservative sweep: convex hull of the tilted rectangular module's
# YZ corners at both ends of the 120 mm vertical path, extruded across full width.
# The rectangular envelope includes (and overestimates) the rounded lens corners.
a=math.radians(50);s,c=math.sin(a),math.cos(a)
points=sorted(set((round(-42+v*c-t*s,9),round(34+v*s+t*c+dz,9)) for v in (-.1,75.2) for t in (-19.5,-1.8) for dz in (-120,0)))
def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
def chain(points):
    h=[]
    for p in points:
        while len(h)>1 and cross(h[-2],h[-1],p)<=0:h.pop()
        h.append(p)
    return h
hull=chain(points)[:-1]+chain(list(reversed(points)))[:-1]
sweep=cq.Workplane('YZ').polyline(hull).close().extrude(112.6).val().translate((-56.3,0,0))
# Relieve the hidden internal edges along the full insertion corridor, adding
# 0.4 mm radial/side clearance. This does not cut the visible front lip.
relief=cq.Workplane('YZ').polyline(hull).close().wires().toPending().offset2D(.4).extrude(113.4).val().translate((-56.7,0,0))
relief_removed=overlap(relief,shell)
shell=shell.cut(relief).clean()
assert shell.isValid() and len(shell.Solids())==1
checks['continuous_insertion_sweep_shell_overlap_mm3']=overlap(sweep,shell)
assert checks['continuous_insertion_sweep_shell_overlap_mm3']<.01,checks
log('Continuous insertion sweep clear')
if args.revision=='v2':
    glass_keepout=pose(rounded(112.6,75.3,3.9,-2.5,.7,37.55))
    pcb_proxy=pose(block(-52.5,52.5,-.1,75.2,-19.5,-2.5))
    for name,k in keepers.items():
        checks[name+'_shell_overlap_mm3']=overlap(k,shell)
        checks[name+'_glass_overlap_mm3']=overlap(k,glass_keepout)
        checks[name+'_pcb_proxy_overlap_mm3']=overlap(k,pcb_proxy)
        for b,bay in bays.items():checks[name+'_'+b+'_overlap_mm3']=overlap(k,bay)
    assert max(checks.values())<.01,checks
    log('Retainers clear shell, glass, PCB proxy and component boxes')
supplier=None;supplier_info=None
if args.supplier_step:
    supplier=cq.importers.importStep(args.supplier_step).val()
    supplier_info={'source':Path(args.supplier_step).name,'bounds_raw_mm':bounds(supplier),'solid_count':len(supplier.Solids()),'orientation':'Assumed +Z glass-front; raw Y minimum maps to lower lens edge. Must verify with rendered imported model.'}
    supplier=supplier.translate((0,39.49,-6.6));supplier=pose(supplier)
    log('Supplier imported')
for name,shape in [('shell-study',shell),('cover-study',cover),('module-envelope',module),*keepers.items(),*coupons.items()]:
    assert shape.isValid() and len(shape.Solids())==1 and shape.Volume()>0,(name,len(shape.Solids()))
    cq.exporters.export(shape,str(OUT/(name+'.step')))
    cq.exporters.export(shape,str(OUT/(name+'.stl')),tolerance=.15,angularTolerance=.15)
assembly=cq.Assembly(name='RiverStoneStudy')
assembly.add(shell,name='shell',color=cq.Color(.72,.69,.61));assembly.add(cover,name='cover',color=cq.Color(.5,.48,.43))
assembly.add(supplier if supplier else module,name='display_reference',color=cq.Color(.12,.16,.18))
for name,bay in bays.items():assembly.add(bay,name=name+'_reservation',color=cq.Color(.45,.65,.48))
cq.exporters.export(cq.Compound.makeCompound([shell,cover,module,*bays.values(),*keepers.values()]),str(OUT/'assembly-envelopes.step'))
# Save tessellations for a deterministic preview, avoiding extra CAD viewer dependencies.
def mesh(shape):
    vs,fs=shape.tessellate(.2,.2);return {'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs}
preview={'shell':mesh(shell),'section':mesh(shell.intersect(block(0,250,-250,250,-1,200))),'cover':mesh(cover),'module':mesh(module),'glass':mesh(pose(rounded(112.4,75.1,4,-1.8,.05,37.55))),'va':mesh(pose(block(-47.77,47.77,12.31,66.67,-1.74,-1.69))),**{n:mesh(v) for n,v in bays.items()}}
if supplier:preview['supplier']=mesh(supplier)
preview.update({n:mesh(k) for n,k in keepers.items()})
(OUT/'preview-meshes.json').write_text(json.dumps(preview))
report={'status':'engineering study; not released for printing or powered assembly','cadquery_version':cq.__version__,'wall_construction':{'radial_profile_inset_mm':4,'facet_inset_mm':3,'lip_mm':1,'constant_normal_wall_thickness':False},'profiles_z_rx_ry_cx_cy_mm':profiles,'shell':bounds(shell),'cover':bounds(cover),'cover_ellipse_radii_mm':[rx,ry],'screen_angle_deg':50,'lens_front_recess_mm':1.8,'fastener_centres_xy_mm':fasteners,'solid_validity':{'shell':shell.isValid(),'cover':cover.isValid(),'shell_solids':len(shell.Solids()),'cover_solids':len(cover.Solids())},'checks':checks,'discrete_insertion_5mm':insertion,'continuous_insertion':{'travel_mm':120,'method':'Convex hull of rectangular module envelope endpoints, extruded across 112.6 mm width','relief_clearance_mm':.4,'relief_removed_mm3':relief_removed,'housing_state':'empty, cover removed; display inserted before power parts'},'supplier':supplier_info,'limitations':['Retainer contact and glass loads require physical validation; electrical ports and acoustic opening unresolved','Battery and board reservations are not selected parts','Print supports, dimensional tolerance, glass loads and thermal/RF behaviour untested','Freeform wall uses separate cavity loft; minimum normal thickness is not certified']}
report['revision']=args.revision
report['retention']={'included':bool(keepers),'glass_back_t_mm':-2.5,'pad_face_t_mm':-3.1,'hard_stop_pad_gap_mm':.6,'proposed_uncompressed_pad_mm':.8,'pcb_proxy_width_mm':105,'actual_supplier_retainer_collision_checked':False,'fasteners':'Provisional M3-size holes/nut pockets; actual hardware and glass loads not validated'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
log('Exported study and validation')

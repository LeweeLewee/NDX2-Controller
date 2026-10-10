import json, cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
sh=cq.Shape.importBrep("phone.brep")
res={}
for i in range(-12,13):
    z=i*0.1
    s=BRepAlgoAPI_Section(sh.wrapped,gp_Pln(gp_Pnt(0,0,z),gp_Dir(0,0,1))); s.Build()
    pts=[]
    for e in cq.Shape.cast(s.Shape()).Edges():
        n=max(4,int(e.Length()/0.1)); pts+=[(v.x,v.y) for v in e.positions([k/n for k in range(n+1)])]
    res[round(z,2)]=pts
json.dump(res,open("outline_pts.json","w"))
import numpy as np
for z,p in res.items():
    a=np.array(p); m=(a[:,1]<-20)&(a[:,1]>-130)
    print(z, round(a[m,0].min(),4), round(a[m,0].max(),4), round(a[:,1].min(),4), round(a[:,1].max(),4))

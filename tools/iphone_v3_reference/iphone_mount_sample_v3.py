"""iPhone 11 snug-fit sample v3. CadQuery 2.8 + trimesh, millimetres.
Snug perimeter location on the real phone outline; generous non-precision reliefs at
buttons, Lightning/grille end and top acoustic zone; rear fully open (camera untouched).
Print allowances are proposals; nothing here is physically validated."""
import json, math, sys
from pathlib import Path
import numpy as np, trimesh, cadquery as cq
from scipy.spatial import ConvexHull

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
P = {
    "fit_clearance_per_side": 0.20,          # proposed snug slip fit (unvalidated)
    "fit_clearance_variants": [0.15, 0.20, 0.25],
    "wall_thickness": 2.4,                   # six 0.4 mm perimeters
    "lip_thickness": 1.2,
    "aperture": [138.9, 63.7], "aperture_corner_r": 3.0, "overlap": 6.0,
    "spacer_options": [0.4, 0.8],
    "wall_top_z": 8.0,                       # captures phone widest line at either spacer
    "lead_in_height": 0.8, "lead_in_extra": 0.5,
    "button_relief_margin_each_end": 3.0,
    "lightning_end_opening": 52.8,           # grilles 14.5-61.2 mm across + 3 mm each side
    "top_end_opening": 36.0,
    "camera_keepout_margin": 3.0, "camera_keepout_depth_behind_back": 5.0,
}
# Measured datum (phone coords): widest band at z=-0.2, body centre, front glass plane
CX, CY, ZF = 37.860, -75.456, 4.16
def to_s(x, y): return (y - CY, x - CX)          # sample X = length (top end +X), Y = width
L_ = P["button_relief_margin_each_end"]
RELIEF = {  # sample-X ranges from measured button spans (phone y) plus margin
    "ring_volume": (-54.66 - CY - L_, -20.58 - CY + L_, "-Y"),
    "side_button": (-51.20 - CY - L_, -34.10 - CY + L_, "+Y"),
}
def in_relief(X, Y):
    a, b, _ = RELIEF["ring_volume"]
    if Y < -30 and a <= X <= b: return True
    a, b, _ = RELIEF["side_button"]
    if Y > 30 and a <= X <= b: return True
    if X < -60 and abs(Y) <= P["lightning_end_opening"] / 2: return True
    return False
raw = json.load(open("outline_pts.json"))
pts = [to_s(x, y) for z, pp in raw.items() if abs(float(z)) <= 0.6 for x, y in pp]
kept = np.array([p for p in pts if not in_relief(*p)])
hull = kept[ConvexHull(kept).vertices]
poly = [tuple(hull[0])]
for p in hull[1:]:
    if math.dist(p, poly[-1]) >= 0.25: poly.append(tuple(p))
body_wire = cq.Wire.makePolygon([cq.Vector(x, y, 0) for x, y in poly], close=True)

def prism(off, z0, h):
    w = body_wire.offset2D(off, "arc")[0]
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), cq.Vector(0, 0, h)).translate(cq.Vector(0, 0, z0))
def rrect(w, h, r, z0, d):
    return cq.Workplane("XY", origin=(0, 0, z0)).rect(w, h).extrude(d).edges("|Z").fillet(r).val()

def build(c):
    t, wall, top = P["lip_thickness"], P["wall_thickness"], P["wall_top_z"]
    fr = prism(c + wall, 0, top).cut(prism(c, t, top))                       # flange + wall
    fr = fr.cut(prism(c + P["lead_in_extra"], top - P["lead_in_height"], 1))  # stepped lead-in
    fr = fr.cut(rrect(*P["aperture"], P["aperture_corner_r"], -1, t + 2))   # accepted aperture
    B = 30
    for a, b, side in RELIEF.values():
        y0 = -B - 30 if side == "-Y" else 30
        fr = fr.cut(cq.Solid.makeBox(b - a, B, top, cq.Vector(a, y0, t)))
    lo = P["lightning_end_opening"]; to = P["top_end_opening"]
    fr = fr.cut(cq.Solid.makeBox(B, lo, top, cq.Vector(-60 - B, -lo / 2, t)))
    fr = fr.cut(cq.Solid.makeBox(B, to, top, cq.Vector(60, -to / 2, t)))
    return fr.clean()

phone = trimesh.load("phone_mesh.stl")          # 0.01 mm tessellation of the STEP
def place(spacer):
    zf = P["lip_thickness"] + spacer
    M = np.array([[0, 1, 0, -CY], [1, 0, 0, -CX], [0, 0, -1, zf + ZF], [0, 0, 0, 1]], float)
    m = phone.copy(); m.apply_transform(M); return m
V0 = phone.vertices
region = {  # phone-coordinate vertex selections
    "buttons": ((V0[:, 0] < -0.1) | (V0[:, 0] > 75.82)) & (V0[:, 1] > -60) & (V0[:, 1] < -15),
    "camera_bump": V0[:, 2] < -4.17,
    "lightning_opening_and_grilles": (V0[:, 1] < -148.0) & (np.abs(V0[:, 0] - CX) < 24) & (np.abs(V0[:, 2]) < 2.0),
    "side_band_snug": (np.abs(V0[:, 2] + 0.2) < 0.3) & ((V0[:, 1] > -130) & (V0[:, 1] < -60)),
    "corners_snug": (np.abs(V0[:, 2] + 0.2) < 0.3) & ((np.abs(V0[:, 0] - CX) > 30) & (np.abs(V0[:, 1] - CY) > 68)),
    "front_glass": V0[:, 2] > 4.15,
}
rep = {"status": "unprinted snug-fit sample v3; CAD/mesh checks only; not retention, acoustic or production validation",
       "phone_reference": {"file": "iPhone 11.STEP", "url": "https://grabcad.com/library/iphone-11-6",
                           "sha256": "ab204f6316407f9c7d9d6a7ec7a97fdd5a2abde12e56e619c3cbceff6474a561",
                           "widest_body_section_mm": [150.91, 75.72], "at_phone_z_mm": -0.2},
       "parameters": P, "relief_sample_x_ranges_mm": {k: [round(v[0], 2), round(v[1], 2), v[2]] for k, v in RELIEF.items()},
       "check_method": "Phone STEP tessellated at 0.01 mm; frame tessellated at 0.01 mm; containment and closest-point queries",
       "variants": {}}
for c in P["fit_clearance_variants"]:
    fr = build(c); assert fr.isValid() and len(fr.Solids()) == 1
    tag = f"{c:.2f}".replace(".", "p")
    cq.exporters.export(fr, str(OUT / f"snug-frame-{tag}.step"))
    cq.exporters.export(fr, str(OUT / f"snug-frame-{tag}.stl"), tolerance=0.01, angularTolerance=0.05)
    fm = trimesh.load(OUT / f"snug-frame-{tag}.stl")
    b = fr.BoundingBox()
    v = {"valid_solid": True, "bounds_mm": [round(b.xlen, 2), round(b.ylen, 2), round(b.zlen, 2)],
         "stl_watertight": bool(fm.is_watertight), "stl_bodies": len(fm.split(only_watertight=False)),
         "aperture_intersection_mm3": round(abs(fr.intersect(rrect(*P["aperture"], P["aperture_corner_r"], -0.5, 2)).Volume()), 6)}
    for s in P["spacer_options"]:
        pm = place(s)
        def chunks(f, X, n=4000):
            return np.concatenate([f(X[i:i + n]) for i in range(0, len(X), n)])
        inside_frame = int(chunks(fm.contains, pm.vertices).sum())
        inside_phone = int(chunks(pm.contains, fm.vertices).sum())
        d = chunks(lambda X: trimesh.proximity.closest_point(fm, X)[1], pm.vertices)
        comp = {"phone_vertices_inside_frame": inside_frame, "frame_vertices_inside_phone": inside_phone,
                "min_clearance_overall": round(float(d.min()), 3)}
        for g, mask in region.items():
            comp[f"min_clearance_{g}"] = round(float(d[mask].min()), 3)
        i = int(np.argmin(d)); comp["closest_point_phone_coords"] = [round(float(x), 2) for x in V0[i]]
        v[f"spacer_{s}"] = comp
        assert inside_frame == 0 and inside_phone == 0
    rep["variants"][tag] = v
rep["camera_keepout_for_enclosure"] = {
    "modelled_plateau_mm": [25.06, 28.26], "modelled_protrusion_mm": 0.70,
    "keepout_footprint_mm": [25.06 + 6, 28.26 + 6], "keepout_depth_behind_back_glass_mm": 5.0,
    "note": "No contact anywhere in this volume; lens rings not modelled, so depth is deliberately generous"}
(OUT / "validation.json").write_text(json.dumps(rep, indent=2) + "\n")
print(json.dumps(rep, indent=2))

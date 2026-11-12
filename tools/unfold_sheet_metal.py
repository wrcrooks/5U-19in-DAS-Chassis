"""Unfold the sheet-metal parts in CAD/Revised into flat patterns with bend lines.

    freecadcmd tools/rebuild_parts.py          # CAD/*.step (Onshape export) -> CAD/Revised/*.step
    freecadcmd tools/unfold_sheet_metal.py     # CAD/Revised/*.step -> CAD/Flat-Patterns/

Writes  CAD/Flat-Patterns/<part>.dxf       cut profile (continuous) + bend centrelines (DASHED), mm, 1:1
        CAD/Flat-Patterns/bend-data.json   per-part bend table and design-rule measurements
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheetmetal import *

OUT = os.path.join(CAD, "Flat-Patterns")
PARTS = ["Chassis", "Bezel", "Back Panel", "Chassis Rear Support Bracket", "Drive Support Panel",
         "Bezel Mounting Bracket", "Drive Bay Cover", "Rear Electronics Cover", "Attic Baffle"]


def main():
    os.makedirs(OUT, exist_ok=True)
    data = dict(material={k: (round(v, 4) if isinstance(v, float) else v) for k, v in MATERIAL.items()},
                units="mm", parts={})
    for name in PARTS:
        s = load(os.path.join(REVISED, "%s.step" % name))
        U, flat, bends = flatten(s, MATERIAL["k_factor"])
        write_dxf(os.path.join(OUT, name + ".dxf"), flat, bends)
        bb, t = flat.BoundBox, U.thickness
        clear = measure(flat, bends)
        groups = {}
        for b in bends:
            g = groups.setdefault(b["id"], dict(id=b["id"], angle_deg=b["angle"],
                                                direction="up" if b["up"] else "down",
                                                inside_radius=round(b["r_in"], 3),
                                                bend_allowance=round(b["ba"], 3), segments=[]))
            g["segments"].append([[round(p.x, 3), round(p.y, 3)] for p in b["line"]])
        for g in groups.values():
            g["total_length"] = round(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in g["segments"]), 3)
            h = clear[g["id"]]["hole"]
            g["nearest_cutout"] = None if h is None else round(h, 3)
        data["parts"][name] = dict(
            thickness=round(t, 3), flat_size=[round(bb.XLength, 3), round(bb.YLength, 3)],
            flat_area=round(flat.Area, 1), cutouts=len(flat.Wires) - 1,
            min_web=None if len(flat.Wires) < 2 else round(min_web(flat), 3),
            volume_check=round(flat.Area * t / s.Volume, 5),
            formed_size=[round(x, 3) for x in (s.BoundBox.XLength, s.BoundBox.YLength, s.BoundBox.ZLength)],
            bends=sorted(groups.values(), key=lambda g: g["id"]))
        print("%-30s t=%.3f flat %.2f x %.2f  bends=%d (hits=%d) cutouts=%d  area*t/vol=%.5f" % (
            name, t, bb.XLength, bb.YLength, len(bends), len(groups), len(flat.Wires) - 1,
            flat.Area * t / s.Volume))
    with open(os.path.join(OUT, "bend-data.json"), "w") as fh:
        json.dump(data, fh, indent=1)
    write_tables(data)


START, END = "<!-- bend-tables:start -->", "<!-- bend-tables:end -->"


def write_tables(data):
    """Refresh the generated section of Bend-Data.md."""
    out = []
    for name, p in data["parts"].items():
        fx, fy = p["flat_size"]
        out.append("### %s: flat %.2f x %.2f mm (%.2f x %.2f in), formed %s\n" % (
            name, fx, fy, fx / IN, fy / IN, " x ".join("%g" % round(v, 2) for v in p["formed_size"])))
        if not p["bends"]:
            out.append("No bends; laser cut only.\n")
            continue
        out.append("| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |")
        out.append("|---|---|---|---|---|---|")
        for b in p["bends"]:
            segs = "; ".join("(%g, %g) to (%g, %g)" % (a[0], a[1], c[0], c[1]) for a, c in b["segments"])
            near = "none" if b["nearest_cutout"] is None else "%.2f" % b["nearest_cutout"]
            out.append("| %d | %g° | %s | %s | %g | %s |" % (
                b["id"], b["angle_deg"], b["direction"], segs, b["total_length"], near))
        out.append("")
    path = os.path.join(OUT, "Bend-Data.md")
    text = open(path).read()
    if START in text and END in text:
        text = text[:text.index(START) + len(START)] + "\n\n" + "\n".join(out) + "\n" + text[text.index(END):]
        open(path, "w").write(text)


main()

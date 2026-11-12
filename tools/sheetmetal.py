"""Shared sheet-metal helpers for FreeCAD scripts: bend detection, unfolding, thickening, DXF.

Bend parameters are SendCutSend's published values for 5052-H32 aluminium, 0.080 in
(https://sendcutsend.com/bending-calculator/). Change MATERIAL if the stock changes.
"""
import math, os
import FreeCAD as App
import Part

V = App.Vector
CAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "CAD")
REVISED = os.path.join(CAD, "Revised")

IN = 25.4
MATERIAL = dict(
    name="5052-H32 aluminium, 0.080 in (2.03 mm)",
    thickness=0.080 * IN,
    k_factor=0.48,
    bend_radius=0.038 * IN,       # effective inside radius
    die_width=0.472 * IN,         # cut features should stay >= die_width/2 from a bend line
    min_flange=0.313 * IN,        # minimum formed flange, outside dimension
    max_flat=(30 * IN, 44 * IN),
    max_bend_length=44 * IN,
)
TOL = 1e-4


def load(path):
    s = Part.Shape()
    s.read(path)
    assert len(s.Solids) == 1, "%s: expected one solid" % path
    return s.Solids[0]


def save(solids, path):
    """Write named solids ({name: shape}) to one STEP file, keeping the names as product names."""
    import Import
    doc = App.newDocument("export")
    objs = []
    for name, shape in solids:
        o = doc.addObject("Part::Feature", "Body")
        o.Label, o.Shape = name, shape
        objs.append(o)
    doc.recompute()
    Import.export(objs, path)
    App.closeDocument(doc.Name)


def surf(f):
    return type(f.Surface).__name__


def normal(f):
    return f.normalAt(*f.Surface.parameter(f.CenterOfMass))


def is_line(e):
    return type(e.Curve).__name__ in ("Line", "LineSegment")


def edge_dir(e):
    p = e.Vertexes
    d = p[1].Point - p[0].Point
    return d.normalize()


def radial(p, c, a):
    r = p - c
    return r - a * r.dot(a)


class Unfolder:
    def __init__(self, shape, k, log):
        self.s, self.k, self.log = shape, k, log
        self.faces = shape.Faces
        self.adj = {}
        for i, f in enumerate(self.faces):
            for e in f.Edges:
                self.adj.setdefault(e.hashCode(), []).append((i, e))
        self.thickness = self._thickness()

    def _thickness(self):
        big = max((f for f in self.faces if surf(f) == "Plane"), key=lambda f: f.Area)
        n, p = normal(big), big.CenterOfMass
        best = None
        for f in self.faces:
            if surf(f) == "Plane" and normal(f).dot(n) < -0.999:
                d = abs((f.CenterOfMass - p).dot(n))
                if d > TOL and f.Area > 0.5 * big.Area and (best is None or d < best):
                    best = d
        return best

    def neighbour(self, i, e):
        for j, e2 in self.adj[e.hashCode()]:
            if j != i and e2.isSame(e):
                return j
        return None

    def bends_from(self, i):
        """Yield (cyl index, L1 edge, next plane index, L2 edge) for bends leaving plane i."""
        f = self.faces[i]
        for e in f.Edges:
            if not is_line(e):
                continue
            j = self.neighbour(i, e)
            if j is None or surf(self.faces[j]) != "Cylinder":
                continue
            c = self.faces[j]
            a = c.Surface.Axis
            if abs(abs(edge_dir(e).dot(a)) - 1) > 1e-6:
                continue
            r = radial(e.CenterOfMass, c.Surface.Center, a)
            if abs(abs(normal(f).dot(r.normalize())) - 1) > 1e-6:
                continue  # not tangent: a cut edge, not a bend
            for e2 in c.Edges:
                if e2.isSame(e) or not is_line(e2):
                    continue
                q = self.neighbour(j, e2)
                if q is not None and q != i and surf(self.faces[q]) == "Plane":
                    yield j, e, q, e2

    def unfold(self, start):
        t = self.thickness
        T = {start: App.Matrix()}
        queue, zones, bends, seen_cyl = [start], [], [], set()
        while queue:
            i = queue.pop(0)
            P = self.faces[i]
            for j, e1, q, e2 in self.bends_from(i):
                if j in seen_cyl:
                    continue
                seen_cyl.add(j)
                C = self.faces[j]
                c, a, R = C.Surface.Center, C.Surface.Axis, C.Surface.Radius
                p1 = e1.CenterOfMass
                r1 = radial(p1, c, a)
                r2 = radial(e2.CenterOfMass, c, a)
                phi = math.atan2(r2.cross(r1).dot(a), r2.dot(r1))
                inside = normal(P).dot(r1) < 0          # this skin is the inside of the bend
                r_in = R if inside else R - t
                ba = abs(phi) * (r_in + self.k * t)
                tau = a.cross(r1).normalize() * (-1 if phi > 0 else 1)
                M = App.Placement(tau * ba, App.Rotation()).toMatrix().multiply(
                    App.Placement(V(0, 0, 0), App.Rotation(a, math.degrees(phi)), c).toMatrix())
                pa, pb = [v.Point for v in e1.Vertexes]
                Tp = T[i]
                zone = [Tp.multVec(x) for x in (pa, pb, pb + tau * ba, pa + tau * ba)]
                zones.append(zone)
                bends.append(dict(
                    geom=dict(R=R, r1=r1, r2=r2, pa=pa, pb=pb),
                    line=[Tp.multVec(pa + tau * ba / 2), Tp.multVec(pb + tau * ba / 2)],
                    angle=round(math.degrees(abs(phi)), 3), up=inside, r_in=r_in, ba=ba,
                    length=e1.Length, walls=(i, q)))
                if q not in T:
                    T[q] = Tp.multiply(M)
                    queue.append(q)
        return T, zones, bends


def to_2d(n):
    """Matrix taking a plane with outward normal n to the XY plane, viewed from outside."""
    u = next(ax for ax in (V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)) if abs(ax.dot(n)) < 1e-6)
    v = n.cross(u)
    return App.Matrix(u.x, u.y, u.z, 0, v.x, v.y, v.z, 0, n.x, n.y, n.z, 0, 0, 0, 0, 1)


def flatten(shape, k, log=print):
    U = Unfolder(shape, k, log)
    planes = sorted((i for i, f in enumerate(U.faces) if surf(f) == "Plane"),
                    key=lambda i: -U.faces[i].Area)
    best = None
    for start in planes[:2]:                       # the two skins of the largest wall
        T, zones, bends = U.unfold(start)
        ups = sum(b["length"] for b in bends if b["up"])
        downs = sum(b["length"] for b in bends if not b["up"])
        if best is None or ups - downs > best[0]:
            best = (ups - downs, start, T, zones, bends)
    _, start, T, zones, bends = best
    G = to_2d(normal(U.faces[start]))
    pieces = []
    for i, M in T.items():
        f = U.faces[i].copy()
        f.transformShape(G.multiply(M))
        pieces.append(f)
    z0 = pieces[0].CenterOfMass.z
    for zpts in zones:
        pts = [G.multVec(p) for p in zpts]
        pieces.append(Part.Face(Part.makePolygon(pts + [pts[0]])))
    flat = pieces[0] if len(pieces) == 1 else outline(pieces[0].multiFuse(pieces[1:], 1e-5))
    for b in bends:
        b["line"] = [G.multVec(p) for p in b["line"]]
    bb = flat.BoundBox
    shift = V(-bb.XMin, -bb.YMin, -z0)
    flat.translate(shift)
    for b in bends:
        b["line"] = [p + shift for p in b["line"]]
    assert len(flat.Faces) == 1, "flat pattern is not a single face (%d)" % len(flat.Faces)
    return U, flat, merge_collinear(bends)


def outline(shell):
    """Single face bounded by the edges that belong to only one face of the fused shell."""
    count = {}
    for f in shell.Faces:
        for e in f.Edges:
            count.setdefault(e.hashCode(), []).append(e)
    free = []
    for group in count.values():
        for e in group:
            if sum(1 for o in group if o.isSame(e)) == 1:
                free.append(e)
    wires = [Part.Wire(g) for g in Part.sortEdges(free)]
    assert all(w.isClosed() for w in wires), "open contour in flat pattern"
    face = Part.makeFace(wires, "Part::FaceMakerBullseye")
    assert abs(face.Area - shell.Area) < 1e-3 * shell.Area, "outline area mismatch"
    try:
        clean = face.removeSplitter()
        if len(clean.Faces) == 1 and abs(clean.Area - face.Area) < 1e-6 * face.Area:
            face = clean.Faces[0]
    except Exception:
        pass
    return face


def merge_collinear(bends):
    """Order bends and give collinear segments (one press-brake hit) a shared id."""
    def key(b):
        p, q = b["line"]
        d = (q - p).normalize()
        if d.x < -1e-9 or (abs(d.x) < 1e-9 and d.y < 0):
            d = d * -1
            b["line"] = [q, p]
        off = round(p.x * d.y - p.y * d.x, 3)
        return (round(d.x, 4), round(d.y, 4), off, round(min(p.x * d.x + p.y * d.y, q.x * d.x + q.y * d.y), 3))
    bends.sort(key=key)
    ids, n = {}, 0
    for b in bends:
        k = key(b)[:3] + (b["up"], b["angle"])
        if k not in ids:
            n += 1
            ids[k] = n
        b["id"] = ids[k]
    return bends


# ---------------------------------------------------------------- DXF (R12 ASCII)
def dxf_entities(flat, bends):
    out = []
    def ent(kind, ltype, *pairs):
        out.extend(["0", kind, "8", "0", "6", ltype])
        for code, val in pairs:
            out.extend([str(code), "%.6f" % val])
    for w in flat.Wires:
        for e in w.Edges:
            kind = type(e.Curve).__name__
            if is_line(e):
                a, b = [v.Point for v in e.Vertexes]
                ent("LINE", "CONTINUOUS", (10, a.x), (20, a.y), (30, 0), (11, b.x), (21, b.y), (31, 0))
            elif kind == "Circle":
                c, r = e.Curve.Center, e.Curve.Radius
                if len(e.Vertexes) == 1 or e.Vertexes[0].Point.distanceToPoint(e.Vertexes[-1].Point) < 1e-7:
                    ent("CIRCLE", "CONTINUOUS", (10, c.x), (20, c.y), (30, 0), (40, r))
                    continue
                ps, pe = e.valueAt(e.FirstParameter), e.valueAt(e.LastParameter)
                pm = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
                ang = lambda p: math.degrees(math.atan2(p.y - c.y, p.x - c.x)) % 360
                s, m, en = ang(ps), ang(pm), ang(pe)
                if (m - s) % 360 > (en - s) % 360:     # midpoint not on the CCW sweep: reverse
                    s, en = en, s
                ent("ARC", "CONTINUOUS", (10, c.x), (20, c.y), (30, 0), (40, r), (50, s), (51, en))
            else:
                pts = e.discretize(Deflection=0.005)
                for a, b in zip(pts, pts[1:]):
                    ent("LINE", "CONTINUOUS", (10, a.x), (20, a.y), (30, 0), (11, b.x), (21, b.y), (31, 0))
    for b in bends:
        p, q = b["line"]
        ent("LINE", "DASHED", (10, p.x), (20, p.y), (30, 0), (11, q.x), (21, q.y), (31, 0))
    return out


def write_dxf(path, flat, bends):
    bb = flat.BoundBox
    head = ["0", "SECTION", "2", "HEADER",
            "9", "$ACADVER", "1", "AC1009",
            "9", "$INSUNITS", "70", "4",
            "9", "$MEASUREMENT", "70", "1",
            "9", "$LTSCALE", "40", "1.0",
            "9", "$EXTMIN", "10", "0.0", "20", "0.0", "30", "0.0",
            "9", "$EXTMAX", "10", "%.6f" % bb.XMax, "20", "%.6f" % bb.YMax, "30", "0.0",
            "0", "ENDSEC",
            "0", "SECTION", "2", "TABLES",
            "0", "TABLE", "2", "LTYPE", "70", "2",
            "0", "LTYPE", "2", "CONTINUOUS", "70", "0", "3", "Solid line", "72", "65", "73", "0", "40", "0.0",
            "0", "LTYPE", "2", "DASHED", "70", "0", "3", "Dashed __ __ __", "72", "65", "73", "2",
            "40", "6.0", "49", "4.0", "49", "-2.0",
            "0", "ENDTAB",
            "0", "TABLE", "2", "LAYER", "70", "1",
            "0", "LAYER", "2", "0", "70", "0", "62", "7", "6", "CONTINUOUS",
            "0", "ENDTAB", "0", "ENDSEC",
            "0", "SECTION", "2", "ENTITIES"]
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(head + dxf_entities(flat, bends) + ["0", "ENDSEC", "0", "EOF"]) + "\n")


# ---------------------------------------------------------------- design-rule measurements
def split_wires(flat):
    wires = sorted(flat.Wires, key=lambda w: -w.BoundBox.DiagonalLength)
    return wires[0], wires[1:]


def measure(flat, bends):
    """Per bend id: clearance from the bend line to the nearest internal cut-out."""
    _, holes = split_wires(flat)
    res = {}
    for b in bends:
        seg = Part.makeLine(*b["line"])
        hole = min((seg.distToShape(h)[0] for h in holes), default=None)
        r = res.setdefault(b["id"], dict(hole=None))
        if hole is not None and (r["hole"] is None or hole < r["hole"]):
            r["hole"] = hole
    return res


def min_web(flat):
    """Narrowest strip of material between two cut contours (including the outline)."""
    outer, holes = split_wires(flat)
    wires, best = [outer] + holes, None
    for i in range(len(wires)):
        for j in range(i + 1, len(wires)):
            bi, bj = wires[i].BoundBox, wires[j].BoundBox
            if best is not None and i > 0 and (bi.XMin - bj.XMax > best or bj.XMin - bi.XMax > best
                                               or bi.YMin - bj.YMax > best or bj.YMin - bi.YMax > best):
                continue
            d = wires[i].distToShape(wires[j])[0]
            if best is None or d < best:
                best = d
    return best


# ---------------------------------------------------------------- rebuilding at stock thickness
def bend_solid(b, t):
    """Solid for one bend: inside radius kept, material added outward to thickness t."""
    g = b["geom"]
    R, r1, r2, pa, pb = g["R"], g["r1"], g["r2"], g["pa"], g["pb"]
    assert b["up"], "bend is not on the inside of the kept skin"
    c = pa - r1
    m = (r1 + r2).normalize()
    k = (R + t) / R
    a1, a2, b1, b2 = c + r1, c + r2, c + r1 * k, c + r2 * k
    wire = Part.Wire([Part.Arc(a1, c + m * R, a2).toShape(), Part.makeLine(a2, b2),
                      Part.Arc(b2, c + m * (R + t), b1).toShape(), Part.makeLine(b1, a1)])
    return Part.Face(wire).extrude(pb - pa)


def wall_solid(face, t):
    return face.extrude(normal(face) * -t)


def fuse(solids):
    out = solids[0] if len(solids) == 1 else solids[0].multiFuse(solids[1:], 1e-6).removeSplitter()
    assert out.isValid() and len(out.Solids) == 1, "rebuild did not give one valid solid"
    return out.Solids[0]


def inside_skin(shape, keep_normal=None):
    """Unfolder plus the wall face to start from: the skin on the inside of the bends.

    Flat parts have no bends, so keep_normal picks which face stays where it is."""
    U = Unfolder(shape, MATERIAL["k_factor"], print)
    planes = sorted((i for i, f in enumerate(U.faces) if surf(f) == "Plane"), key=lambda i: -U.faces[i].Area)[:2]
    if keep_normal is not None:
        start = next(i for i in planes if normal(U.faces[i]).dot(keep_normal) > 0.999)
    else:
        start = max(planes, key=lambda i: sum(b["length"] * (1 if b["up"] else -1) for b in U.unfold(i)[2]))
    return U, start


def rethicken(shape, t, keep_normal=None):
    """Same part at thickness t: the inside-of-bend skin stays put, material grows away from it."""
    U, start = inside_skin(shape, keep_normal)
    T, _, bends = U.unfold(start)
    return fuse([wall_solid(U.faces[i], t) for i in T] + [bend_solid(b, t) for b in bends])

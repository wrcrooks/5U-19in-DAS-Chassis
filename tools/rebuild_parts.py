"""Build the manufacturable parts in CAD/Revised from the Onshape exports in CAD/.

    freecadcmd tools/rebuild_parts.py

Changes made to the exported design:
  * every sheet part is rebuilt at stock thickness (0.080 in = 2.032 mm). The skin on the inside of
    the bends stays where it was, so the 0.965 mm inside radius is kept and parts grow outward.
  * Chassis: side walls lowered to WALL_HEIGHT so the base is at least twice the wall height, and
    the four bent front tabs removed so the part has bends on one axis only.
  * Bezel Mounting Bracket (new, 2 off): bolt-on L-bracket that replaces the front tabs. Its front
    holes are where the tab holes were, so the Bezel and handles are unchanged.
  * Top covers (new): Drive Bay Cover and Rear Electronics Cover drop in from above and rest on the
    side walls, with finger holes for lifting. Attic Baffle (2 off) bolts to the side walls.
  * Back Panel: exhaust area increased, and the six low-profile bracket slots merged into one.
  * Drive layout: the four backplanes (Supermicro BPN-SAS3-826EL1, three drives per stack) are spread
    across the width so air passes both sides of every stack. Spacing inside a backplane is untouched.
    The Drive Support Panel has one opening per stack with clearance, and the Chassis floor holes
    that follow the backplanes move with them.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheetmetal import *

T_STOCK = MATERIAL["thickness"]
R_IN = MATERIAL["bend_radius"]

WALL_HEIGHT = 212.0            # top of the chassis side walls above the underside datum (was 221)
HOLE_R = 2.6                   # M5 clearance, as used elsewhere in the design
ONSHAPE_PARTS = ("Chassis", "Bezel", "Back Panel", "Chassis Rear Support Bracket", "Drive Support Panel")
# Bezel Mounting Bracket, right-hand instance (the left one is its mirror image, same part flipped)
BR_Z = (20.0, 188.0)           # same span as the handles
BR_FRONT_Y = -323.0            # back face of the Bezel
BR_SIDE_LEN = 24.0             # leg along the side wall (outside dimension)
BR_FRONT_END_X = 192.5         # inner end of the front leg, where the old tab ended
BR_FRONT_HOLES = [(202.5, 30.0), (202.5, 178.0)]       # (x, z): bezel and handle screws
BR_WALL_HOLES = [(-309.0, 50.0), (-309.0, 104.0), (-309.0, 158.0)]   # (y, z): bracket to side wall

# Drive layout. Everything set by the backplane is taken from the Onshape model and left alone.
DRIVE_T, DRIVE_W = 26.1, 101.6           # 3.5 in drive thickness and width
STACK_PITCH = 27.1                       # drive-to-drive spacing within a backplane (x)
ROW_Y = [-292.9, -183.3, -73.7, 35.9]    # front edge of each drive row (109.6 pitch along a backplane)
STACK_W = 2 * STACK_PITCH + DRIVE_T      # 80.3 over three drives
N_TRAYS = 4                              # backplanes side by side; 5 fit only at 82.3 pitch (2 mm air gaps)
BACKPLANE_PITCH = 105.4                  # 25.1 mm of air between stacks, 12.7 at the walls
STACK_CX = [(i - (N_TRAYS - 1) / 2) * BACKPLANE_PITCH for i in range(N_TRAYS)]   # stack centres
STACK_X = [cx - STACK_W / 2 for cx in STACK_CX]
SLOT_CLEAR = 0.5                         # clearance around the drives in the panel openings, per side
OLD_STACK_X = [-162.6, -80.3, 2.0, 84.3] # first drive face of each stack in the Onshape model
OLD_FLOOR_HOLE_Y = -284.6                # Onshape floor holes, one under each tray's TRAY_FLOOR_POST
# Printed Backplane Tray (CAD/Backplane Tray), one under each stack, placed as in the Onshape model:
# long axis front to back, power-connector end (tray +x) towards the Bezel, mounting-hole edge
# (tray y = +4) on the right. The Onshape model had the trays edge to edge and centred, which puts
# the first drive face 2.0 mm from the tray's left edge and the last flush with its right edge.
TRAY_DIR = os.path.join(CAD, "Backplane Tray")
STACK_TRAY_OFFSET = 1.0                  # stack centre sits this far right of the tray centre
TRAY_FLOOR_POST = (415.1, -51.6)         # tray-frame post that sits over the Chassis floor hole
TRAY_JOINT_DY = -40.3                    # second Part A to Part B connector, relative to the first
FLOOR_TOP_Z = 2.0
DAM_T = 3.0                              # printed air dam across the front of each tray
DAM_Z = (2.5, 29.5)                      # floor to just under the backplane (underside at 30)
DAM_WINDOW_Z = (6.5, 16.5)               # metered opening: the expander heatsinks under the boards need air
DAM_LUG_YT = [0.0, -56.3]                # tray-frame positions of the front-end sockets
DAM_LUG_XT = 419.5
# The trays are 82.3 mm wide and link edge to edge with a dog-bone connector, 8 mm between lobes.
# The wider backplane spacing needs a longer side link.
TRAY_WIDTH = 82.3
TRAY_SIDE_SOCKETS_XT = [43.0, 141.5, 258.1, 342.5]
TRAY_SIDE_SOCKET_YT = (0.0, -74.3)
TRAY_LINK = dict(lobe_r=2.0, bar_w=2.0, thickness=2.0, centres=8.0)

# Back Panel changes (positions are the Onshape model's, x across, z up)
BRACKET_SLOT_Z = (82.6, 84.2)            # row of six slots for the low-profile PCIe bracket lips
VENT_WIDTH = 18.0                        # slanted exhaust slots widened from 12 mm (32 mm pitch, 14 mm bars)
VENT_APEX_GAP = 4.0                      # the two slots either side of the centre line stay this far apart
VENT_LONG_BOTTOM = 110.5                 # the seven long vents run from here up to 198.5
VENT_COPY_X = (-32.0, 96.0)              # the four long vents above the free area between the cards and the PSU
VENT_COPY_DROP = 96.0                    # repeated this far down, leaving an 8 mm bar between the rows
VENT_RIGHT_BOTTOM = 154.5                # short vents on the right lengthened to just above the PSU
VENT_LEFT_BOTTOM = 130.0                 # short vents on the left lengthened to just above the card bracket slot

# Top covers: inverted U, flanges outside the chassis side walls
COVER_UNDER_Z = WALL_HEIGHT     # covers drop in and rest on the tops of the chassis side walls,
                               # held in place by the Bezel, fan wall and Back Panel standing 7 mm proud
COVER_GAP = 1.0                # side clearance per side; must exceed the bend radius so the plate sits flat
COVER_FLANGE = 15.0            # flange length outside, measured from the top surface
DRIVE_COVER_Y = (-322.5, 166.45)       # Bezel back face is -323, fan wall front face is 166.97
REAR_COVER_Y = (169.25, 414.75)        # fan wall rear face is 169, Back Panel inside face is 415
FINGER_HOLE_R = 12.5                   # lifting holes
DRIVE_COVER_FINGER_Y = [-228.0, 72.0]  # both over the sealed space between the Attic Baffles
REAR_COVER_FINGER_Y = [292.0]
# Attic Baffle: closes the space between the Drive Support Panel and the Drive Bay Cover
PANEL_TOP_Z = 175.0 + T_STOCK
BAFFLE_Z = (PANEL_TOP_Z + 0.5, COVER_UNDER_Z - 0.5)
BAFFLE_HALF_WIDTH = 212.75             # 0.25 clear of each side wall
BAFFLE_TAB = 25.0
BAFFLE_HOLE = (12.5, 201.0)            # (distance behind the baffle's front face, z)
# Printed support for the edge connectors of the SAS expander cards (Adaptec AEC-82885T, low profile).
# The cards hang from their brackets in the Back Panel; there is no motherboard slot under them.
CARD_OPENING_X0 = -155.2                 # centre of the first Back Panel card opening (Onshape)
CARD_PITCH = 20.3                        # Back Panel opening pitch (PCIe slot pitch is 20.32)
CARD_SLOTS = 6
CARD_PCB_DX = -9.0                       # PCB centre from its opening centre: estimate, not measured
CARD_CHANNEL_W = 2.2                     # for a 1.57 mm PCB
CARD_SUPPORT_Y = (320.0, 380.0)          # spans the x4 edge fingers, about 44-85 mm inside the Back Panel
CARD_SUPPORT_H = 11.0                    # stays below the card's lower edge
CARD_SUPPORT_BASE = 2.0                  # material under the channels
CARD_EAR = (20.0, 5.0)                   # length beyond the outer channels, thickness
CARD_EAR_SLOT = (5.5, 13.5)              # M5 slot, long in x: +/-4 mm of sideways adjustment
CARD_SUPPORT_HOLES_X = [CARD_OPENING_X0 + CARD_PCB_DX - 18.0,
                        CARD_OPENING_X0 + CARD_PCB_DX + (CARD_SLOTS - 1) * CARD_PITCH + 18.0]

BAFFLE_FRONT_Y = [-297.0, 139.5]       # front face of the front and rear baffles


def chassis_extra_holes():
    """(centre, axis) of the holes the Attic Baffles need in the Chassis side walls, and the two
    floor holes for the Card Edge Support."""
    out = [(V(x, sum(CARD_SUPPORT_Y) / 2, -10.0), V(0, 0, 1)) for x in CARD_SUPPORT_HOLES_X]
    for sx in (-1, 1):
        for yf in BAFFLE_FRONT_Y:
            out.append((V(sx * 205, yf + BAFFLE_HOLE[0], BAFFLE_HOLE[1]), V(sx, 0, 0)))
    return out


def u_channel(origin, eu, ev, ew, half_in, depth_in, length):
    """U section. Web inside face at v=0, flange inside faces at u=+-half_in, flange tips at
    v=depth_in, extruded along ew. Inside bend radius R_IN, material outside the inside skin."""
    t, r, R, a, d = T_STOCK, R_IN, R_IN + T_STOCK, half_in, depth_in
    s = 2 ** -0.5
    P = lambda u, v: origin + eu * u + ev * v
    L = lambda p, q: Part.makeLine(P(*p), P(*q))
    A = lambda p, m, q: Part.Arc(P(*p), P(*m), P(*q)).toShape()
    c = a - r
    wire = Part.Wire([
        L((a, d), (a, r)), A((a, r), (c + r * s, r - r * s), (c, 0)), L((c, 0), (-c, 0)),
        A((-c, 0), (-c - r * s, r - r * s), (-a, r)), L((-a, r), (-a, d)), L((-a, d), (-a - t, d)),
        L((-a - t, d), (-a - t, r)), A((-a - t, r), (-c - R * s, r - R * s), (-c, -t)), L((-c, -t), (c, -t)),
        A((c, -t), (c + R * s, r - R * s), (a + t, r)), L((a + t, r), (a + t, d)), L((a + t, d), (a, d))])
    return Part.Face(wire).extrude(ew * length)


def drill(body, holes, depth=30.0, radius=None):
    for centre, axis in holes:
        body = body.cut(Part.makeCylinder(radius or HOLE_R, depth, centre, axis))
    assert body.isValid() and len(body.Solids) == 1
    return body.Solids[0]


def build_cover(y_range, finger_y):
    assert COVER_GAP >= R_IN, "cover would ride up on its bend radius"
    half_in = 213.0 + T_STOCK + COVER_GAP
    body = u_channel(V(0, y_range[0], COVER_UNDER_Z), V(1, 0, 0), V(0, 0, -1), V(0, 1, 0),
                     half_in, COVER_FLANGE - T_STOCK, y_range[1] - y_range[0])
    return drill(body, [(V(0, y, COVER_UNDER_Z - 5), V(0, 0, 1)) for y in finger_y], radius=FINGER_HOLE_R)


def build_baffle(y_front):
    body = u_channel(V(0, y_front + T_STOCK, BAFFLE_Z[0]), V(1, 0, 0), V(0, 1, 0), V(0, 0, 1),
                     BAFFLE_HALF_WIDTH - T_STOCK, BAFFLE_TAB - T_STOCK, BAFFLE_Z[1] - BAFFLE_Z[0])
    return drill(body, [(V(sx * 205, y_front + BAFFLE_HOLE[0], BAFFLE_HOLE[1]), V(sx, 0, 0)) for sx in (-1, 1)])


def build_chassis(orig):
    U, start = inside_skin(orig)
    T, _, bends = U.unfold(start)
    floor = U.faces[start]
    walls = [i for i in T if abs(normal(U.faces[i]).x) > 0.999]
    assert len(walls) == 2
    outer, holes = split_wires(floor)
    moved = 0
    for k, h in enumerate(holes):
        c = h.BoundBox.Center
        if abs(c.y - OLD_FLOOR_HOLE_Y) < 0.1:
            n = min(range(4), key=lambda q: abs(c.x - OLD_STACK_X[q] - 24.7))
            post = tray_place(V(TRAY_FLOOR_POST[0], TRAY_FLOOR_POST[1], 0), STACK_CX[n])
            assert abs(post.x - (c.x + STACK_X[n] - OLD_STACK_X[n])) < 0.1 and abs(post.y - c.y) < 0.1, \
                "floor hole is not under the tray post"
            holes[k] = h.copy()
            holes[k].translate(V(post.x - c.x, post.y - c.y, 0))
            moved += 1
    assert moved == 4 == N_TRAYS, "expected one Onshape floor hole per tray"
    new_floor = Part.makeFace([outer] + holes, "Part::FaceMakerBullseye")
    solids = [new_floor.extrude(normal(floor) * -T_STOCK)]
    solids += [bend_solid(b, T_STOCK) for b in bends if b["walls"][0] == start]
    for i in walls:
        f = U.faces[i]
        bb, n = f.BoundBox, normal(f)
        x = bb.XMin
        corners = [V(x, bb.YMin, bb.ZMin), V(x, bb.YMax, bb.ZMin), V(x, bb.YMax, WALL_HEIGHT), V(x, bb.YMin, WALL_HEIGHT)]
        outer, holes = split_wires(f)
        assert all(len(h.Edges) == 1 for h in holes), "unexpected cut-out in side wall"
        new = [Part.Wire(Part.makeCircle(HOLE_R, V(x, y, z), V(1, 0, 0))) for y, z in BR_WALL_HOLES]
        face = Part.makeFace([Part.makePolygon(corners + corners[:1])] + holes + new, "Part::FaceMakerBullseye")
        solids.append(face.extrude(n * -T_STOCK))
    return drill(fuse(solids), chassis_extra_holes())


def build_back_panel(orig):
    """Onshape Back Panel with a larger exhaust and the card-bracket slots merged per row.

    Exhaust openings stay as wide, steep slots: nothing fine enough to trap lint and no ledges
    for dust to settle on."""
    U, start = inside_skin(orig)
    T, _, bends = U.unfold(start)
    plate = U.faces[start]
    outer, holes = split_wires(plate)
    y = plate.BoundBox.YMin
    poly = lambda pts: Part.makePolygon(pts + pts[:1])
    slanted = lambda w: len(w.Edges) == 4 and any(
        abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) > 0.1 and abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 0.1
        for e in w.Edges)
    keep, lips, vents = [], [], []
    for w in holes:
        b = w.BoundBox
        if len(w.Edges) == 4 and (round(b.ZMin, 2), round(b.ZMax, 2)) == BRACKET_SLOT_Z:
            lips.append(w)                                    # low-profile bracket slots, 0.8 mm apart
        elif slanted(w):
            pts = [v.Point for v in w.OrderedVertexes]
            hi = sorted((p for p in pts if p.z > b.ZMax - 1), key=lambda p: p.x)
            lo = sorted((p for p in pts if p.z < b.ZMin + 1), key=lambda p: p.x)
            vents.append(dict(xl=hi[0].x, xr=hi[1].x, top=b.ZMax, bottom=b.ZMin,
                              lean=(lo[0].x - hi[0].x) / (b.ZMax - b.ZMin), x0=b.XMin, x1=b.XMax))
        else:
            keep.append(w)
    assert len(lips) == 6 and len(vents) == 12, "unexpected Back Panel cut-outs (%d, %d)" % (len(lips), len(vents))
    grow = VENT_WIDTH - (vents[0]["xr"] - vents[0]["xl"])
    added = []
    for v in vents:
        long = abs(v["bottom"] - VENT_LONG_BOTTOM) < 0.01
        if abs(v["x1"] + VENT_APEX_GAP / 2) < 0.01:           # the pair that meets at the centre grows outwards only
            v["xl"] -= grow
        elif abs(v["x0"] - VENT_APEX_GAP / 2) < 0.01:
            v["xr"] += grow
        else:
            v["xl"] -= grow / 2
            v["xr"] += grow / 2
        if not long:                                          # short vents: lengthen down to clear what is below
            v["bottom"] = VENT_RIGHT_BOTTOM if v["x0"] > 0 else VENT_LEFT_BOTTOM
        rows = [0.0]
        if long and VENT_COPY_X[0] - 0.01 <= v["x0"] and v["x1"] <= VENT_COPY_X[1] + 0.01:
            rows.append(-VENT_COPY_DROP)                      # second row below the first
        for dz in rows:
            h, sh = v["top"] - v["bottom"], v["lean"] * (v["top"] - v["bottom"])
            added.append(poly([V(v["xl"], y, v["top"] + dz), V(v["xr"], y, v["top"] + dz),
                               V(v["xr"] + sh, y, v["bottom"] + dz), V(v["xl"] + sh, y, v["bottom"] + dz)]))
    x0 = min(w.BoundBox.XMin for w in lips)
    x1 = max(w.BoundBox.XMax for w in lips)
    z0, z1 = BRACKET_SLOT_Z
    added.append(poly([V(x0, y, z0), V(x1, y, z0), V(x1, y, z1), V(x0, y, z1)]))
    new_plate = Part.makeFace([outer] + keep + added, "Part::FaceMakerBullseye")
    assert abs(new_plate.Area - (Part.Face(outer).Area - sum(Part.Face(w).Area for w in keep + added))) < 1e-3, \
        "Back Panel cut-outs overlap"
    assert len(added) == 17, "expected 16 exhaust slots and one bracket slot, got %d" % len(added)
    solids = [new_plate.extrude(normal(plate) * -T_STOCK)]
    solids += [wall_solid(U.faces[i], T_STOCK) for i in T if i != start]
    solids += [bend_solid(b, T_STOCK) for b in bends]
    return fuse(solids)


def build_drive_panel(orig):
    """Onshape panel with its 48 single-drive slots replaced by one opening per stack of three."""
    U, start = inside_skin(orig)
    T, _, bends = U.unfold(start)
    plate = U.faces[start]
    outer, holes = split_wires(plate)
    assert len(holes) == 48 and all(len(h.Edges) == 4 for h in holes), "unexpected drive panel cut-outs"
    z, c = plate.BoundBox.ZMin, SLOT_CLEAR
    slots = []
    for x in STACK_X:
        for y in ROW_Y:
            x0, x1, y0, y1 = x - c, x + STACK_W + c, y - c, y + DRIVE_W + c
            pts = [V(x0, y0, z), V(x1, y0, z), V(x1, y1, z), V(x0, y1, z)]
            slots.append(Part.makePolygon(pts + pts[:1]))
    new_plate = Part.makeFace([outer] + slots, "Part::FaceMakerBullseye")
    solids = [new_plate.extrude(normal(plate) * -T_STOCK)]
    solids += [wall_solid(U.faces[i], T_STOCK) for i in T if i != start]
    solids += [bend_solid(b, T_STOCK) for b in bends]
    return fuse(solids)


_tray = {}


def tray_parts():
    if not _tray:
        for n in ("Part A", "Part B", "Connector"):
            _tray[n] = load(os.path.join(TRAY_DIR, "Backplane Tray - %s.step" % n))
        bb = _tray["Part A"].BoundBox
        bb.add(_tray["Part B"].BoundBox)
        rows_centre = (ROW_Y[0] + ROW_Y[-1] + DRIVE_W) / 2
        _tray["centre_yt"] = (bb.YMin + bb.YMax) / 2
        _tray["offset_y"] = rows_centre + (bb.XMin + bb.XMax) / 2
        _tray["front_xt"] = bb.XMax
        assert abs(bb.ZMin) < 1e-6 and abs(bb.YLength - TRAY_WIDTH) < 1e-6
    return _tray


def tray_place(obj, cx):
    """Tray frame to chassis for the tray under the stack centred at cx: tray +x points to the Bezel."""
    t = tray_parts()
    move = V(cx - STACK_TRAY_OFFSET - t["centre_yt"], t["offset_y"], FLOOR_TOP_Z)
    if isinstance(obj, App.Vector):
        return V(obj.y, -obj.x, obj.z) + move
    out = obj.copy()
    out.rotate(V(0, 0, 0), V(0, 0, 1), -90)
    out.translate(move)
    return out


def build_air_dam(cx):
    """Printed wall across the front of one tray, plugged into the tray's two front-end sockets."""
    t = tray_parts()
    k = TRAY_LINK
    y1 = tray_place(V(t["front_xt"], 0, 0), cx).y          # front end of the tray
    body = Part.makeBox(BACKPLANE_PITCH, DAM_T, DAM_Z[1] - DAM_Z[0], V(cx - BACKPLANE_PITCH / 2, y1 - DAM_T, DAM_Z[0]))
    lugs = [tray_place(V(DAM_LUG_XT, yt, k["thickness"]), cx) for yt in DAM_LUG_YT]
    tx = cx - STACK_TRAY_OFFSET                           # windows across the tray width, legs at the lugs
    spans, x = [], tx - TRAY_WIDTH / 2 + 3
    for lx in sorted(l.x for l in lugs) + [tx + TRAY_WIDTH / 2 + 1]:
        spans.append((x, min(lx - 4, tx + TRAY_WIDTH / 2 - 3)))
        x = lx + 4
    for x0, x1 in spans:
        if x1 - x0 < 5:
            continue
        body = body.cut(Part.makeBox(x1 - x0, 3 * DAM_T, DAM_WINDOW_Z[1] - DAM_WINDOW_Z[0], V(x0, y1 - 2 * DAM_T, DAM_WINDOW_Z[0])))
    for l in lugs:
        bar = Part.makeBox(k["bar_w"], l.y - y1, k["thickness"], V(l.x - k["bar_w"] / 2, y1, l.z))
        lobe = Part.makeCylinder(k["lobe_r"], k["thickness"], l)
        body = body.fuse(bar).fuse(lobe)
    body = body.removeSplitter()
    assert body.isValid() and len(body.Solids) == 1
    return body.Solids[0]


def build_card_support():
    """Printed comb screwed to the floor: one open-ended channel per card slot holds the card's edge
    fingers sideways. The channels are deep and open at both ends, so the card's height and its
    distance from the Back Panel do not have to be known exactly; the bracket carries the weight."""
    y0, y1 = CARD_SUPPORT_Y
    pcb = [CARD_OPENING_X0 + CARD_PCB_DX + i * CARD_PITCH for i in range(CARD_SLOTS)]
    ear, ear_t = CARD_EAR
    z0 = 2.0                                                   # floor top
    body = Part.makeBox(pcb[-1] - pcb[0] + 16.0, y1 - y0, CARD_SUPPORT_H, V(pcb[0] - 8.0, y0, z0))
    base = Part.makeBox(pcb[-1] - pcb[0] + 2 * ear, y1 - y0, ear_t, V(pcb[0] - ear, y0, z0))
    body = body.fuse(base)
    top, w = z0 + CARD_SUPPORT_H, CARD_CHANNEL_W
    for x in pcb:
        body = body.cut(Part.makeBox(w, y1 - y0 + 2, CARD_SUPPORT_H, V(x - w / 2, y0 - 1, z0 + CARD_SUPPORT_BASE)))
        # lead-in: the channel widens to 5 mm over its top 2.5 mm
        tri = Part.makePolygon([V(x - 2.5, y0 - 1, top), V(x + 2.5, y0 - 1, top), V(x, y0 - 1, top - 4.5), V(x - 2.5, y0 - 1, top)])
        body = body.cut(Part.Face(tri).extrude(V(0, y1 - y0 + 2, 0)))
    sw, sl = CARD_EAR_SLOT
    for x in CARD_SUPPORT_HOLES_X:
        yc = (y0 + y1) / 2
        slot = Part.makeBox(sl - sw, sw, 30, V(x - (sl - sw) / 2, yc - sw / 2, 0))
        for dx in (-(sl - sw) / 2, (sl - sw) / 2):
            slot = slot.fuse(Part.makeCylinder(sw / 2, 30, V(x + dx, yc, 0)))
        body = body.cut(slot)
    body = body.removeSplitter()
    assert body.isValid() and len(body.Solids) == 1
    return body.Solids[0]


def build_tray_link():
    """Dog-bone connector for the side joints between Backplane Trays at the new spacing."""
    k = TRAY_LINK
    d = k["centres"] + BACKPLANE_PITCH - TRAY_WIDTH
    disc = lambda x: Part.Face(Part.Wire(Part.makeCircle(k["lobe_r"], V(x, 0, 0))))
    bar = Part.makePlane(d, k["bar_w"], V(0, -k["bar_w"] / 2, 0))
    face = disc(0).multiFuse([disc(d), bar]).removeSplitter()
    body = face.extrude(V(0, 0, k["thickness"]))
    assert body.isValid() and len(body.Solids) == 1
    return body.Solids[0]


def build_bracket(wall_x):
    """Right-hand bracket; wall_x is the inside face of the right side wall."""
    t, r, R = T_STOCK, R_IN, R_IN + T_STOCK
    y0, z0, z1 = BR_FRONT_Y, BR_Z[0], BR_Z[1]
    cx, cy = wall_x - R, y0 + R                     # bend axis
    s = 2 ** -0.5
    P = lambda x, y: V(x, y, z0)
    wire = Part.Wire([
        Part.makeLine(P(wall_x, y0 + BR_SIDE_LEN), P(wall_x, cy)),
        Part.Arc(P(wall_x, cy), P(cx + R * s, cy - R * s), P(cx, y0)).toShape(),
        Part.makeLine(P(cx, y0), P(BR_FRONT_END_X, y0)),
        Part.makeLine(P(BR_FRONT_END_X, y0), P(BR_FRONT_END_X, y0 + t)),
        Part.makeLine(P(BR_FRONT_END_X, y0 + t), P(cx, y0 + t)),
        Part.Arc(P(cx, y0 + t), P(cx + r * s, cy - r * s), P(wall_x - t, cy)).toShape(),
        Part.makeLine(P(wall_x - t, cy), P(wall_x - t, y0 + BR_SIDE_LEN)),
        Part.makeLine(P(wall_x - t, y0 + BR_SIDE_LEN), P(wall_x, y0 + BR_SIDE_LEN))])
    body = Part.Face(wire).extrude(V(0, 0, z1 - z0))
    for x, z in BR_FRONT_HOLES:
        body = body.cut(Part.makeCylinder(HOLE_R, 3 * t, V(x, y0 - t, z), V(0, 1, 0)))
    for y, z in BR_WALL_HOLES:
        body = body.cut(Part.makeCylinder(HOLE_R, 3 * t, V(wall_x - 2 * t, y, z), V(1, 0, 0)))
    assert body.isValid() and len(body.Solids) == 1
    return body.Solids[0]


def main():
    os.makedirs(REVISED, exist_ok=True)
    src = lambda n: load(os.path.join(CAD, "Assembly - %s.step" % n))
    parts = {}
    parts["Chassis"] = build_chassis(src("Chassis"))
    parts["Bezel"] = rethicken(src("Bezel"), T_STOCK, keep_normal=V(0, 1, 0))   # back face stays on the chassis
    parts["Back Panel"] = build_back_panel(src("Back Panel"))
    parts["Chassis Rear Support Bracket"] = rethicken(src("Chassis Rear Support Bracket"), T_STOCK)
    parts["Drive Support Panel"] = build_drive_panel(src("Drive Support Panel"))
    parts["Bezel Mounting Bracket"] = build_bracket(213.0)
    parts["Drive Bay Cover"] = build_cover(DRIVE_COVER_Y, DRIVE_COVER_FINGER_Y)
    parts["Rear Electronics Cover"] = build_cover(REAR_COVER_Y, REAR_COVER_FINGER_Y)
    parts["Attic Baffle"] = build_baffle(BAFFLE_FRONT_Y[0])
    new_parts = [n for n in parts if n not in ONSHAPE_PARTS]
    for n, s in parts.items():
        save([(n, s)], os.path.join(REVISED, n + ".step"))
        o = src(n) if n in ONSHAPE_PARTS else None
        bb = s.BoundBox
        print("%-30s %8.3f x %8.3f x %8.3f  vol %.0f%s" % (n, bb.XLength, bb.YLength, bb.ZLength, s.Volume,
              "" if o is None else "  (was %.0f, x%.4f)" % (o.Volume, s.Volume / o.Volume)))

    link = build_tray_link()
    save([("Backplane Tray Connector (Wide)", link)], os.path.join(REVISED, "Backplane Tray - Connector (Wide).step"))
    print("%-30s %8.3f x %8.3f x %8.3f  vol %.0f" % ("Backplane Tray Connector (Wide)", link.BoundBox.XLength,
          link.BoundBox.YLength, link.BoundBox.ZLength, link.Volume))

    dam = build_air_dam(STACK_CX[0])
    save([("Backplane Tray Air Dam", dam)], os.path.join(REVISED, "Backplane Tray - Air Dam.step"))
    print("%-30s %8.3f x %8.3f x %8.3f  vol %.0f" % ("Backplane Tray Air Dam", dam.BoundBox.XLength,
          dam.BoundBox.YLength, dam.BoundBox.ZLength, dam.Volume))

    comb = build_card_support()
    save([("Card Edge Support", comb)], os.path.join(REVISED, "Card Edge Support.step"))
    print("%-30s %8.3f x %8.3f x %8.3f  vol %.0f" % ("Card Edge Support", comb.BoundBox.XLength,
          comb.BoundBox.YLength, comb.BoundBox.ZLength, comb.Volume))

    # Complete assembly: revised sheet parts, both brackets, and the untouched bought/printed parts.
    grow = T_STOCK - 2.0
    asm = [(n, s) for n, s in parts.items() if n not in ("Bezel Mounting Bracket", "Attic Baffle")]
    asm.append(("Attic Baffle (Front)", parts["Attic Baffle"]))
    asm.append(("Attic Baffle (Rear)", build_baffle(BAFFLE_FRONT_Y[1])))
    asm.append(("Bezel Mounting Bracket (Right)", parts["Bezel Mounting Bracket"]))
    asm.append(("Bezel Mounting Bracket (Left)", parts["Bezel Mounting Bracket"].mirror(V(0, 0, 0), V(1, 0, 0))))
    for n in ("Left Front Handle", "Right Front Handle"):
        h = src(n)
        h.translate(V(0, -grow, 0))          # the Bezel's front face moved forward by the added thickness
        asm.append((n, h))
    for n in ("PSU", "SFF8643 to M.2 Mounting Bracket"):
        asm.append((n, src(n)))
    asm.append(("Card Edge Support", comb))
    t = tray_parts()
    new_parts += ["Backplane Tray", "Air Dam", "Card Edge Support"]
    for i, cx in enumerate(STACK_CX):
        asm.append(("Backplane Tray %d Part A" % (i + 1), tray_place(t["Part A"], cx)))
        asm.append(("Backplane Tray %d Part B" % (i + 1), tray_place(t["Part B"], cx)))
        asm.append(("Air Dam %d" % (i + 1), build_air_dam(cx)))
    small = []
    for i, cx in enumerate(STACK_CX):
        for dy in (0.0, TRAY_JOINT_DY):
            c = t["Connector"].copy()
            c.translate(V(0, dy, 0))
            small.append(("Tray %d Connector" % (i + 1), tray_place(c, cx)))
        if i + 1 < N_TRAYS:
            for xt in TRAY_SIDE_SOCKETS_XT:
                a = tray_place(V(xt, TRAY_SIDE_SOCKET_YT[0], TRAY_LINK["thickness"]), cx)
                b = tray_place(V(xt, TRAY_SIDE_SOCKET_YT[1], TRAY_LINK["thickness"]), STACK_CX[i + 1])
                assert b.x > a.x and abs((b - a).Length - (link.BoundBox.XLength - 2 * TRAY_LINK["lobe_r"])) < 1e-6, "link does not span the sockets"
                l = link.copy()
                l.translate(a)
                small.append(("Tray %d-%d Connector (Wide)" % (i + 1, i + 2), l))
    save(asm + small, os.path.join(REVISED, "Complete-Assembly.step"))

    print("interference (mm3) above 0.5, and clearance (mm) for the new parts:")
    for i in range(len(asm)):
        for j in range(i + 1, len(asm)):
            if asm[i][1].BoundBox.intersect(asm[j][1].BoundBox):
                v = asm[i][1].common(asm[j][1]).Volume
                if v > 0.5:
                    print("   %-32s x %-32s %.2f" % (asm[i][0], asm[j][0], v))
    for n, s in asm:
        if any(n.startswith(p) for p in new_parts):
            near = sorted((s.distToShape(o)[0], m) for m, o in asm if m != n)[:3]
            print("   %-32s nearest: %s" % (n, ", ".join("%s %.2f" % (m, d) for d, m in near)))


main()

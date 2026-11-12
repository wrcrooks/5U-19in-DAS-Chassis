# Sheet-metal bend data

Flat patterns and bend tables for the parts to be laser cut and bent by SendCutSend.

- `CAD/*.step` is the untouched Onshape export.
- `CAD/Revised/*.step` holds the manufacturable parts, built by `freecadcmd tools/rebuild_parts.py`.
- `CAD/Flat-Patterns/` holds the flat patterns of the revised parts, built by
  `freecadcmd tools/unfold_sheet_metal.py`. The same numbers are in `bend-data.json`.

Run both commands from the repository root, in that order, after any change.

## Changes from the Onshape export

| Change | Reason |
|---|---|
| All sheet parts rebuilt at 2.032 mm (0.080 in) instead of 2.00 mm | SendCutSend wants 3D models at stock thickness. The inside bend radius stays 0.965 mm and each part grows away from the inside of its bends. |
| Chassis side walls lowered from 221 mm to 212 mm | U-channel rule: base must be at least 2x the flange height. Now 430.06 / 212.03 = 2.03x. |
| Four bent front tabs removed from the Chassis | The tabs were bent on an axis perpendicular to the 221 mm walls, which SendCutSend limits to 5 in flanges. The Chassis now has two parallel bends only. |
| New part: Bezel Mounting Bracket, 2 off | Bolt-on L-bracket that replaces the tabs. Its front holes are where the tab holes were, so the Bezel and handles are unchanged. |
| Three new 5.2 mm holes near the front of each Chassis side wall | Fix the brackets to the walls: 14 mm back from the front edge, at 50, 104 and 158 mm above the underside. |
| New part: Drive Bay Cover | Drop-in lid from the Bezel to the fan wall, no fasteners. It rests on the tops of the side walls, 7 mm below the Bezel and fan wall, which stop it sliding. Its 15 mm flanges hang outside the walls, so the unit is 436.1 mm wide over that band. Two 25 mm finger holes for lifting, both over the sealed space above the drives. |
| New part: Rear Electronics Cover | Separate drop-in lid from the fan wall to the Back Panel, same section, one 25 mm finger hole. |
| New part: Attic Baffle, 2 off | Closes the 34 mm space between the Drive Support Panel and the Drive Bay Cover at the front and rear of the drive array, so air cannot pass over the drives. |
| Four more 5.2 mm holes in the Chassis side walls | Two per side for the Attic Baffles, 201 mm up. |
| Back Panel exhaust enlarged from 8,980 to 22,270 mm² | All slanted vents widened from 12 to 18 mm (14 mm bars between them). Four of the long vents are repeated as a second row below the first, between the card slots and the PSU. The short vents are lengthened: down to 154.5 mm above the PSU, and down to 130 mm above the card slots. The openings stay wide and steep so lint cannot bridge them and dust has no ledge to settle on. |
| Back Panel: the six low-profile bracket slots merged into one 121 x 1.6 mm slot | The slots were 0.8 mm apart, too thin to cut reliably. Each PCIe bracket lip still has its full width; the card openings below locate the brackets. |
| Backplanes spread from 82.3 mm to 105.4 mm pitch | Moves the two 46-48 mm side channels in between the four backplanes (Supermicro BPN-SAS3-826EL1), leaving 25.1 mm of air between stacks and 12.7 mm at each wall. Spacing inside a backplane (27.1 mm between drives, 109.6 mm between rows) is unchanged. |
| Drive Support Panel: 16 openings, one per stack of three drives, in place of 48 single-drive slots | The old slots were exactly drive size (26.1 x 101.6 mm) with 1 mm strips between them. Each opening now has 0.5 mm clearance all round. |
| Four Chassis floor holes at y = -284.6 moved to x = -173.55, -68.15, 37.25, 142.65 | Each stays under the same post of its printed Backplane Tray (tray post at 415.1, -51.6), as in the Onshape model. Hole size unchanged. |

`WALL_HEIGHT` and the dimensions of every new part are constants at the top of `tools/rebuild_parts.py`.

The side clearance of the covers (`COVER_GAP`, 1.0 mm per side) has to stay above the 0.965 mm bend radius,
or the cover rides up on its bend instead of sitting flat on the walls.


## Material and bend parameters

**5052-H32 aluminium, 0.080 in (2.032 mm)**, values from https://sendcutsend.com/bending-calculator/:

| Parameter | Value |
|---|---|
| K-factor | 0.48 |
| Effective inside bend radius at 90° | 0.038 in / 0.965 mm |
| Bend allowance at 90° | 3.048 mm |
| Bend deduction at 90° | 0.116 in / 2.946 mm |
| Die width | 0.472 in / 12.0 mm (keep cut features 6.0 mm from a bend line) |
| Minimum formed flange at 90° | 0.313 in / 7.95 mm |
| Maximum flat size for bending | 30 x 44 in / 762 x 1117.6 mm |
| Maximum bend length | 44 in / 1117.6 mm |

If the stock changes, `MATERIAL` in `tools/sheetmetal.py` and the inside radius of the source models both
have to change with it; SendCutSend does not bend to a custom radius.

## DXF conventions

- Units are millimetres at 1:1, origin at the lower-left corner of the flat pattern.
- Cut geometry is continuous lines, arcs and circles. Bend centrelines are `DASHED` lines. Everything
  is on layer `0`, as SendCutSend's pre-flight asks.
- Each pattern is drawn looking at the face the flanges fold **toward**, so every bend is **90° up**
  (toward the viewer). For the Chassis that is the inside of the floor.
- Bends that share an id are collinear and are formed in one press-brake hit.

## Bend tables

Positions are in DXF coordinates (mm). This section is rewritten by `tools/unfold_sheet_metal.py`.

<!-- bend-tables:start -->

### Chassis: flat 848.24 x 738.00 mm (33.40 x 29.06 in), formed 430.06 x 738 x 212.03

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (210.559, 0) to (210.559, 738) | 738 | 15.96 |
| 2 | 90° | up | (637.677, 0) to (637.677, 738) | 738 | 15.96 |

### Bezel: flat 430.00 x 221.00 mm (16.93 x 8.70 in), formed 430 x 2.03 x 221

No bends; laser cut only.

### Back Panel: flat 470.24 x 221.00 mm (18.51 x 8.70 in), formed 426.06 x 25.03 x 221

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (23.559, 10) to (23.559, 30); (23.559, 191) to (23.559, 211) | 40 | 9.56 |
| 2 | 90° | up | (446.677, 10) to (446.677, 30); (446.677, 191) to (446.677, 211) | 40 | 7.56 |

### Chassis Rear Support Bracket: flat 465.24 x 219.00 mm (18.32 x 8.62 in), formed 426.06 x 22.53 x 219

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (21.059, 10) to (21.059, 28); (21.059, 189) to (21.059, 209) | 38 | 8.46 |
| 2 | 90° | up | (444.177, 10) to (444.177, 28); (444.177, 189) to (444.177, 209) | 38 | 8.46 |

### Drive Support Panel: flat 486.24 x 440.50 mm (19.14 x 17.34 in), formed 426.06 x 440.5 x 33.03

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (31.559, 0) to (31.559, 440.5) | 440.5 | 12.81 |
| 2 | 90° | up | (454.677, 0) to (454.677, 440.5) | 440.5 | 12.81 |

### Bezel Mounting Bracket: flat 41.55 x 168.00 mm (1.64 x 6.61 in), formed 20.5 x 24 x 168

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (19.027, 0) to (19.027, 168) | 168 | 6.43 |

### Drive Bay Cover: flat 460.24 x 488.95 mm (18.12 x 19.25 in), formed 436.13 x 488.95 x 15

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (13.527, 0) to (13.527, 488.95) | 488.95 | 204.09 |
| 2 | 90° | up | (446.709, 0) to (446.709, 488.95) | 488.95 | 204.09 |

### Rear Electronics Cover: flat 460.24 x 245.50 mm (18.12 x 9.67 in), formed 436.13 x 245.5 x 15

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (13.527, 0) to (13.527, 245.5) | 245.5 | 204.09 |
| 2 | 90° | up | (446.709, 0) to (446.709, 245.5) | 245.5 | 204.09 |

### Attic Baffle: flat 469.61 x 33.97 mm (18.49 x 1.34 in), formed 425.5 x 25 x 33.97

| Bend | Angle | Dir | Segments, (x, y) to (x, y) | Bent length | Nearest cut-out |
|---|---|---|---|---|---|
| 1 | 90° | up | (23.527, 0) to (23.527, 33.968) | 33.968 | 8.43 |
| 2 | 90° | up | (446.081, 0) to (446.081, 33.968) | 33.968 | 8.43 |

<!-- bend-tables:end -->

## Checks against SendCutSend's rules

| Check | Result |
|---|---|
| Flat size within 30 x 44 in | All pass. The Chassis is now 738 mm on its short side against a 762 mm limit. |
| Bend length within 44 in | Pass (longest is 738 mm / 29.06 in; the covers are 489 mm and 245.5 mm). |
| Formed flange at least 7.95 mm | Pass (shortest is the 20.5 mm front leg of the Bezel Mounting Bracket). |
| Cut features at least 6.0 mm from a bend line | Pass. The closest is 6.43 mm, on the Bezel Mounting Bracket's front holes, whose position is fixed by the Bezel. |
| U-channel base at least 2x flange height | Pass. Chassis 2.03x; every other U-section is above 12x. |
| Flanges on two perpendicular bend axes limited to 5 in | Pass. No part bends on two axes. |
| Stock thickness | Pass. All parts are 2.032 mm. |
| Narrowest strip between cuts | Back Panel 1.35 mm (between the merged bracket slot and the neighbouring full-height card opening, as in the Onshape model). Rear Support Bracket 3.0 mm, Bezel 4.0 mm, Drive Support Panel 4.5 mm, all others above 7 mm. |

Bends longer than 24 in carry a ±2° tolerance, which on the Chassis is up to about 7.4 mm of lean at the
top of a 212 mm wall.

## Fit notes

- The Chassis keeps its inside faces, so it is 430.06 mm wide outside and its underside is 0.03 mm lower.
- The Back Panel, Rear Support Bracket and Drive Support Panel keep the inside faces of their flanges,
  so each is now 426.06 mm over its flanges in a 426.00 mm opening: a nominal 0.03 mm overlap per side.
  The export was already a line-to-line fit, and both numbers are far inside the ±0.38 mm bend tolerance.
- The Bezel keeps its back face, so its front face and the handles move forward 0.03 mm in the assembly.

## Verification

- Every revised part is a single valid solid with 0.965 mm inside and 2.997 mm outside bend radii.
- Flat area x thickness matches the solid volume of every part to within 0.16 %.
- Every cut contour in every DXF is closed (checked by re-reading the written files).
- In the revised assembly the only overlaps between parts are the 0.03 mm flange fits listed above.
- The baffles clear every neighbouring part by 0.25 to 0.5 mm; the covers rest on the side walls and clear everything else by 0.25 mm or more.

# Bill of materials and cost estimate

Prices are in USD, quantity one build, as of November 2026, before sales tax. **Only the fan price is a
published figure. Everything else is an estimate**, and the sheet-metal line, the largest one, has not
been quoted: SendCutSend prices per uploaded part and publishes no rate card.

## Summary

| Group | Low | Planning figure | High |
|---|---|---|---|
| Sheet metal (SendCutSend) | 450 | 600 | 800 |
| Cooling | 225 | 240 | 270 |
| Power | 110 | 160 | 220 |
| SAS connectivity (two AEC-82885T expanders, cables) | 185 | 240 | 355 |
| Printed parts and sealing | 25 | 30 | 45 |
| Fasteners | 20 | 25 | 35 |
| Rack mounting | 40 | 60 | 100 |
| **Total to buy** | **1,055** | **1,355** | **1,825** |

Not in the total: the four backplanes and their printed trays (already owned), the 48 drives, the host's
HBA (it needs external SFF-8644 ports), and anything for the NVMe bays of the two -N4 backplanes.

## 1. Sheet metal

5052-H32 aluminium, 0.080 in, laser cut and bent, no finish. Files: `CAD/Revised/*.step`
(or `CAD/Flat-Patterns/*.dxf`).

| Part | Qty | Flat size (mm) | Flat blank (ft², each) | Bends (each) |
|---|---|---|---|---|
| Chassis | 1 | 848.2 x 738.0 | 6.74 | 2 |
| Drive Bay Cover | 1 | 460.2 x 489.0 | 2.42 | 2 |
| Drive Support Panel | 1 | 486.2 x 440.5 | 2.31 | 2 |
| Rear Electronics Cover | 1 | 460.2 x 245.5 | 1.22 | 2 |
| Back Panel | 1 | 470.2 x 221.0 | 1.12 | 2 |
| Chassis Rear Support Bracket | 1 | 465.2 x 219.0 | 1.10 | 2 |
| Bezel | 1 | 430.0 x 221.0 | 1.02 | 0 |
| Attic Baffle | 2 | 469.6 x 34.0 | 0.17 | 2 |
| Bezel Mounting Bracket | 2 | 41.6 x 168.0 | 0.08 | 1 |
| **Total** | **11** | | **16.4** | **18** |

Finished weight is about 6.9 kg (2,564 cm³ at 2.68 g/cm³).

**How the estimate was made:** 16.4 ft² of blank at $20 to $35 per ft² cut (raw 0.080 in 5052 sheet
retails at $12 to $16 per ft²), plus $10 to $25 of bending per bent part for ten bent parts. The Chassis
alone is about 40 % of the area. Replace this line with the real number by uploading the STEP files to
SendCutSend's instant quote.

## 2. Cooling

| Item | Qty | Unit | Total | Note |
|---|---|---|---|---|
| Noctua NF-A12x25 G2 PWM, 120 mm | 6 | 34.90 | 209 | Published price; three twin packs at 64.90 come to 195. Each fan ships with four screws. |
| 120 mm screw-on dust filter | 3 | 5 | 15 | Bezel fan positions. Magnetic filters will not hold on aluminium. |
| PWM fan controller and splitters | 1 | 30 | 30 | There is no motherboard to drive the fans. Skip it if the fans will run at fixed speed from the PSU. |

## 3. Power

| Item | Qty | Unit | Total | Note |
|---|---|---|---|---|
| ATX PSU, 150 x 86 mm, at most 200 mm deep | 1 | 140 | 140 | Size it for spin-up, not running load: 48 drives draw roughly 400 W running but can exceed 1,100 W on 12 V if they all start together. 850 W with staggered spin-up, 1,200 W without. |
| ATX power-on jumper or switch board | 1 | 8 | 8 | Starts the PSU without a motherboard. |
| Backplane power cables and splitters | 1 set | 15 | 15 | Four backplanes. |

## 4. SAS connectivity

Two Adaptec AEC-82885T (2283400-R, also sold Lenovo-branded) 36-port 12 Gb/s SAS expander cards sit in
the Back Panel card slots. Each card has seven internal SFF-8643 connectors and two external SFF-8644
connectors, so the external ports are on the cards' own brackets and no separate slot adapters are needed.

| Item | Qty | Unit | Total | Note |
|---|---|---|---|---|
| Adaptec AEC-82885T expander card | 2 | 60 | 120 | Unit price is an estimate for a used pull. New stock was listed at $329 to $440 and mostly out of stock. |
| Internal SFF-8643 to SFF-8643 cable | 4 | 12 | 48 | One per backplane, two backplanes per card. Not supplied with the cards. |
| External SFF-8644 cable | 2 to 4 | 30 | 60-120 | One or two uplinks per card to the host HBA. |
| 4-pin Molex power lead or splitter | 2 | 5 | 10 | The cards take power through their 4-pin Molex connector; there is no PCIe slot to feed them. |

Two backplanes use 2 of each card's 7 internal connectors, so a single card could serve all four
backplanes; the second card doubles the uplink bandwidth to the host and leaves room for more cards or
backplanes later.

The cards hang from their brackets in the Back Panel. The printed Card Edge Support (section 5) holds
their edge connectors, since there is no motherboard slot under them.

## 5. Printed parts and sealing

| Part | Qty | Volume each (cm³) | Status |
|---|---|---|---|
| Front Handle, left and right (ABS) | 1 each | 106.6 | To print |
| Backplane Tray Air Dam | 4 | 6.7 | To print |
| Card Edge Support | 1 | 75.9 | To print |
| Backplane Tray Connector (Wide) | 12 | 0.2 | To print |
| Backplane Tray Part A / Part B | 4 each | 36.6 / 36.2 | Already printed |
| Backplane Tray Connector | 8 | 0.1 | Already printed |

The parts still to print total about 320 cm³, roughly 335 g of ABS if printed solid: one 1 kg spool at
about $20. Add about $10 for brush strip or foam to close the fan-wall cable cut-outs. Blanks for empty
drive positions are not designed yet.

## 6. Fasteners

Counted from the holes in the models; buy assortments rather than exact counts.

| Fastener | About | Where |
|---|---|---|
| M5 x 10 screw with nut | 40 | 5.2 mm holes joining Chassis, Back Panel, fan wall, Drive Support Panel, Attic Baffles, Bezel brackets and handles |
| M5 screw with nut, longer | 8 | 5.5 mm Chassis floor holes under the backplane trays |
| M5 x 16 screw with nut and washer | 2 | Card Edge Support to the Chassis floor |
| M3 screw | 40 | Backplanes to trays (nine holes per tray pair) |
| Fan screws | 24 | Supplied with the fans |
| PSU screws, 6-32 | 4 | Supplied with the PSU |

Allowance: $25.

## 7. Rack mounting

The chassis is 430 mm wide and has no rack ears or rail mounts, so it needs a rack shelf or a pair of
L-rails rated for the loaded weight. That is roughly 45 kg with 48 drives, which rules out light
cantilever shelves. Allowance: $60.

## Already owned

| Item | Qty | Replacement value |
|---|---|---|
| Supermicro BPN-SAS3-826EL1 | 2 | Used asking prices run from about $45 to $100 each |
| Supermicro BPN-SAS3-826EL1-N4 | 2 | About $95 each used |

## Sources

- Noctua NF-A12x25 G2 pricing: <https://noctua.at/en/noctua-introduces-nf-a12x25-g2-next-generation-120mm-fan>
- Raw 0.080 in 5052-H32 sheet pricing: <https://speedymetals.com/p-1940-008-5052-h32-aluminum-sheet.aspx>
- SendCutSend pricing (per part, by upload): <https://sendcutsend.com/pricing/>
- AEC-82885T port layout and new pricing: <https://esaitech.com/products/adaptec-2283400-r-82885t-36-port-12gbps-sas-expander-card>,
  <https://store.ccnytech.com/products/microchip-expander-card-82885t-single-1161079>
- Used backplane listings: <https://www.ebay.de/itm/357022305067>, <https://www.ebay.de/itm/285857591043>,
  <https://pcserverandparts.com/supermicro-bpn-sas3-826el1-12-bay-lff-12gb-s-sas3-sata-server-expander-backplane/>

# Duckling v0.1: cost breakdown

Prices are typical AliExpress figures in USD, late 2026, including the usual free or cheap
"Choice" shipping. They move around, so treat them as a range, not a quote.

## 1. Per duck (what one robot's parts cost)

| Part | Qty | Low | High |
|------|-----|-----|------|
| ESP32-S3 SuperMini | 1 | 3.50 | 5.00 |
| MG90S metal-gear servo | 4 | 9.00 | 12.00 |
| SG90 servo (neck) | 1 | 1.20 | 1.80 |
| 0.96" SSD1306 OLED | 1 | 1.50 | 2.50 |
| MAX98357A amp | 1 | 1.20 | 2.00 |
| 28 mm speaker | 1 | 0.50 | 1.00 |
| 18650 protected cell (branded, not "9900 mAh" fakes) | 1 | 4.00 | 7.00 |
| 18650 holder | 1 | 0.30 | 0.60 |
| IP5306 USB-C charge/boost module | 1 | 1.00 | 2.00 |
| Slide switch + 1000 µF cap | 1 | 0.10 | 0.30 |
| Perfboard + headers | 1 | 0.50 | 1.00 |
| Wire / jumpers | – | 1.00 | 2.00 |
| Screws (4× M3, 6× M2) | – | 0.30 | 0.60 |
| **Electronics subtotal** | | **24.10** | **37.80** |
| PLA, ~141 g + ~10 g supports/purge @ $15–23/kg | | 2.30 | 3.50 |
| Electricity (~10 h at ~0.1 kW) | | 0.10 | 0.30 |
| **Total per duck** | | **≈ $27** | **≈ $42** |

**Typical: about $33 per duck.** The four leg servos and the battery are over
half of it.

### Filament by part (estimated from the CAD volumes)

| Part | g | Part | g |
|------|---|------|---|
| shell | 67 | head_shell | 15 |
| chassis | 15 | head_base | 9 |
| legs (×2) | 13 | feet (×2) | 13 |
| tray | 6 | beak | 3 |
| **Total** | **≈ 141 g** | **Print time** | **≈ 8–11 h on the A1** |

## 2. Your first duck (what you'll actually spend)

Many parts only come in packs, so the first build costs more and leaves spares:

| Item | You buy | ~Cost |
|------|---------|-------|
| MG90S | 5-pack (1 spare) | $12 |
| SG90 | 2-pack | $3 |
| ESP32-S3 SuperMini | 2-pack (1 spare) | $8 |
| OLED, amp, speaker, IP5306 | singles | $7 |
| 18650 + holder | 1 | $6 |
| Screw assortment (M2/M3) | box | $4 |
| Perfboard, headers, caps, switch | small packs | $4 |
| Silicone wire + jumper set | sets | $5 |
| PLA (yellow + orange) | you already have | – |
| **First-build outlay** | | **≈ $49** |

The second duck then costs about $25 more, because the spares are already
paid for.

## 3. As a business (rough unit economics)

At 100+ units, buying in bulk (servos in 50s, ESPs in 20s, cells by the carton)
typically cuts electronics by 25–35%.

| Product | Your cost | Suggested price | Gross margin |
|---------|-----------|-----------------|--------------|
| Digital: STLs + guide + firmware | ~$0 | $9–12 | ~100% (minus platform fee) |
| Electronics kit (customer prints the parts) | ~$18 parts + ~$6 bag/box/labour | $49–59 | ~50–60% before shipping |
| Complete kit incl. printed parts | ~$24 + ~$4 filament/print time + $6 | $79–89 | ~55% |
| Assembled duck | + 1–1.5 h labour | $129+ | depends on labour rate |

Before selling physical kits, budget for safety and labelling: shipping lithium cells
has carrier rules, and electronics sold in the UK, EU or US need the right
markings (UKCA/CE/FCC). Selling the kit without the battery is the easy first step.

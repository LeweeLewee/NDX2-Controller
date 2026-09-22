# Research and selection register

20 September 2026. Open work; candidate links do not mean selected or approved for wiring.

**D017 update, 21 September 2026:** Waveshare selected; Android ruled out. Close R11 selection and proceed with [HP-01](first-experiment.md). Electrical/mechanical validation gates remain open.

## Work order

| ID | Priority / BOM | Decision and current position | Evidence needed to close |
| --- | --- | --- | --- |
| R01 | First / HW-001,003,004 | Establish actual Waveshare board revision and power topology. Manufacturer guidance limits the recommended onboard cell to 2 Ah; external 5 V route now leads research. | Revision-matched schematic, supply paths, battery polarity, charger/load-sharing behaviour, backlight/touch power control and accessible wake interrupt |
| R02 | First / HW-001,009 | Validate touch wake with lowest viable standby draw. A fully unpowered board cannot detect touch. | Wake trials from each intended sleep state, total current and reconnect latency; external wake circuit only if justified |
| R03 | First / HW-002 | Choose battery energy and pack geometry after R01/R02 and usage profile. Protected assembled 1S pack is a candidate route, not a final chemistry/topology choice. | Wh and current ratings, charge compatibility, protection, dimensions, mass, sourcing/shipping and measured runtime |
| R04 | First / HW-003,004,017 | Decide onboard charging versus separate charger/converter. Avoid treating battery presence as proof of good power management. | Charge duration, thermal performance, low-load losses, peak-load stability and concurrent use/charging |
| R05 | Next / HW-005,008 | Low-battery indication, orderly shutdown and service disconnect | Accessible measurement/status, cutoff behaviour, leakage when off and recovery on charging |
| R06 | Next / HW-006,007 | Internal wiring and USB access | Correct mating connectors/polarity, current ratings, cable bend/strain relief, service access and no USB backfeeding |
| R07 | Next / HW-010–015 | Enclosure, battery restraint, feet and fasteners | Measured parts, initial layout, screen support, RF clearance, fit print, touch stability and finish sample |
| R08 | Later / HW-018 | Dock versus accessible connector | User convenience, contact alignment/polarity, contact rating and charging behaviour; no dock architecture chosen |
| R09 | Later / HW-016 | Extra weight | Actual assembled mass and stability; do not buy ballast just because weight is desirable |
| R10 | Software dependency / SYS-002,003 | Wired amplifier control verified D011; bridge host pending | Preserve bounded amplifier behavior; inspect Pi suitability and validate deployment/recovery |
| R11 | Closed selection / HW-001,019 | Waveshare selected; Android excluded by user (D017) | No comparative hardware test claimed; R01/R02 and HP-01 still pending |
| R12 | Next / HW-020 | Microphone/acoustic packaging | Candidate-specific capture, pin/bus budget if external, music interference, power and privacy controls |

## Initial power research

The [power component review](power-review.md) supersedes the initial onboard-first priority. R01–R06 remain open: documentary findings narrow the route but do not establish electrical compatibility or measured standby.

| Option | What is established | Selection position |
| --- | --- | --- |
| Waveshare onboard 1S battery input | Official documentation shows a battery connection switch and 3.7 V single-cell MX1.25 connection. Legacy wiki search evidence quotes 580 mA charging; verify against the actual schematic/revision before relying on it. | On hold for the large base pack: current user guide recommends ≤2,000 mAh; see power review |
| [Adafruit 353 protected 3.7 V 6600 mAh pack](https://www.adafruit.com/product/353) | Manufacturer describes a parallel assembled pack with over/under-voltage and over-current protection; represents roughly 24.4 Wh nominal energy. | Reference candidate within initial capacity range; not selected. Verify UK sourcing, dimensions, continuous current and connector adaptation |
| [Adafruit BQ24074 charger board, 4755](https://www.adafruit.com/product/4755) | Manufacturer documents load sharing and up to 1.5 A load draw. | External charger reference if onboard charging is unsuitable; not a regulated 5 V output or complete drop-in power system |
| [Pololu U3V70F5 5 V boost regulator, 2891](https://www.pololu.com/product/2891) | Manufacturer lists a true-shutdown option. | External converter reference only; likely more current capacity than needed. Compare low-load efficiency, quiescent current, size and cost before selecting |

Sources checked 20 September 2026: [Waveshare hardware](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B), [legacy wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B), [Adafruit battery catalogue](https://www.adafruit.com/category/889), and linked manufacturer product pages.

At a hypothetical 580 mA charge current, 5 Ah / 0.58 A = 8.6 h and 10 Ah / 0.58 A = 17.2 h before charge taper and active-load effects. These are arithmetic lower bounds, not promised charge times. This makes acceptable recharge duration a real selection criterion for a large pack.

Do not casually parallel separate packs or attach two chargers. Specify one compatible protected pack and one verified charging path. No resistor change to increase board charge current is selected.

## Display alternatives retained

HW-001 is selected (D017); Android HW-019 is excluded. The following older alternatives are historical fallback references only, not active selection work or purchases.

| Candidate | Reason to retain / reason not preferred now |
| --- | --- |
| [LILYGO T5 E-Paper S3 Pro Lite](https://lilygo.cc/products/t5-e-paper-s3-pro-lite) | 4.7-inch 960 x 540 grayscale touch e-paper; persistent image and illumination, but search/refresh interaction untested |
| [Good Display GDEQ0426T82-FT01C](https://www.good-display.com/product/938.html) | 4.26-inch 800 x 480 front-lit touch e-paper; custom integration route if visible standby becomes decisive |
| [SenseCAP Indicator D1](https://www.seeedstudio.com/SenseCAP-Indicator-D1-p-5643.html) | Integrated 480 x 480 LCD option; no penalty for lacking built-in battery; preferred Waveshare provides wider UI canvas |

Proportions are flexible, integrated batteries are not a ranking advantage, and headline MCU sleep figures do not establish whole-device standby.

## User-profile inputs needed before final sizing

- Desired number of standby weeks and reserve margin.
- Typical active browsing minutes/day; occasional long sessions.
- Whether LCD should remain visible through listening sessions or turn off after interaction.
- Comfortable screen timeout and acceptable wake/reconnect delay.
- Acceptable recharge duration and preference for cable versus dock.

These do not block documentation, software development or bench planning. Use explicitly labelled scenarios until agreed; do not turn assumptions into requirements.

## UK procurement and microphone follow-up — 21 September 2026

[Microphone review](microphone-review.md) proposes SPH0645LM4H with microSD-sniffer access to GPIO11/12/13; this is untested and would reserve the SD interface. [Full procurement coverage](prototype-shopping-list.md) records supplier baskets, stock, owned tools/wires and outstanding power/mechanical selection. Screen not ordered; user waiting stock and wants consolidated purchase. No additional accepted hardware selection or closed physical-validation gate is implied.

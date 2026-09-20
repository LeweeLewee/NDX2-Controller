# Hardware

Status: concept and parts planning; no physical build or purchases recorded.
Last reviewed: 20 September 2026.

The leading screen is the **Waveshare ESP32-S3-Touch-LCD-4.3B, standard version without case (SKU 27848)**. This is a preferred prototype candidate, not a tested or final production selection.

Current enclosure: **original 01 River Stone, stationary on the table**. See [dimensioned packaging and construction study](river-stone/README.md).

## Design baseline

- Compact coffee-table controller with a bespoke touch UI and a substantial, serviceable 3D-printed enclosure.
- Rectangular or square proportions are acceptable: screen quality and interaction take priority over aspect ratio.
- A separate large rechargeable battery lives low in the base. An included small battery adds no selection value.
- Weeks of standby is a target, not a measured specification. Screen-off standby is the working LCD direction; keeping now-playing continuously visible has a different energy budget.
- Touch wake remains a requirement to validate. Powering down the entire display board also disables its touch electronics unless a wake circuit remains powered.
- Native Naim TIDAL playback stays on the NDX 2. Controller and optional existing Pi carry commands and metadata only.

## Documents

| Document | Purpose |
| --- | --- |
| [Hardware design](design.md) | Electrical boundaries, physical layout and screen record |
| [Parts BOM](bom.md) | Authoritative part IDs, quantities, status, sourcing and costs |
| [Research and selection](research.md) | Open decisions, candidate routes and next actions |
| [Power component review](power-review.md) | Source findings, shortlist and compatibility gates |
| [Power budget and validation](validation.md) | Runtime assumptions and hardware acceptance checks |

## BOM management

Use one stable HW identifier per functional item. The BOM is the source of truth; do not maintain a second independently edited spreadsheet.

Selection states: **existing**, **preferred**, **candidate**, **research**, **design**, **optional**, **excluded**.
Track procurement separately: **not ordered**, **ordered**, **received**, **assembled**, or **existing / inventory unverified**. A preferred part is not a purchase instruction.

Before ordering, record exact manufacturer part number, board revision, supplier link, quantity, connector/polarity requirements, dated unit price and currency. Record shipping and taxes separately. Unknown cost is **TBD**, never zero. Included functions are not additional purchased parts. Alternatives are mutually exclusive, not additive.

After receiving a part, record actual revision and dimensions, paid cost, sanitized order reference and validation evidence. Keep private receipts/account details in ignored local/. Record substitutions and accepted choices in [decisions](../decisions.md), hardware results in [evidence](../evidence.md), and milestone changes in [roadmap](../roadmap.md).

Complete the software control-loop milestone before final component purchase and final enclosure CAD. Research and provisional layout work can proceed now.

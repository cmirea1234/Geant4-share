# V5 Current Status — 2026-06-23

## Complete

- Full V4.3 two-temperature, nine-bias map set processed.
- Six explicit independent damage states D0--D5 processed at every operating
  point: 108 rows total, with no missing or non-finite charge result.
- All converged TCAD points are retained in the CSV.
- Current-classified breakdown points are excluded from the plotted normal
  operating envelope.
- No K1 absolute charge, coefficient, or fitting target was used.

## Stable-envelope examples

| Temperature | Bias | State | Charge MPV [fC] |
|---:|---:|---|---:|
| 253 K | 550 V | D0 undamaged | 8.46646 |
| 253 K | 550 V | D3 medium | 2.83703 |
| 253 K | 550 V | D5 high | 1.40370 |
| 300 K | 490 V | D0 undamaged | 4.74108 |
| 300 K | 490 V | D3 medium | 1.84308 |
| 300 K | 490 V | D5 high | 1.01996 |

These values form an independent phenomenological sensitivity envelope. They
are not a self-consistent irradiated-TCAD solution or a calibrated fluence
prediction.

## Main outputs

- `outputs/independent_response_10k/v5_independent_response_surface.csv`
- `outputs/independent_response_10k/v5_charge_operating_envelope.png`
- `outputs/independent_response_10k/V5_INDEPENDENT_IRRADIATED_RESPONSE.md`


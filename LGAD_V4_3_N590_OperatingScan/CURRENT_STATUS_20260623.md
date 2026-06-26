# V4.3 Current Status — 2026-06-23

## Complete

- Sentaurus license service restored (`lmgrd` and `snpslmd`).
- All `253/300 K x 450..610 V` cases converged: 17 new runs and one reused
  validated `300 K, 590 V` run.
- All 18 TDR files were exported to Silicon field/alpha/mobility CSV maps.
- The maps were copied locally and processed with one common 10,000-event
  Geant4 MIP sample.
- No K1 charge point or fitted K1 coefficient was used.

## Operating-regime finding

The high-bias solutions are not all valid normal operating points. Final
Sentaurus anode conduction current gives the explicit classification in
`outputs/operating_scan_10k/operating_point_validity.csv`:

- stable: `|I| < 1 uA`,
- transition: `1 uA <= |I| < 1 mA`,
- breakdown: `|I| >= 1 mA`.

At 253 K, 450--550 V are stable and 570--610 V are breakdown solutions.
At 300 K, 450--490 V are stable, 510 V is transitional, and 530 V first
enters breakdown. The 570 V solution returns to a low-current nonlinear
branch and is marked transition/branch-sensitive rather than accepted as a
stable point. The 590 V preserved reference is a high-current breakdown
solution, despite being useful for reproducing the earlier code path.

## Main outputs

- `outputs/tcad_maps/`: 18 local TCAD maps
- `outputs/operating_scan_10k/v43_operating_scan_summary.csv`
- `outputs/operating_scan_10k/operating_point_validity.csv`
- `outputs/operating_scan_10k/v43_operating_curves.png`


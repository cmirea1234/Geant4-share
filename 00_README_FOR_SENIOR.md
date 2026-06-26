# LGAD TCAD final handoff

Date: 2026-06-26

## Short conclusion

Final working result is the V5 independent irradiated response envelope.

It uses the V4.3 n590 TCAD operating maps and explicit damage-state inputs.
It does not use a K1 absolute-charge fit target, fitted coefficient, or hidden
normalization. The irradiated result is a documented sensitivity envelope, not
a self-consistent irradiated TCAD prediction.

## Read first

1. `LGAD_V5_IndependentIrradiatedResponse/CURRENT_STATUS_20260623.md`
   - Current final status and representative charge values.
2. `LGAD_V5_IndependentIrradiatedResponse/outputs/independent_response_10k/V5_INDEPENDENT_IRRADIATED_RESPONSE.md`
   - Final model boundary and output list.
3. `LGAD_V5_IndependentIrradiatedResponse/outputs/independent_response_10k/v5_charge_operating_envelope.png`
   - Main plot.
4. `LGAD_V5_IndependentIrradiatedResponse/outputs/independent_response_10k/v5_independent_response_surface.csv`
   - Final response-surface table.

## Key V5 numbers

Stable-envelope examples:

| Temperature | Bias | State | Charge MPV [fC] |
|---:|---:|---|---:|
| 253 K | 550 V | D0 undamaged | 8.46646 |
| 253 K | 550 V | D3 medium | 2.83703 |
| 253 K | 550 V | D5 high | 1.40370 |
| 300 K | 490 V | D0 undamaged | 4.74108 |
| 300 K | 490 V | D3 medium | 1.84308 |
| 300 K | 490 V | D5 high | 1.01996 |

## Included folders

- `LGAD_V5_IndependentIrradiatedResponse/`
  - Final independent irradiated response surface.
  - Includes damage-state config, V5 output CSV, main envelope figure, and K1 literature audit notes.

- `LGAD_V4_3_N590_OperatingScan/`
  - n590 operating scan over `253/300 K x 450..610 V`.
  - Includes 18 TCAD-derived field/alpha/mobility CSV maps, operating validity table, and operating curve plot.

- `LGAD_V4_2_IrradiatedHybridResponse/`
  - Earlier irradiated hybrid sensitivity scan.
  - Kept as comparison/history; V5 is the cleaner independent response version.

- `LGAD_V4_1_PreIrradiationTransport/`
  - TCAD server input audit and recovered n590 590 V input snapshot.
  - Includes Sentaurus/DF-ISE files, exported transport CSV, and pre-irradiation transport outputs.

- `00_older_reference_pdfs/`
  - Older V0 validation report, included only as background.

## Important boundaries

- V4.3 used preserved n590 TCAD maps and one common Geant4 MIP event sample.
- V4.3 did not use a K1 charge point or fitted K1 coefficient.
- V5 excludes current-classified breakdown points from the plotted normal operating envelope.
- Irradiated scenarios are phenomenological response surfaces over explicit acceptor/trapping parameters.
- A predictive irradiated TCAD validation would still require self-consistent irradiated TCAD maps, trap/defect parameters, annealing/fluence treatment, and experimental charge-vs-bias uncertainties.

## Not included

`LGAD_V4_TCADBiasFieldResponse/` was not copied in full because it is about 2.8 GB and mostly an older/intermediate workspace. The compact V4.1/V4.3/V5 folders above contain the core final TCAD input audit, operating scan, and final response outputs.

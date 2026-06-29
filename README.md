# LGAD TCAD and Geant4 handoff

Date: 2026-06-26

## Current conclusion

This repository is a handoff package for the work completed so far. The final
working result currently included here is the V5 independent irradiated-response
envelope.

The existing V5 result combines preserved V4.3 n590 TCAD operating maps with
explicit damage-state inputs. It does not use a K1 absolute-charge fit target,
a fitted coefficient, or hidden normalization. The irradiated result should be
read as a documented sensitivity envelope, not as a self-consistent irradiated
TCAD prediction.

In practical terms: the present package shows how the Geant4 MIP energy-deposit
positions respond when coupled to TCAD-derived electric-field, avalanche, and
mobility maps. The next major step is to move the non-operating irradiation
damage assumptions into TCAD itself, rerun the damaged device, and then evaluate
how voltage behavior and sensor performance change.

## Recommended next step

The next work should start from the non-operating irradiation damage case,
before interpreting operation-under-damage response.

Recommended order:

1. Define the bias-off irradiation damage model.
   - Fluence and particle type.
   - Gain-layer acceptor removal or active-acceptor fraction.
   - Bulk trap or defect levels.
   - Leakage-generation model.
   - Annealing or temperature history, if available.

2. Apply that damage model inside TCAD.
   - Modify the gain-layer effective acceptor profile.
   - Add bulk radiation trap or defect parameters.
   - Keep the pre-irradiation n590 setup as the reference case.
   - Record all defect parameters in the TCAD command or parameter files.

3. Rerun TCAD bias and temperature scans for the damaged device.
   - Suggested starting grid: `253/300 K x 450..610 V`.
   - Track convergence, leakage current, and breakdown/transition/stable state.
   - Export field, potential, doping/space charge, mobility, and avalanche maps.

4. Compare pre-irradiation and damaged TCAD maps.
   - Gain-layer electric-field peak position and magnitude.
   - Depletion and space-charge changes.
   - Avalanche coefficient changes.
   - Leakage-current increase.
   - Breakdown or operating-voltage shift.

5. Only after that, reconnect to Geant4.
   - Use the damaged TCAD maps as the transport/gain input.
   - Recompute charge collection and gain response for the same MIP sample.
   - Compare charge MPV, median charge, drift diagnostics, and operating envelope.

This keeps the interpretation clean: first determine how irradiation changes the
sensor in TCAD, then ask how that changed sensor responds to Geant4 energy
deposition.

## What has already been completed

### V4.1 pre-irradiation transport

Folder: `LGAD_V4_1_PreIrradiationTransport/`

V4.1 converts the existing n590 TCAD field and Geant4 step energy deposition
into a position-dependent, pre-irradiation transport baseline. It includes the
TCAD server input audit, recovered n590 590 V input snapshot, exported transport
CSV, and pre-irradiation transport outputs.

Important boundary: no bulk radiation trap or defect model was found in the
recovered TCAD evidence. The n590 590 V map is therefore treated as a
pre-irradiation map.

### V4.2 irradiated hybrid response

Folder: `LGAD_V4_2_IrradiatedHybridResponse/`

V4.2 is an earlier documented irradiation sensitivity scan. It is kept as
comparison/history. V5 is the cleaner independent response version.

### V4.3 n590 operating scan

Folder: `LGAD_V4_3_N590_OperatingScan/`

V4.3 processes the n590 operating scan over `253/300 K x 450..610 V`. It
contains 18 TCAD-derived field/alpha/mobility CSV maps, an operating-validity
table, and an operating-curve plot.

Important boundary: V4.3 uses preserved n590 TCAD maps and one common Geant4 MIP
event sample. It does not use a K1 charge point or fitted K1 coefficient.

### V5 independent irradiated response

Folder: `LGAD_V5_IndependentIrradiatedResponse/`

V5 is the current final response-surface result in this package. It uses V4.3
maps and explicit damage-state parameters to build a sensitivity envelope.

Read first:

1. `LGAD_V5_IndependentIrradiatedResponse/CURRENT_STATUS_20260623.md`
2. `LGAD_V5_IndependentIrradiatedResponse/outputs/independent_response_10k/V5_INDEPENDENT_IRRADIATED_RESPONSE.md`
3. `LGAD_V5_IndependentIrradiatedResponse/outputs/independent_response_10k/v5_charge_operating_envelope.png`
4. `LGAD_V5_IndependentIrradiatedResponse/outputs/independent_response_10k/v5_independent_response_surface.csv`

Stable-envelope examples:

| Temperature | Bias | State | Charge MPV [fC] |
|---:|---:|---|---:|
| 253 K | 550 V | D0 undamaged | 8.46646 |
| 253 K | 550 V | D3 medium | 2.83703 |
| 253 K | 550 V | D5 high | 1.40370 |
| 300 K | 490 V | D0 undamaged | 4.74108 |
| 300 K | 490 V | D3 medium | 1.84308 |
| 300 K | 490 V | D5 high | 1.01996 |

## Important interpretation boundaries

- The current V5 irradiated scenarios are phenomenological response surfaces
over explicit acceptor/trapping parameters.
- The present result is not a self-consistent irradiated TCAD calculation.
- The current package does not yet prove where and how much the physical sensor
was damaged inside TCAD.
- A predictive irradiated TCAD validation still requires self-consistent damaged
TCAD maps, trap/defect parameters, fluence and annealing treatment, and
experimental charge-versus-bias uncertainties.
- The existing 2D TCAD to Geant4 coupling uses a 2D map projected into the
Geant4 energy-deposit geometry. For strong edge, guard-ring, JTE, pad-boundary,
or truly 3D effects, a full 3D TCAD treatment or a stricter mapping audit is
needed.

## Checks that should be added before senior review

These checks would make the handoff more reproducible and easier to defend:

1. Folding/mapping audit.
   - Report how many Geant4 steps fall outside the TCAD lateral window.
   - Compare the current mirror/fold mapping with a no-folding valid-window-only
     run.

2. TCAD export preservation audit.
   - Compare original TCAD center-line profiles with exported CSV profiles.
   - Check `E(x)`, `eAlpha(x)`, `hAlpha(x)`, potential, doping, and space charge.
   - Verify that integrating the electric field gives the expected bias scale.

3. Reproducibility note.
   - List the Python packages and Sentaurus environment used.
   - Identify which input files are required but not included in this compact
     repository.

## Not included

`LGAD_V4_TCADBiasFieldResponse/` was not copied in full because it is about
2.8 GB and mostly an older/intermediate workspace. The compact V4.1, V4.3, and
V5 folders above contain the core final TCAD input audit, operating scan, and
final response outputs.

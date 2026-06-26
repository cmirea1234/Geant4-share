# V4.1 Pre-Irradiation Transport Result

## Provenance

- TCAD state: treated as pre-irradiation
- TCAD temperature: `300 K`
- electrodes: anode `-590 V`, cathode `0 V`
- TCAD avalanche model: `Okuto`
- radiation traps/defects: not found in the supplied evidence

## Result

- events with energy deposition: `10,000`
- primary-charge MPV: `0.55514 fC`
- pre-irradiation full-collection MPV: `5.21084 fC`
- pre-irradiation full-collection median: `6.14575 fC`
- effective multiplication median: `9.76246`
- electron drift-time median: `278.796 ps`
- hole drift-time median: `3418.94 ps`

## Interpretation boundary

The integrated charge is a pre-irradiation, no-trapping baseline.
The drift times use a configurable saturated-velocity surrogate
because TCAD carrier velocities have not yet been exported.
This result is not a validation against the irradiated K1 EoL
measurement, which was taken near 253 K rather than 300 K.

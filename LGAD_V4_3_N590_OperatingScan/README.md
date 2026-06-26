# LGAD V4.3 n590 Operating Scan

V4.3 closes the independent pre-irradiation n590 branch by scanning operating
temperature and reverse bias without using or fitting K1 measurements.

## Scan grid

- temperature: `253 K`, `300 K`
- anode reverse bias: `-450, -470, -490, -510, -530, -550, -570, -590, -610 V`
- cathode: `0 V`
- device: preserved n590 pre-irradiation TCAD structure
- avalanche model: Okuto

Remote TCAD work must be performed only under:

```text
/home/partical/TCAD/OvO/LGAD_V4_3_N590_OperatingScan
```

The original n590 run and every directory outside `OvO` are read-only inputs.

## Intended outputs

- one final TDR and solver log per temperature/bias case,
- field, potential, avalanche, doping, and mobility CSV maps,
- solver convergence/status table,
- Geant4-coupled gain, charge MPV, and drift-time operating curves.


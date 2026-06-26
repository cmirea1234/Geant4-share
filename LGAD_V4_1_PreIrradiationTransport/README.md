# LGAD V4.1 Pre-Irradiation Transport

V4.1 converts the existing V4 n590 TCAD field and Geant4 step energy
deposition into a position-dependent, pre-irradiation transport baseline.

## Fixed provenance

- TCAD temperature: `300 K`
- anode: ramped to `-590 V`
- cathode: `0 V`
- avalanche model used by TCAD: `Okuto`
- high-field mobility option: `HighFieldSaturation(GradQuasiFermi)`
- recombination: `SRH(DopingDependence TempDependence)` and
  `Auger(WithGeneration)`
- radiation traps/defects: not present in the received evidence

The n590 map is therefore treated as a pre-irradiation map. Its predictions
must not be presented as validation of the irradiated K1 100% EoL charge.

## V4.1 model boundary

- Geant4 supplies the ionization-energy deposition positions.
- The n590 field supplies the position-dependent field and Okuto avalanche
  coefficients.
- Electron and hole drift times are integrated to their respective contacts.
- TCAD `eMobility/hMobility` are exported and multiplied by the local field
  magnitude for the excess-carrier drift-time estimate. The exported DC
  `eVelocity/hVelocity` are preserved for inspection but are not used as
  test-charge drift speeds because they include the solved quasi-Fermi/current
  state.
- Electron-path avalanche multiplication uses the TCAD
  `eAlphaAvalanche_cm-1` map.
- With no trapping and complete collection, integrated readout charge is
  `primary charge x electron multiplication`.
- A linear parallel-plate weighting potential is retained only to report the
  separate electron/hole shares of the unmultiplied primary signal. It is not
  used to reduce the total collected charge.

## Run

```bash
python3 analysis/build_preirradiation_transport.py \
  --step-hits ../LGAD_V4_TCADBiasFieldResponse/outputs/data/runs/\
lgad_v4_response_mip_120gev_10000_20260618/step_hits.csv
```

Use the 100k step file for the final statistics.

## 100k baseline result

| Quantity | Value |
|---|---:|
| primary-charge MPV | `0.552245 fC` |
| full-collection MPV | `5.3188 fC` |
| full-collection median | `6.14389 fC` |
| effective multiplication median | `9.76279` |
| electron active-region drift median | `476.256 ps` |
| hole active-region drift median | `301.429 ps` |
| electron full-contact drift median | `476.256 ps` |
| hole full-contact drift median | `14306.7 ps` |

The charge agrees with the earlier V4 electron-gain bracket by construction:
without trapping, every primary or avalanche electron-hole pair contributes
one elementary charge to the fully integrated readout signal. The V4.1
upgrade adds explicit transport times, corrects the interpretation of the
linear weighting diagnostic, and fixes the pre-irradiation provenance.

The final output is under:

```text
outputs/data/preirradiation_transport_tcad_mobility_100k/
```

The active-region times are the trapping-relevant diagnostics. Full-contact
times additionally include low-field, heavily doped neutral contact regions
and must not be used as the fast LGAD pulse time without a transient model.

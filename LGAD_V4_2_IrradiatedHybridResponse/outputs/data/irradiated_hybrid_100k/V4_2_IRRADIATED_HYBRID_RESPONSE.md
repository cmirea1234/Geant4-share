# V4.2 Irradiated Hybrid Sensitivity

## Fixed reference inputs

- proton fluence: `4.9e+14 p/cm2`
- neutron-equivalent fluence used for trapping: `2.5e+15 neq/cm2`
- proton acceptor-removal coefficient: `7.5e-16 cm2`
- active-acceptor survival: `0.692463`
- target measurement temperature: `253.15 K`
- avalanche-pair anchor x: `-49.2251 um`
- inherited TCAD field/mobility temperature: `300 K`

## Scenario results

| Scenario | gain log scale | beta e | beta h | MPV [fC] | median [fC] |
|---|---:|---:|---:|---:|---:|
| preirradiation_reference | 1 | 0 | 0 | 5.3188 | 6.14389 |
| acceptor_sqrt_no_trapping | 0.8321 | 0 | 0 | 3.62215 | 4.18801 |
| acceptor_direct_no_trapping | 0.6925 | 0 | 0 | 2.63112 | 3.04535 |
| hybrid_sqrt_nominal_trapping | 0.8321 | 5e-16 | 7e-16 | 2.28297 | 2.64054 |
| hybrid_direct_nominal_trapping | 0.6925 | 5e-16 | 7e-16 | 1.67358 | 1.93894 |
| hybrid_direct_strong_trapping | 0.6925 | 7e-16 | 1e-15 | 1.4181 | 1.64622 |

## Interpretation boundary

`gain_log_scale` is a phenomenological bracket applied as
`M_after = exp(scale * ln(M_before))`; it is not a self-consistent
Poisson/avalanche solution. Trapping uses active-region drift and
linear-weighting Ramo induction with exponential carrier loss.
The beta values are sensitivity assumptions, not calibrated values
for this device. The 300 K field/mobility map has not been rerun at
the 253 K measurement temperature. Therefore none of the irradiated
scenarios is a predictive result or a fit to the thesis charge point.

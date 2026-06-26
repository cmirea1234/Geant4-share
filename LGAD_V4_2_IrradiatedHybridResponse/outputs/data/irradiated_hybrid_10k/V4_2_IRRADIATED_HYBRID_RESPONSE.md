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
| preirradiation_reference | 1 | 0 | 0 | 5.21084 | 6.14575 |
| acceptor_sqrt_no_trapping | 0.8321 | 0 | 0 | 3.5488 | 4.18926 |
| acceptor_direct_no_trapping | 0.6925 | 0 | 0 | 2.57799 | 3.04692 |
| hybrid_sqrt_nominal_trapping | 0.8321 | 5e-16 | 7e-16 | 2.23218 | 2.64273 |
| hybrid_direct_nominal_trapping | 0.6925 | 5e-16 | 7e-16 | 1.63379 | 1.94057 |
| hybrid_direct_strong_trapping | 0.6925 | 7e-16 | 1e-15 | 1.38261 | 1.64717 |

## Interpretation boundary

`gain_log_scale` is a phenomenological bracket applied as
`M_after = exp(scale * ln(M_before))`; it is not a self-consistent
Poisson/avalanche solution. Trapping uses active-region drift and
linear-weighting Ramo induction with exponential carrier loss.
The beta values are sensitivity assumptions, not calibrated values
for this device. The 300 K field/mobility map has not been rerun at
the 253 K measurement temperature. Therefore none of the irradiated
scenarios is a predictive result or a fit to the thesis charge point.

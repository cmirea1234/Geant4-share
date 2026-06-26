# LGAD V4.2 Irradiated Hybrid Response

V4.2 is a documented irradiation sensitivity model built on the locally
preserved V4.1 pre-irradiation TCAD baseline. It does not claim to replace an
irradiated TCAD field solution.

The model separates:

- gain-layer acceptor-removal sensitivity,
- electron and hole trapping during active-region drift,
- pre-irradiation TCAD avalanche multiplication,
- primary and avalanche-pair Shockley-Ramo contributions.

See the generated report under `outputs/data/` for scenario definitions and
interpretation limits.

## 100k sensitivity result

| Scenario | Charge MPV [fC] |
|---|---:|
| pre-irradiation reference | `5.319` |
| acceptor direct, no trapping | `2.631` |
| sqrt-acceptor response + nominal trapping | `2.283` |
| direct acceptor response + nominal trapping | `1.674` |
| direct acceptor response + strong trapping | `1.418` |

These values are deliberately not tuned to the thesis `6.3 fC` point. Their
failure to reproduce that point shows that direct acceptor-survival scaling
of the pre-irradiation multiplication is not an adequate predictive field
model, or that the preserved n590 device is not the measured K1 device, or
both. A self-consistent irradiated TCAD field/avalanche solution is required
to distinguish those explanations.

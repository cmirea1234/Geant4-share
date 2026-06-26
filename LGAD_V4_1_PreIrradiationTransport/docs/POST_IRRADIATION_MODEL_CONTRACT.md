# Post-Irradiation Model Contract

The V4.1 pre-irradiation transport result is the baseline for a later
irradiated-response model. Two distinct model levels must not be mixed.

## Level 1: hybrid sensitivity model

This can be built locally without another TCAD run:

1. apply gain-layer acceptor survival,
2. scan an assumed field/gain reduction,
3. calculate electron and hole trapping from the V4.1 drift paths,
4. compare the response across parameter ranges.

For the thesis K1 100% EoL proton campaign, the available reference inputs
are:

- proton fluence: approximately `4.9e14 p/cm2`,
- corresponding neutron-equivalent fluence: approximately
  `2.5e15 neq/cm2`,
- proton acceptor-removal coefficient: approximately `7.5e-16 cm2`,
- acceptor-survival reference: `exp(-c_p * Phi_p) ~= 0.692`,
- annealing: `80 min at 60 degC`,
- test-beam temperature: approximately `253 K` (`-20 degC`).

The proton coefficient must be multiplied by proton fluence, not by the
neutron-equivalent fluence. Electron and hole trapping coefficients still
need an explicit source and temperature scaling before numerical trapping is
enabled.

This level is a sensitivity study. Scaling the acceptor density does not by
itself produce a self-consistent irradiated electric field.

## Level 2: predictive irradiated model

A predictive model must recompute the electrostatics and avalanche response
after acceptor removal and radiation defects. The preferred input is a new
irradiated TCAD solution containing:

```text
x, y, potential, Ex, Ey, eAlphaAvalanche, hAlphaAvalanche,
donor concentration, active acceptor concentration
```

The run metadata must include fluence, particle type, annealing, temperature,
trap/defect model, electrodes, and bias. A separate weighting-potential map is
required for a segmented/JTE waveform model. For the current central n590
rectangle, both contacts span the full lateral width, so the linear
parallel-plate weighting potential is the corresponding Laplace solution.
TCAD mobility/velocity quantities have now been exported; the effective
mobility map is used for drift-time estimates.

If TCAD cannot be rerun, a local Poisson/transport approximation can be
implemented, but it must remain labeled as an approximate V5 model and be
validated against at least two measured bias points. A single `6.3 fC` point
cannot independently constrain acceptor removal, trapping, field change, and
avalanche multiplication.

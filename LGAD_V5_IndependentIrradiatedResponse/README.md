# LGAD V5 Independent Irradiated Response

V5 is an independent irradiation-response surface built on V4.3 n590
temperature/bias maps. It does not use K1 absolute charge values and does not
fit any external measurement.

Damage inputs are explicit and editable in:

```text
config/independent_damage_states.csv
```

Each state separately specifies:

- neutron-equivalent fluence,
- active gain-layer acceptor fraction,
- electron trapping coefficient,
- hole trapping coefficient.

The current gain transformation is a phenomenological response bracket:

```text
M_damage = exp(active_acceptor_fraction * ln(M_preirradiation))
```

It is not a self-consistent irradiated Poisson/avalanche TCAD solution. V5 is
therefore an independent sensitivity/operating-envelope model, not a
process-calibrated sensor prediction.

The full response CSV retains every converged TCAD point. The plotted operating
envelope excludes points classified as breakdown from the final TCAD anode
conduction current. The current classification is supplied explicitly with
`--operating-status`; it is not inferred from K1 data.

The separate K1 literature and local-source audit is stored in
`docs/k1_literature_review_20260623/`. It is used only for a normalized,
trend-level comparison and does not change the V5 damage-state parameters.

# V5 Independent Irradiated n590 Response

No K1 absolute charge, coefficient, or fitting target is used.
Damage-state values come only from the explicit configuration CSV.

## Model boundary

The operating field/alpha/mobility maps come from V4.3 TCAD.
All points remain in the CSV, while breakdown points are excluded
from the plotted operating envelope using the supplied current-based
operating-status table.
Irradiation is a response surface over explicit acceptor and trapping
parameters. The gain transformation is phenomenological and does not
replace a self-consistent irradiated TCAD solution.

## Output

- `v5_independent_response_surface.csv`
- `v5_charge_operating_envelope.png`

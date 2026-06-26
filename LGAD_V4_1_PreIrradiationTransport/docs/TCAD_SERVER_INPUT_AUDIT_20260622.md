# TCAD Server Input Audit — 2026-06-22

## Access boundary

Remote inspection was read-only outside `/home/partical/TCAD/OvO`.
All created files and preserved copies were written only under `OvO`.

## Confirmed simulation provenance

- Sentaurus generation: `W-2024.09-SP1`
- device temperature: `300 K`
- anode: full-width contact at `x=1..2 um`, ramped to `-590 V`
- cathode: full-width contact at `x=-50..-51 um`, held at `0 V`
- silicon TCAD domain: approximately `x=-50..1 um`, lateral `-70..70 um`
- mobility: `DopingDependence`,
  `HighFieldSaturation(GradQuasiFermi)`, `Enormal(Lombardi)`
- avalanche: `Okuto`
- recombination: `SRH(DopingDependence TempDependence)` and
  `Auger(WithGeneration)`
- band-gap narrowing: `OldSlotboom`
- explicit interface charge: `FixedCharge Conc=1e10` at `Silicon/Oxide`
- no bulk radiation-damage trap/defect model was found
- no custom parameter file is named in `pp590_des.cmd`; the run therefore
  appears to use the installed Sentaurus defaults for the selected models

The interface fixed charge is a device/interface condition. It is not an
irradiation fluence or a bulk radiation-damage trapping model.

## Data recovered from the existing result

The existing DF-ISE export already contained, for all 1,836 Silicon vertices:

- `eMobility`, `hMobility`
- `eVelocity`, `hVelocity`
- carrier densities and current densities
- electric field and potential
- donor/acceptor/space charge
- SRH/Auger/avalanche generation
- electron/hole ionization integrals and avalanche coefficients
- quasi-Fermi gradients and parallel/normal fields

The mobility/velocity fields were exported without rerunning TCAD:

```text
inputs/tcad_n590_590V/n590_tcad_silicon_transport_590V.csv
```

The V4.1 timing calculation uses the effective TCAD mobility multiplied by
the local field. The exported DC `eVelocity/hVelocity` are not directly used
as test-charge drift speeds because the DC values include the solved
quasi-Fermi/current state and approach equilibrium values in contact regions.

## Weighting field status

No separate weighting-potential result was found. For this particular central
n590 model, both electrodes span the full lateral width, so the linear
parallel-plate weighting potential is the corresponding Laplace solution.
A separate 2D weighting solve becomes necessary when pad segmentation,
guard-ring, JTE, or partial electrodes are included.

## What is now sufficient

The recovered inputs are sufficient for the current pre-irradiation V4.1
baseline:

- primary charge from Geant4 energy deposition,
- position-dependent Okuto avalanche multiplication,
- 300 K mobility-based active-region drift-time diagnostics,
- full-collection integrated charge under the no-trapping assumption.

## Still missing for an irradiated predictive model

- an irradiated K1 device definition or active-acceptor profile,
- bulk radiation trap/defect parameters,
- fluence and annealing applied inside the TCAD device model,
- self-consistent irradiated field and avalanche maps at `253 K`,
- preferably several bias points from `450..610 V`,
- experimental charge-versus-bias values and uncertainties for validation.

Without these items, an irradiated model can be built only as a documented
hybrid sensitivity scan, not as a predictive TCAD validation.


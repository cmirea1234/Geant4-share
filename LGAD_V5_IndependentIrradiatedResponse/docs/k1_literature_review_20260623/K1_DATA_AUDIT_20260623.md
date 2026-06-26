# UFSD-K1 Data Audit — 2026-06-23

## Sources checked

### Local primary source

- `/home/OvO/Geant4_Project/PDF/20245032(안근필).pdf`
- Geunpil An, *Performance Analysis of LGAD Sensors for the CMS MIP
  Timing Detector at the HL-LHC*, M.S. thesis, Gangneung-Wonju
  National University, degree date February 2026.
- SHA-256:
  `2c2671995ee620a41ae2a36af9e3621a81f0215db442c117fc4bf68785ee251c`

### Internet records and supporting primary literature

- Official thesis record, UCI `I804:42001-000000012336`:
  https://dcollection.gwnu.ac.kr/srch/srchDetail/000000012336
- An et al., *Irradiation and test beam studies of LGAD sensors for the
  CMS MTD*, New Physics: Sae Mulli 76 (2026) 282--293,
  DOI `10.3938/NPSM.76.282`:
  https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003330837
- Jin et al., *Experimental Study of Acceptor Removal in UFSD*, NIM A
  983 (2020) 164611, DOI `10.1016/j.nima.2020.164611`:
  https://cds.cern.ch/record/2718058
- Kraus et al., *Proton Energy Dependence of Radiation Induced Low Gain
  Avalanche Detector Degradation*, arXiv:2602.01800:
  https://arxiv.org/abs/2602.01800
- CMS MTD Technical Design Report, CMS-TDR-020:
  https://cds.cern.ch/record/2667167

The online thesis record confirms the title, author, institution, degree date,
scope, and the 15/13.5 MeV KOMAC plus CERN SPS H6 workflow. The 2026 journal
article independently confirms the 15 MeV irradiation and the failure of the
irradiated collected charge to meet the required threshold.

## K1 device and test conditions

- Manufacturer/branch: FBK UFSD-K1.
- Gain layer: deep boron gain layer with carbon co-implantation.
- Counter implant: single N+; K2 uses the double-N+ variant.
- Irradiation used for the measured 100% EoL point: 15 MeV protons at
  KOMAC, `4.9e14 p/cm2`.
- Thesis conversion: extrapolated `c_p(15 MeV) = 7.5e-16 cm2`, neutron
  reference `c_n = 1.5e-16 cm2`, hence `k = 5` and
  `2.5e15 neq/cm2`.
- Annealing: 80 minutes at 60 degC.
- Beam test: 120 GeV hadron beam at CERN SPS H6.
- K1 bias scan: approximately 450--610 V.
- Cold-box temperature: -20 degC (253 K).

The thesis explicitly states that the 15 MeV coefficient and `k=5` are
extrapolated BL+1C process estimates, not a direct 15 MeV measurement. Recent
proton-energy studies also find that NIEL conversion does not fully remove the
energy dependence of LGAD degradation. The `neq` value must therefore retain
this systematic caveat.

## Measured K1 results

| State | Bias | Fluence | Collected charge | Timing | Interpretation |
|---|---:|---:|---:|---:|---|
| Before irradiation | ~230 V | 0 | ~25 fC | not tabulated in Table 5-2 | optimum point |
| 100% EoL | 590 V | 2.5e15 neq/cm2 | 6.3 +/- 0.1 fC | 34.3 +/- 1.2 ps | below 8 fC post-EoL requirement |
| 200% EoL | 525 V | 5.0e15 neq/cm2 | not measurable | not measurable | signal not separated from noise |

The before/after charge ratio at the respective optimum voltages is about
`6.3/25 = 0.252`. It is not a same-bias ratio. Table 5-2 reports the K1
breakdown voltage changing from about 280 V before irradiation to greater than
600 V after irradiation.

Figure 5-4 gives an approximate 100% EoL charge scan of 3.8, 4.3, 4.5, 4.9,
and 6.3 fC at 450, 500, 525, 550, and 590 V. Only the 590 V value is also
reported numerically with an uncertainty; the other points in
`k1_charge_vs_bias_digitized_approx.csv` are visual digitizations and must not
be presented as exact table values.

## Trend-only comparison with V5

V5 D5 uses `2.5e15 neq/cm2`, matching the thesis nominal 100% EoL equivalent
fluence, but its active-acceptor fraction and trapping coefficients are
independent benchmark assumptions rather than a K1 fit.

At 253 K over V5's stable n590 domain:

- `D5/D0 = 0.223` at 450 V,
- decreases continuously to `0.166` at 550 V.

The measured K1 optimum-point ratio is approximately `0.252`. Both show a
strong charge reduction at the nominal EoL fluence, and the V5 normalized loss
is of the same order but somewhat stronger. This is qualitative agreement
only: the devices, gain-layer processes, safe voltage ranges, and comparison
biases are different.

In particular, the n590 TCAD solutions at 253 K and 570--610 V are classified
as breakdown solutions. The K1 post-irradiation device instead has a reported
breakdown voltage above 600 V. Therefore the K1 590 V point must not be
compared directly with the n590 590 V absolute charge.

## Files

- `k1_reference_points.csv`: tabulated thesis values.
- `k1_charge_vs_bias_digitized_approx.csv`: approximate Figure 5-4 points.
- `k1_v5_normalized_trend_comparison.csv`: K1 and V5 normalized ratios.
- `figures/thesis_page_63_figures_5_4_5_5.jpg`: local source-page rendering.

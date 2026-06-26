#!/usr/bin/env python3
"""Build an explicitly non-predictive irradiated LGAD sensitivity scan."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


PROJECT_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT_DIR.parent
V4_DIR = WORKSPACE / "LGAD_V4_TCADBiasFieldResponse"
V41_DIR = WORKSPACE / "LGAD_V4_1_PreIrradiationTransport"
sys.path.insert(0, str(V4_DIR / "analysis"))
sys.path.insert(0, str(V41_DIR / "analysis"))

from build_2d_mirrored_gain_response import (  # noqa: E402
    FC_PER_MEV,
    MAP_PATH,
    read_rows,
    summarize,
    write_csv,
)
from build_preirradiation_transport import (  # noqa: E402
    DEFAULT_TRANSPORT_MAP,
    TransportMap,
    readout_weighting_potential,
)


DEFAULT_OUTPUT_DIR = PROJECT_DIR / "outputs/data/irradiated_hybrid_100k"
PROTON_FLUENCE_CM2 = 4.9e14
NEQ_FLUENCE_CM2 = 2.5e15
PROTON_ACCEPTOR_REMOVAL_CM2 = 7.5e-16
TARGET_MEASUREMENT_TEMPERATURE_K = 253.15


def induction_survival_factor(
    drift_time_ps: float, beta_cm2_per_ns: float, fluence_cm2: float
) -> float:
    """Ramo induction retained with exponential trapping along a linear path."""
    if drift_time_ps <= 0.0 or beta_cm2_per_ns <= 0.0 or fluence_cm2 <= 0.0:
        return 1.0
    drift_ns = drift_time_ps * 1.0e-3
    lifetime_ns = 1.0 / (beta_cm2_per_ns * fluence_cm2)
    ratio = drift_ns / lifetime_ns
    if ratio < 1.0e-8:
        return 1.0
    return -math.expm1(-ratio) / ratio


def build_scenarios(acceptor_survival: float) -> list[dict[str, float | str]]:
    sqrt_survival = math.sqrt(acceptor_survival)
    return [
        {
            "name": "preirradiation_reference",
            "gain_log_scale": 1.0,
            "beta_e_cm2_per_ns": 0.0,
            "beta_h_cm2_per_ns": 0.0,
        },
        {
            "name": "acceptor_sqrt_no_trapping",
            "gain_log_scale": sqrt_survival,
            "beta_e_cm2_per_ns": 0.0,
            "beta_h_cm2_per_ns": 0.0,
        },
        {
            "name": "acceptor_direct_no_trapping",
            "gain_log_scale": acceptor_survival,
            "beta_e_cm2_per_ns": 0.0,
            "beta_h_cm2_per_ns": 0.0,
        },
        {
            "name": "hybrid_sqrt_nominal_trapping",
            "gain_log_scale": sqrt_survival,
            "beta_e_cm2_per_ns": 5.0e-16,
            "beta_h_cm2_per_ns": 7.0e-16,
        },
        {
            "name": "hybrid_direct_nominal_trapping",
            "gain_log_scale": acceptor_survival,
            "beta_e_cm2_per_ns": 5.0e-16,
            "beta_h_cm2_per_ns": 7.0e-16,
        },
        {
            "name": "hybrid_direct_strong_trapping",
            "gain_log_scale": acceptor_survival,
            "beta_e_cm2_per_ns": 7.0e-16,
            "beta_h_cm2_per_ns": 1.0e-15,
        },
    ]


def gain_anchor_x_um(transport: TransportMap) -> float:
    center = int(np.argmin(np.abs(transport.depths)))
    weights = np.maximum(transport.e_alpha[center], 0.0)
    if float(np.sum(weights)) <= 0.0:
        return float(transport.x_um[0])
    return float(np.average(transport.x_um, weights=weights))


def process_step_hits(
    step_path: Path,
    transport: TransportMap,
    scenarios: list[dict[str, float | str]],
) -> tuple[list[dict[str, float | int]], dict[str, dict[str, float]], float]:
    event_primary: defaultdict[int, float] = defaultdict(float)
    event_charge = {
        str(scenario["name"]): defaultdict(float) for scenario in scenarios
    }
    anchor_x_um = gain_anchor_x_um(transport)
    step_count = 0
    used_steps = 0

    with step_path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            step_count += 1
            if row.get("volume_name") != "TcadSiliconSensor":
                continue
            edep_mev = float(row["edep_MeV"])
            if edep_mev <= 0.0:
                continue

            lateral_um = 0.5 * (float(row["pre_x_um"]) + float(row["post_x_um"]))
            g4_z_um = 0.5 * (float(row["pre_z_um"]) + float(row["post_z_um"]))
            tcad_x_um = -g4_z_um - 24.5
            (
                pre_gain,
                _hole_gain,
                _field,
                _folded,
                electron_ps,
                hole_ps,
                _electron_full_ps,
                _hole_full_ps,
            ) = transport.transport_at(tcad_x_um, lateral_um)
            (
                _anchor_gain,
                _anchor_hole_gain,
                _anchor_field,
                _anchor_folded,
                anchor_electron_ps,
                anchor_hole_ps,
                _anchor_e_full_ps,
                _anchor_h_full_ps,
            ) = transport.transport_at(anchor_x_um, lateral_um)

            phi = readout_weighting_potential(
                tcad_x_um, transport.x_low, transport.x_high
            )
            anchor_phi = readout_weighting_potential(
                anchor_x_um, transport.x_low, transport.x_high
            )
            primary_fc = edep_mev * FC_PER_MEV
            event_id = int(row["event_id"])
            event_primary[event_id] += primary_fc

            for scenario in scenarios:
                name = str(scenario["name"])
                beta_e = float(scenario["beta_e_cm2_per_ns"])
                beta_h = float(scenario["beta_h_cm2_per_ns"])
                gain_log_scale = float(scenario["gain_log_scale"])
                damaged_gain = math.exp(gain_log_scale * math.log(max(pre_gain, 1.0)))

                primary_e = (1.0 - phi) * induction_survival_factor(
                    electron_ps, beta_e, NEQ_FLUENCE_CM2
                )
                primary_h = phi * induction_survival_factor(
                    hole_ps, beta_h, NEQ_FLUENCE_CM2
                )
                avalanche_e = (1.0 - anchor_phi) * induction_survival_factor(
                    anchor_electron_ps, beta_e, NEQ_FLUENCE_CM2
                )
                avalanche_h = anchor_phi * induction_survival_factor(
                    anchor_hole_ps, beta_h, NEQ_FLUENCE_CM2
                )
                response = primary_e + primary_h + (damaged_gain - 1.0) * (
                    avalanche_e + avalanche_h
                )
                event_charge[name][event_id] += primary_fc * response
            used_steps += 1

    event_rows: list[dict[str, float | int]] = []
    for event_id in sorted(event_primary):
        output: dict[str, float | int] = {
            "event_id": event_id,
            "primary_charge_fC": event_primary[event_id],
        }
        for scenario in scenarios:
            name = str(scenario["name"])
            output[f"{name}_charge_fC"] = event_charge[name][event_id]
        event_rows.append(output)

    summary: dict[str, dict[str, float]] = {
        "run": {
            "input_step_rows": float(step_count),
            "used_edep_steps": float(used_steps),
            "events_with_edep": float(len(event_rows)),
        }
    }
    primary = np.array([row["primary_charge_fC"] for row in event_rows])
    summary["primary"] = summarize(primary, "charge_fC")
    for scenario in scenarios:
        name = str(scenario["name"])
        values = np.array([row[f"{name}_charge_fC"] for row in event_rows])
        summary[name] = summarize(values, "charge_fC")
    return event_rows, summary, anchor_x_um


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step-hits", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--transport-map", type=Path, default=DEFAULT_TRANSPORT_MAP)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    transport = TransportMap(
        read_rows(MAP_PATH),
        1350.0,
        480.0,
        1.07e7,
        8.37e6,
        read_rows(args.transport_map),
        1.0e3,
    )
    acceptor_survival = math.exp(
        -PROTON_ACCEPTOR_REMOVAL_CM2 * PROTON_FLUENCE_CM2
    )
    scenarios = build_scenarios(acceptor_survival)
    event_rows, summary, anchor_x_um = process_step_hits(
        args.step_hits, transport, scenarios
    )
    write_csv(args.output_dir / "irradiated_hybrid_events.csv", event_rows)

    scenario_rows = []
    for scenario in scenarios:
        name = str(scenario["name"])
        scenario_rows.append(
            {
                **scenario,
                "charge_MPV_fC": summary[name]["charge_fC_mpv_hist"],
                "charge_median_fC": summary[name]["charge_fC_median"],
                "status": "sensitivity_scenario_not_predictive_tcad",
            }
        )
    write_csv(args.output_dir / "irradiated_hybrid_scenarios.csv", scenario_rows)

    selected = [
        "preirradiation_reference",
        "acceptor_direct_no_trapping",
        "hybrid_sqrt_nominal_trapping",
        "hybrid_direct_strong_trapping",
    ]
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    all_values = {
        name: np.array([row[f"{name}_charge_fC"] for row in event_rows])
        for name in selected
    }
    upper = max(float(np.percentile(values, 99.0)) for values in all_values.values())
    bins = np.linspace(0.0, max(upper, 1.0), 90)
    for name, values in all_values.items():
        ax.hist(values, bins=bins, histtype="step", label=name)
    ax.set_xlabel("Integrated charge [fC]")
    ax.set_ylabel("Events")
    ax.set_title("V4.2 irradiated hybrid sensitivity scan")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(args.output_dir / "irradiated_hybrid_charge_scan.png", dpi=180)
    plt.close(fig)

    lines = [
        "# V4.2 Irradiated Hybrid Sensitivity",
        "",
        "## Fixed reference inputs",
        "",
        f"- proton fluence: `{PROTON_FLUENCE_CM2:.6g} p/cm2`",
        f"- neutron-equivalent fluence used for trapping: `{NEQ_FLUENCE_CM2:.6g} neq/cm2`",
        f"- proton acceptor-removal coefficient: `{PROTON_ACCEPTOR_REMOVAL_CM2:.6g} cm2`",
        f"- active-acceptor survival: `{acceptor_survival:.6g}`",
        f"- target measurement temperature: `{TARGET_MEASUREMENT_TEMPERATURE_K:.6g} K`",
        f"- avalanche-pair anchor x: `{anchor_x_um:.6g} um`",
        "- inherited TCAD field/mobility temperature: `300 K`",
        "",
        "## Scenario results",
        "",
        "| Scenario | gain log scale | beta e | beta h | MPV [fC] | median [fC] |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in scenario_rows:
        lines.append(
            f"| {row['name']} | {float(row['gain_log_scale']):.4g} | "
            f"{float(row['beta_e_cm2_per_ns']):.3g} | "
            f"{float(row['beta_h_cm2_per_ns']):.3g} | "
            f"{float(row['charge_MPV_fC']):.6g} | "
            f"{float(row['charge_median_fC']):.6g} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "`gain_log_scale` is a phenomenological bracket applied as",
            "`M_after = exp(scale * ln(M_before))`; it is not a self-consistent",
            "Poisson/avalanche solution. Trapping uses active-region drift and",
            "linear-weighting Ramo induction with exponential carrier loss.",
            "The beta values are sensitivity assumptions, not calibrated values",
            "for this device. The 300 K field/mobility map has not been rerun at",
            "the 253 K measurement temperature. Therefore none of the irradiated",
            "scenarios is a predictive result or a fit to the thesis charge point.",
            "",
        ]
    )
    report = "\n".join(lines)
    (args.output_dir / "V4_2_IRRADIATED_HYBRID_RESPONSE.md").write_text(
        report, encoding="utf-8"
    )
    print(report)


if __name__ == "__main__":
    main()

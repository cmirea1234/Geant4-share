#!/usr/bin/env python3
"""Build the independent V5 n590 irradiation-response surface."""

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
V41_DIR = WORKSPACE / "LGAD_V4_1_PreIrradiationTransport"
V4_DIR = WORKSPACE / "LGAD_V4_TCADBiasFieldResponse"
sys.path.insert(0, str(V41_DIR / "analysis"))
sys.path.insert(0, str(V4_DIR / "analysis"))

from build_preirradiation_transport import (  # noqa: E402
    TransportMap,
    readout_weighting_potential,
)
from build_2d_mirrored_gain_response import (  # noqa: E402
    FC_PER_MEV,
    histogram_mpv,
)


DEFAULT_STATES = PROJECT_DIR / "config/independent_damage_states.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def induction_factor(time_ps: float, beta: float, fluence: float) -> float:
    if time_ps <= 0.0 or beta <= 0.0 or fluence <= 0.0:
        return 1.0
    time_ns = time_ps * 1.0e-3
    lifetime_ns = 1.0 / (beta * fluence)
    ratio = time_ns / lifetime_ns
    if ratio < 1.0e-8:
        return 1.0
    return -math.expm1(-ratio) / ratio


def gain_anchor_x_um(transport: TransportMap) -> float:
    center = int(np.argmin(np.abs(transport.depths)))
    weights = np.maximum(transport.e_alpha[center], 0.0)
    if float(np.sum(weights)) <= 0.0:
        return float(transport.x_um[0])
    return float(np.average(transport.x_um, weights=weights))


def process_map(
    map_path: Path,
    step_path: Path,
    states: list[dict[str, str]],
    operating_points: dict[tuple[float, float], dict[str, str]],
) -> list[dict[str, float | int | str]]:
    tcad_rows = read_rows(map_path)
    temperature = float(tcad_rows[0]["temperature_K"])
    bias = abs(float(tcad_rows[0]["bias_V"]))
    operating = operating_points.get((temperature, bias), {})
    transport = TransportMap(
        tcad_rows, 1350.0, 480.0, 1.07e7, 8.37e6, tcad_rows, 1.0e3
    )
    anchor_x = gain_anchor_x_um(transport)
    event_charge = {
        state["state"]: defaultdict(float) for state in states
    }

    with step_path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            if row.get("volume_name") != "TcadSiliconSensor":
                continue
            edep_mev = float(row["edep_MeV"])
            if edep_mev <= 0.0:
                continue
            lateral_um = 0.5 * (float(row["pre_x_um"]) + float(row["post_x_um"]))
            g4_z_um = 0.5 * (float(row["pre_z_um"]) + float(row["post_z_um"]))
            tcad_x_um = -g4_z_um - 24.5
            (
                gain,
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
            ) = transport.transport_at(anchor_x, lateral_um)
            phi = readout_weighting_potential(
                tcad_x_um, transport.x_low, transport.x_high
            )
            anchor_phi = readout_weighting_potential(
                anchor_x, transport.x_low, transport.x_high
            )
            primary_fc = edep_mev * FC_PER_MEV
            event_id = int(row["event_id"])

            for state in states:
                fluence = float(state["fluence_neq_cm-2"])
                acceptor = float(state["active_acceptor_fraction"])
                beta_e = float(state["beta_e_cm2_per_ns"])
                beta_h = float(state["beta_h_cm2_per_ns"])
                damaged_gain = math.exp(acceptor * math.log(max(gain, 1.0)))
                primary_response = (
                    (1.0 - phi) * induction_factor(electron_ps, beta_e, fluence)
                    + phi * induction_factor(hole_ps, beta_h, fluence)
                )
                avalanche_response = (
                    (1.0 - anchor_phi)
                    * induction_factor(anchor_electron_ps, beta_e, fluence)
                    + anchor_phi
                    * induction_factor(anchor_hole_ps, beta_h, fluence)
                )
                response = primary_response + (damaged_gain - 1.0) * avalanche_response
                event_charge[state["state"]][event_id] += primary_fc * response

    output = []
    for state in states:
        name = state["state"]
        values = np.array(list(event_charge[name].values()), dtype=float)
        output.append(
            {
                "temperature_K": temperature,
                "bias_V": bias,
                "anode_conduction_current_A": float(
                    operating.get("anode_conduction_current_A", "nan")
                ),
                "operating_regime": operating.get("operating_regime", "unclassified"),
                "state": name,
                "fluence_neq_cm-2": float(state["fluence_neq_cm-2"]),
                "active_acceptor_fraction": float(state["active_acceptor_fraction"]),
                "beta_e_cm2_per_ns": float(state["beta_e_cm2_per_ns"]),
                "beta_h_cm2_per_ns": float(state["beta_h_cm2_per_ns"]),
                "charge_MPV_fC": histogram_mpv(values),
                "charge_median_fC": float(np.median(values)),
                "charge_p16_fC": float(np.percentile(values, 16)),
                "charge_p84_fC": float(np.percentile(values, 84)),
                "events": int(values.size),
                "map": str(map_path),
            }
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maps-dir", type=Path, required=True)
    parser.add_argument("--step-hits", type=Path, required=True)
    parser.add_argument("--states", type=Path, default=DEFAULT_STATES)
    parser.add_argument("--operating-status", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    states = read_rows(args.states)
    operating_points: dict[tuple[float, float], dict[str, str]] = {}
    if args.operating_status:
        for row in read_rows(args.operating_status):
            operating_points[(float(row["temperature_K"]), float(row["bias_V"]))] = row
    map_paths = sorted(args.maps_dir.rglob("*_map.csv"))
    if not map_paths:
        raise FileNotFoundError(f"No V4.3 maps below {args.maps_dir}")
    rows = []
    for map_path in map_paths:
        rows.extend(process_map(map_path, args.step_hits, states, operating_points))
    rows.sort(
        key=lambda row: (
            float(row["temperature_K"]),
            str(row["state"]),
            float(row["bias_V"]),
        )
    )
    write_csv(args.output_dir / "v5_independent_response_surface.csv", rows)

    temperatures = sorted({float(row["temperature_K"]) for row in rows})
    fig, axes = plt.subplots(
        len(temperatures), 1,
        figsize=(9.5, 4.8 * len(temperatures)),
        squeeze=False,
        constrained_layout=True,
    )
    for axis, temperature in zip(axes[:, 0], temperatures):
        for state in states:
            selected = [
                row for row in rows
                if float(row["temperature_K"]) == temperature
                and row["state"] == state["state"]
                and row["operating_regime"] != "breakdown"
            ]
            selected.sort(key=lambda row: float(row["bias_V"]))
            axis.plot(
                [float(row["bias_V"]) for row in selected],
                [float(row["charge_MPV_fC"]) for row in selected],
                marker="o",
                label=state["state"],
            )
        axis.set_title(f"Independent n590 irradiation response — {temperature:g} K")
        axis.set_xlabel("Reverse bias magnitude [V]")
        axis.set_ylabel("Charge MPV [fC]")
        axis.grid(True, alpha=0.25)
        axis.legend(fontsize=8)
    fig.savefig(args.output_dir / "v5_charge_operating_envelope.png", dpi=180)
    plt.close(fig)

    lines = [
        "# V5 Independent Irradiated n590 Response",
        "",
        "No K1 absolute charge, coefficient, or fitting target is used.",
        "Damage-state values come only from the explicit configuration CSV.",
        "",
        "## Model boundary",
        "",
        "The operating field/alpha/mobility maps come from V4.3 TCAD.",
        "All points remain in the CSV, while breakdown points are excluded",
        "from the plotted operating envelope using the supplied current-based",
        "operating-status table.",
        "Irradiation is a response surface over explicit acceptor and trapping",
        "parameters. The gain transformation is phenomenological and does not",
        "replace a self-consistent irradiated TCAD solution.",
        "",
        "## Output",
        "",
        "- `v5_independent_response_surface.csv`",
        "- `v5_charge_operating_envelope.png`",
    ]
    (args.output_dir / "V5_INDEPENDENT_IRRADIATED_RESPONSE.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()

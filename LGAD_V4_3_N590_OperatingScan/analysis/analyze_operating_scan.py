#!/usr/bin/env python3
"""Analyze V4.3 TCAD operating maps with one common Geant4 MIP sample."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


PROJECT_DIR = Path(__file__).resolve().parents[1]
V41_DIR = PROJECT_DIR.parent / "LGAD_V4_1_PreIrradiationTransport"
sys.path.insert(0, str(V41_DIR / "analysis"))

from build_preirradiation_transport import (  # noqa: E402
    TransportMap,
    process_step_hits,
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maps-dir", type=Path, required=True)
    parser.add_argument("--step-hits", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    map_paths = sorted(args.maps_dir.rglob("*_map.csv"))
    if not map_paths:
        raise FileNotFoundError(f"No *_map.csv files below {args.maps_dir}")

    summaries: list[dict[str, float | int | str]] = []
    for map_path in map_paths:
        tcad_rows = read_rows(map_path)
        temperature = float(tcad_rows[0]["temperature_K"])
        bias = abs(float(tcad_rows[0]["bias_V"]))
        transport = TransportMap(
            tcad_rows, 1350.0, 480.0, 1.07e7, 8.37e6, tcad_rows, 1.0e3
        )
        _events, summary = process_step_hits(args.step_hits, transport)
        center = int(np.argmin(np.abs(transport.depths)))
        summaries.append(
            {
                "temperature_K": temperature,
                "bias_V": bias,
                "map": str(map_path),
                "max_field_V_per_cm": float(np.max(transport.e_field)),
                "max_eAlpha_cm-1": float(np.max(transport.e_alpha)),
                "max_hAlpha_cm-1": float(np.max(transport.h_alpha)),
                "center_full_electron_gain": float(transport.electron_gain[center, -1]),
                "primary_charge_MPV_fC": summary["primary_charge_fC_mpv_hist"],
                "full_collection_charge_MPV_fC": summary["preirradiation_full_collection_charge_fC_mpv_hist"],
                "full_collection_charge_median_fC": summary["preirradiation_full_collection_charge_fC_median"],
                "effective_multiplication_median": summary["effective_electron_multiplication_median"],
                "electron_active_drift_median_ps": summary["primary_charge_weighted_electron_active_drift_ps_median"],
                "hole_active_drift_median_ps": summary["primary_charge_weighted_hole_active_drift_ps_median"],
                "events": int(summary["events_with_edep"]),
            }
        )

    summaries.sort(key=lambda row: (float(row["temperature_K"]), float(row["bias_V"])))
    write_csv(args.output_dir / "v43_operating_scan_summary.csv", summaries)

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.4), constrained_layout=True)
    for temperature in sorted({float(row["temperature_K"]) for row in summaries}):
        selected = [row for row in summaries if float(row["temperature_K"]) == temperature]
        bias = [float(row["bias_V"]) for row in selected]
        label = f"{temperature:g} K"
        axes[0, 0].plot(bias, [float(row["max_field_V_per_cm"]) for row in selected], marker="o", label=label)
        axes[0, 1].plot(bias, [float(row["center_full_electron_gain"]) for row in selected], marker="o", label=label)
        axes[1, 0].plot(bias, [float(row["full_collection_charge_MPV_fC"]) for row in selected], marker="o", label=label)
        axes[1, 1].plot(bias, [float(row["electron_active_drift_median_ps"]) for row in selected], marker="o", label=f"electron {label}")
        axes[1, 1].plot(bias, [float(row["hole_active_drift_median_ps"]) for row in selected], marker="s", linestyle="--", label=f"hole {label}")

    axes[0, 0].set_ylabel("Maximum |E| [V/cm]")
    axes[0, 1].set_ylabel("Center electron gain")
    axes[1, 0].set_ylabel("Charge MPV [fC]")
    axes[1, 1].set_ylabel("Active drift median [ps]")
    for axis in axes.flat:
        axis.set_xlabel("Reverse bias magnitude [V]")
        axis.grid(True, alpha=0.25)
        axis.legend()
    fig.savefig(args.output_dir / "v43_operating_curves.png", dpi=180)
    plt.close(fig)

    lines = [
        "# V4.3 n590 Independent Operating Scan",
        "",
        "This scan uses only the preserved n590 device and one common Geant4",
        "MIP event sample. No K1 charge point or fit is used.",
        "",
        "| T [K] | Bias [V] | Max field [V/cm] | Gain | Charge MPV [fC] | e drift [ps] | h drift [ps] |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {float(row['temperature_K']):.0f} | {float(row['bias_V']):.0f} | "
            f"{float(row['max_field_V_per_cm']):.6g} | "
            f"{float(row['center_full_electron_gain']):.6g} | "
            f"{float(row['full_collection_charge_MPV_fC']):.6g} | "
            f"{float(row['electron_active_drift_median_ps']):.6g} | "
            f"{float(row['hole_active_drift_median_ps']):.6g} |"
        )
    (args.output_dir / "V4_3_OPERATING_SCAN.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()


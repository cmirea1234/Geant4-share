#!/usr/bin/env python3
"""Build the V4.1 pre-irradiation drift/collection baseline.

The TCAD avalanche coefficients determine multiplication.  The velocity
surrogate affects drift-time diagnostics only; it does not alter the
no-trapping integrated charge.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


PROJECT_DIR = Path(__file__).resolve().parents[1]
V4_DIR = PROJECT_DIR.parent / "LGAD_V4_TCADBiasFieldResponse"
sys.path.insert(0, str(V4_DIR / "analysis"))

from build_2d_mirrored_gain_response import (  # noqa: E402
    FC_PER_MEV,
    MAP_PATH,
    MirroredGainMap,
    fold_to_window,
    read_rows,
    summarize,
    write_csv,
)


DEFAULT_OUTPUT_DIR = PROJECT_DIR / "outputs/data/preirradiation_transport"
DEFAULT_TRANSPORT_MAP = (
    PROJECT_DIR / "inputs/tcad_n590_590V/n590_tcad_silicon_transport_590V.csv"
)
TEMPERATURE_K = 300.0

# Configurable timing surrogate. These values do not claim to reproduce the
# full proprietary/default Sentaurus mobility parameter set.
DEFAULT_E_MOBILITY_CM2_VS = 1350.0
DEFAULT_H_MOBILITY_CM2_VS = 480.0
DEFAULT_E_SATURATION_CM_S = 1.07e7
DEFAULT_H_SATURATION_CM_S = 8.37e6


def saturated_velocity_cm_s(
    field_v_cm: np.ndarray,
    mobility_cm2_vs: float,
    saturation_cm_s: float,
) -> np.ndarray:
    """Smooth low-field mobility to high-field saturation surrogate."""
    low_field_velocity = mobility_cm2_vs * np.maximum(field_v_cm, 0.0)
    return low_field_velocity / (1.0 + low_field_velocity / saturation_cm_s)


def cumulative_time_ps(x_um: np.ndarray, velocity_cm_s: np.ndarray) -> np.ndarray:
    """Integrate travel time from the first x point to each point."""
    inverse_velocity = 1.0 / np.maximum(velocity_cm_s, 1.0)
    result_s = np.zeros_like(x_um)
    x_cm = x_um * 1.0e-4
    for index in range(1, len(x_um)):
        dx_cm = abs(x_cm[index] - x_cm[index - 1])
        result_s[index] = result_s[index - 1] + 0.5 * (
            inverse_velocity[index] + inverse_velocity[index - 1]
        ) * dx_cm
    return result_s * 1.0e12


class TransportMap(MirroredGainMap):
    def __init__(
        self,
        rows: list[dict[str, str]],
        electron_mobility_cm2_vs: float,
        hole_mobility_cm2_vs: float,
        electron_saturation_cm_s: float,
        hole_saturation_cm_s: float,
        tcad_transport_rows: list[dict[str, str]] | None = None,
        active_field_threshold_v_cm: float = 1.0e3,
    ) -> None:
        super().__init__(rows)
        self.electron_drift_ps = np.zeros_like(self.e_field)
        self.hole_drift_ps = np.zeros_like(self.e_field)
        self.electron_full_contact_drift_ps = np.zeros_like(self.e_field)
        self.hole_full_contact_drift_ps = np.zeros_like(self.e_field)
        self.electron_velocity_cm_s = np.zeros_like(self.e_field)
        self.hole_velocity_cm_s = np.zeros_like(self.e_field)

        self.velocity_model = "constant_mobility_smooth_saturation_surrogate"
        tcad_mobility = None
        if tcad_transport_rows is not None:
            tcad_mobility = self._build_tcad_mobility_grids(tcad_transport_rows)
            self.velocity_model = "tcad_effective_mobility_times_electric_field"

        for depth_index in range(len(self.depths)):
            if tcad_mobility is None:
                e_velocity = saturated_velocity_cm_s(
                    self.e_field[depth_index],
                    electron_mobility_cm2_vs,
                    electron_saturation_cm_s,
                )
                h_velocity = saturated_velocity_cm_s(
                    self.e_field[depth_index],
                    hole_mobility_cm2_vs,
                    hole_saturation_cm_s,
                )
            else:
                e_mobility, h_mobility = tcad_mobility
                # The exported mobility contains the configured doping,
                # high-field, and Lombardi model response. The exported DC
                # velocity is not used because it also reflects the solved
                # quasi-Fermi/current state rather than a test-charge path.
                e_velocity = e_mobility[depth_index] * self.e_field[depth_index]
                h_velocity = h_mobility[depth_index] * self.e_field[depth_index]
            e_from_cathode = cumulative_time_ps(self.x_um, e_velocity)
            h_from_cathode = cumulative_time_ps(self.x_um, h_velocity)
            self.electron_velocity_cm_s[depth_index] = e_velocity
            self.hole_velocity_cm_s[depth_index] = h_velocity
            # Full-contact paths include neutral, heavily doped contact regions.
            self.electron_full_contact_drift_ps[depth_index] = e_from_cathode
            self.hole_full_contact_drift_ps[depth_index] = (
                h_from_cathode[-1] - h_from_cathode
            )

            # Trapping-relevant active paths stop when the carrier exits the
            # depleted/high-field region. Full-contact times remain diagnostic.
            active = np.flatnonzero(
                self.e_field[depth_index] >= active_field_threshold_v_cm
            )
            if active.size == 0:
                low_active, high_active = 0, len(self.x_um) - 1
            else:
                low_active, high_active = int(active[0]), int(active[-1])
            self.electron_drift_ps[depth_index] = np.maximum(
                e_from_cathode - e_from_cathode[low_active], 0.0
            )
            self.hole_drift_ps[depth_index] = np.maximum(
                h_from_cathode[high_active] - h_from_cathode, 0.0
            )
        self.active_field_threshold_v_cm = active_field_threshold_v_cm

    def _build_tcad_mobility_grids(
        self, rows: list[dict[str, str]]
    ) -> tuple[np.ndarray, np.ndarray]:
        by_coordinate = {
            (float(row["depth_um"]), float(row["x_um"])): row for row in rows
        }
        e_mobility = np.zeros_like(self.e_field)
        h_mobility = np.zeros_like(self.e_field)
        for depth_index, depth_um in enumerate(self.depths):
            for x_index, x_um in enumerate(self.x_um):
                key = (float(depth_um), float(x_um))
                if key not in by_coordinate:
                    raise RuntimeError(f"TCAD transport coordinate missing: {key}")
                row = by_coordinate[key]
                e_mobility[depth_index, x_index] = float(
                    row["eMobility_cm2_per_Vs"]
                )
                h_mobility[depth_index, x_index] = float(
                    row["hMobility_cm2_per_Vs"]
                )
        return e_mobility, h_mobility

    def _interpolate_grid(self, grid: np.ndarray, tcad_x_um: float, lateral_um: float) -> float:
        x = float(np.clip(tcad_x_um, self.x_low, self.x_high))
        depth = fold_to_window(lateral_um, self.depth_low, self.depth_high)
        if depth <= self.depths[0]:
            low_index = high_index = 0
            weight = 0.0
        elif depth >= self.depths[-1]:
            low_index = high_index = len(self.depths) - 1
            weight = 0.0
        else:
            high_index = int(np.searchsorted(self.depths, depth))
            low_index = high_index - 1
            weight = float(
                (depth - self.depths[low_index])
                / (self.depths[high_index] - self.depths[low_index])
            )
        low_value = float(np.interp(x, self.x_um, grid[low_index]))
        high_value = float(np.interp(x, self.x_um, grid[high_index]))
        return (1.0 - weight) * low_value + weight * high_value

    def transport_at(
        self, tcad_x_um: float, lateral_um: float
    ) -> tuple[float, float, float, float, float, float, float, float]:
        ge, gh, field, folded_depth = self.interpolate(tcad_x_um, lateral_um)
        return (
            ge,
            gh,
            field,
            folded_depth,
            self._interpolate_grid(self.electron_drift_ps, tcad_x_um, lateral_um),
            self._interpolate_grid(self.hole_drift_ps, tcad_x_um, lateral_um),
            self._interpolate_grid(
                self.electron_full_contact_drift_ps, tcad_x_um, lateral_um
            ),
            self._interpolate_grid(
                self.hole_full_contact_drift_ps, tcad_x_um, lateral_um
            ),
        )


def readout_weighting_potential(tcad_x_um: float, x_low: float, x_high: float) -> float:
    """Parallel-plate diagnostic: cathode/readout=1, anode=0."""
    return float(np.clip((x_high - tcad_x_um) / (x_high - x_low), 0.0, 1.0))


def process_step_hits(
    step_path: Path,
    transport: TransportMap,
) -> tuple[list[dict[str, float | int]], dict[str, float]]:
    accumulators: dict[str, defaultdict[int, float]] = {
        name: defaultdict(float)
        for name in (
            "primary",
            "multiplied",
            "electron_primary_induced",
            "hole_primary_induced",
            "gain_weighted_e_drift",
            "primary_weighted_e_drift",
            "primary_weighted_h_drift",
            "primary_weighted_e_full_contact_drift",
            "primary_weighted_h_full_contact_drift",
            "weight",
            "max_e_drift",
            "max_h_drift",
        )
    }
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

            g4_x_um = 0.5 * (float(row["pre_x_um"]) + float(row["post_x_um"]))
            g4_z_um = 0.5 * (float(row["pre_z_um"]) + float(row["post_z_um"]))
            tcad_x_um = -g4_z_um - 24.5
            (
                ge,
                _gh,
                _field,
                _folded,
                e_drift_ps,
                h_drift_ps,
                e_full_contact_ps,
                h_full_contact_ps,
            ) = transport.transport_at(tcad_x_um, g4_x_um)
            phi = readout_weighting_potential(
                tcad_x_um, transport.x_low, transport.x_high
            )
            primary_fc = edep_mev * FC_PER_MEV
            event_id = int(row["event_id"])

            accumulators["primary"][event_id] += primary_fc
            accumulators["multiplied"][event_id] += primary_fc * ge
            accumulators["electron_primary_induced"][event_id] += primary_fc * (1.0 - phi)
            accumulators["hole_primary_induced"][event_id] += primary_fc * phi
            accumulators["gain_weighted_e_drift"][event_id] += primary_fc * ge * e_drift_ps
            accumulators["primary_weighted_e_drift"][event_id] += primary_fc * e_drift_ps
            accumulators["primary_weighted_h_drift"][event_id] += primary_fc * h_drift_ps
            accumulators["primary_weighted_e_full_contact_drift"][event_id] += (
                primary_fc * e_full_contact_ps
            )
            accumulators["primary_weighted_h_full_contact_drift"][event_id] += (
                primary_fc * h_full_contact_ps
            )
            accumulators["weight"][event_id] += primary_fc
            accumulators["max_e_drift"][event_id] = max(
                accumulators["max_e_drift"][event_id], e_drift_ps
            )
            accumulators["max_h_drift"][event_id] = max(
                accumulators["max_h_drift"][event_id], h_drift_ps
            )
            used_steps += 1

    rows: list[dict[str, float | int]] = []
    for event_id in sorted(accumulators["primary"]):
        primary = accumulators["primary"][event_id]
        multiplied = accumulators["multiplied"][event_id]
        rows.append(
            {
                "event_id": event_id,
                "primary_charge_fC": primary,
                "preirradiation_full_collection_charge_fC": multiplied,
                "effective_electron_multiplication": multiplied / primary if primary else 0.0,
                "primary_electron_induced_charge_fC": accumulators["electron_primary_induced"][event_id],
                "primary_hole_induced_charge_fC": accumulators["hole_primary_induced"][event_id],
                "primary_charge_weighted_electron_active_drift_ps": accumulators["primary_weighted_e_drift"][event_id] / primary if primary else 0.0,
                "primary_charge_weighted_hole_active_drift_ps": accumulators["primary_weighted_h_drift"][event_id] / primary if primary else 0.0,
                "gain_charge_weighted_electron_active_drift_ps": accumulators["gain_weighted_e_drift"][event_id] / multiplied if multiplied else 0.0,
                "primary_charge_weighted_electron_full_contact_drift_ps": accumulators["primary_weighted_e_full_contact_drift"][event_id] / primary if primary else 0.0,
                "primary_charge_weighted_hole_full_contact_drift_ps": accumulators["primary_weighted_h_full_contact_drift"][event_id] / primary if primary else 0.0,
                "max_electron_drift_ps": accumulators["max_e_drift"][event_id],
                "max_hole_drift_ps": accumulators["max_h_drift"][event_id],
            }
        )

    summary: dict[str, float] = {
        "input_step_rows": float(step_count),
        "used_edep_steps": float(used_steps),
        "events_with_edep": float(len(rows)),
    }
    keys = [key for key in rows[0] if key != "event_id"] if rows else []
    for key in keys:
        summary.update(summarize(np.array([row[key] for row in rows]), key))
    return rows, summary


def write_transport_map(output_dir: Path, transport: TransportMap) -> None:
    rows: list[dict[str, float]] = []
    for depth_index, depth_um in enumerate(transport.depths):
        for x_index, x_um in enumerate(transport.x_um):
            rows.append(
                {
                    "tcad_x_um": float(x_um),
                    "tcad_lateral_um": float(depth_um),
                    "electric_field_V_per_cm": float(transport.e_field[depth_index, x_index]),
                    "electron_velocity_cm_per_s": float(transport.electron_velocity_cm_s[depth_index, x_index]),
                    "hole_velocity_cm_per_s": float(transport.hole_velocity_cm_s[depth_index, x_index]),
                    "electron_active_drift_ps": float(transport.electron_drift_ps[depth_index, x_index]),
                    "hole_active_drift_ps": float(transport.hole_drift_ps[depth_index, x_index]),
                    "electron_full_contact_drift_ps": float(transport.electron_full_contact_drift_ps[depth_index, x_index]),
                    "hole_full_contact_drift_ps": float(transport.hole_full_contact_drift_ps[depth_index, x_index]),
                    "electron_multiplication_to_cathode": float(transport.electron_gain[depth_index, x_index]),
                    "hole_multiplication_to_anode": float(transport.hole_gain[depth_index, x_index]),
                }
            )
    write_csv(output_dir / "preirradiation_transport_map.csv", rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step-hits", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--transport-map", type=Path, default=DEFAULT_TRANSPORT_MAP
    )
    parser.add_argument(
        "--use-surrogate-velocity",
        action="store_true",
        help="ignore the TCAD mobility map and use the configurable surrogate",
    )
    parser.add_argument("--electron-mobility-cm2-vs", type=float, default=DEFAULT_E_MOBILITY_CM2_VS)
    parser.add_argument("--hole-mobility-cm2-vs", type=float, default=DEFAULT_H_MOBILITY_CM2_VS)
    parser.add_argument("--electron-saturation-cm-s", type=float, default=DEFAULT_E_SATURATION_CM_S)
    parser.add_argument("--hole-saturation-cm-s", type=float, default=DEFAULT_H_SATURATION_CM_S)
    parser.add_argument(
        "--active-field-threshold-v-cm", type=float, default=1.0e3
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tcad_transport_rows = None
    if not args.use_surrogate_velocity:
        if not args.transport_map.exists():
            raise FileNotFoundError(
                f"TCAD transport map not found: {args.transport_map}"
            )
        tcad_transport_rows = read_rows(args.transport_map)

    transport = TransportMap(
        read_rows(MAP_PATH),
        args.electron_mobility_cm2_vs,
        args.hole_mobility_cm2_vs,
        args.electron_saturation_cm_s,
        args.hole_saturation_cm_s,
        tcad_transport_rows,
        args.active_field_threshold_v_cm,
    )
    write_transport_map(args.output_dir, transport)
    rows, summary = process_step_hits(args.step_hits, transport)
    if not rows:
        raise RuntimeError("No positive energy-deposition steps were found")
    write_csv(args.output_dir / "preirradiation_transport_events.csv", rows)

    metadata = {
        "tcad_temperature_K": TEMPERATURE_K,
        "tcad_anode_bias_V": -590.0,
        "tcad_cathode_bias_V": 0.0,
        "tcad_avalanche_model": "Okuto",
        "radiation_state": "treated_as_preirradiation_no_traps_in_evidence",
        "velocity_model": transport.velocity_model,
        "electron_mobility_cm2_Vs": args.electron_mobility_cm2_vs,
        "hole_mobility_cm2_Vs": args.hole_mobility_cm2_vs,
        "electron_saturation_velocity_cm_s": args.electron_saturation_cm_s,
        "hole_saturation_velocity_cm_s": args.hole_saturation_cm_s,
        "weighting_model": "linear_parallel_plate_diagnostic",
        "charge_model": "no_trapping_full_collection_q_times_electron_multiplication",
        "active_field_threshold_V_per_cm": args.active_field_threshold_v_cm,
    }
    summary_rows = [
        {"quantity": key, "value": value, "note": str(args.step_hits)}
        for key, value in summary.items()
    ] + [
        {"quantity": key, "value": value, "note": "V4.1 model configuration"}
        for key, value in metadata.items()
    ]
    write_csv(args.output_dir / "preirradiation_transport_summary.csv", summary_rows)

    primary = np.array([row["primary_charge_fC"] for row in rows])
    charge = np.array([row["preirradiation_full_collection_charge_fC"] for row in rows])
    e_time = np.array([row["primary_charge_weighted_electron_active_drift_ps"] for row in rows])
    h_time = np.array([row["primary_charge_weighted_hole_active_drift_ps"] for row in rows])

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    charge_upper = max(float(np.percentile(charge, 99.0)), 1.0)
    axes[0].hist(primary, bins=np.linspace(0.0, charge_upper, 90), histtype="step", label="primary")
    axes[0].hist(charge, bins=np.linspace(0.0, charge_upper, 90), histtype="step", label="pre-irradiation full collection")
    axes[0].set_xlabel("Integrated charge [fC]")
    axes[0].set_ylabel("Events")
    axes[0].set_title("V4.1 300 K, 590 V baseline")
    axes[0].legend()
    axes[0].grid(True, alpha=0.25)
    axes[1].hist(e_time, bins=80, histtype="step", label="electron")
    axes[1].hist(h_time, bins=80, histtype="step", label="hole")
    axes[1].set_xlabel("Charge-weighted drift time [ps]")
    axes[1].set_ylabel("Events")
    axes[1].set_title("Active-region drift diagnostic")
    axes[1].legend()
    axes[1].grid(True, alpha=0.25)
    fig.savefig(args.output_dir / "preirradiation_charge_and_drift.png", dpi=180)
    plt.close(fig)

    report = "\n".join(
        [
            "# V4.1 Pre-Irradiation Transport Result",
            "",
            "## Provenance",
            "",
            "- TCAD state: treated as pre-irradiation",
            "- TCAD temperature: `300 K`",
            "- electrodes: anode `-590 V`, cathode `0 V`",
            "- TCAD avalanche model: `Okuto`",
            "- radiation traps/defects: not found in the supplied evidence",
            "",
            "## Result",
            "",
            f"- events with energy deposition: `{int(summary['events_with_edep']):,}`",
            f"- primary-charge MPV: `{summary['primary_charge_fC_mpv_hist']:.6g} fC`",
            f"- pre-irradiation full-collection MPV: `{summary['preirradiation_full_collection_charge_fC_mpv_hist']:.6g} fC`",
            f"- pre-irradiation full-collection median: `{summary['preirradiation_full_collection_charge_fC_median']:.6g} fC`",
            f"- effective multiplication median: `{summary['effective_electron_multiplication_median']:.6g}`",
            f"- electron active-region drift median: `{summary['primary_charge_weighted_electron_active_drift_ps_median']:.6g} ps`",
            f"- hole active-region drift median: `{summary['primary_charge_weighted_hole_active_drift_ps_median']:.6g} ps`",
            f"- electron full-contact drift median: `{summary['primary_charge_weighted_electron_full_contact_drift_ps_median']:.6g} ps`",
            f"- hole full-contact drift median: `{summary['primary_charge_weighted_hole_full_contact_drift_ps_median']:.6g} ps`",
            "",
            "## Interpretation boundary",
            "",
            "The integrated charge is a pre-irradiation, no-trapping baseline.",
            "The drift times use exported TCAD effective mobility multiplied",
            "by local electric-field magnitude. Exported DC carrier velocity",
            "is not used because it includes quasi-Fermi/current equilibrium.",
            "Active-region times stop at |E| >= 1 kV/cm boundaries; physical",
            "metal-contact times additionally include neutral implant regions.",
            "This result is not a validation against the irradiated K1 EoL",
            "measurement, which was taken near 253 K rather than 300 K.",
            "",
        ]
    )
    (args.output_dir / "V4_1_PREIRRADIATION_TRANSPORT.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
